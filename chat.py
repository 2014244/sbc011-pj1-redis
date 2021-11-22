# -*- coding: utf-8 -*-

"""
Chat Server
===========

This simple application uses WebSockets to run a primitive chat server.
"""

import os
import logging
import redis
import gevent
from flask import Flask, render_template
from flask_sockets import Sockets
from sqlite_json import sqlite_set, sqlite_get, sqlite_get_all, get_json_cmd, sqlite_del, \
    sqlite_get_estatisticas, sqlite_update, init_db

REDIS_URL = os.environ['REDIS_URL']
REDIS_CHAN = 'chat'
SET_CAD = 'salvaCadastro'
GET_CAD = 'leCadastro'
GET_ALL = 'leTodoCadastro'
DEL_CAD = 'deleteCadastro'
GET_EST = 'leEstatisticas'
SET_UPD = 'updateCadastro'
PING = 'ping'

app = Flask(__name__)
app.debug = 'DEBUG' in os.environ

sockets = Sockets(app)
redis = redis.from_url(REDIS_URL)


class ChatBackend(object):
    """Interface for registering and updating WebSocket clients."""

    def __init__(self):
        self.clients = list()
        self.pubsub = redis.pubsub()
        self.pubsub.subscribe(REDIS_CHAN)
        if init_db():
            app.logger.info(u'DB EXISTS')
        else:
            app.logger.info(u'DB CREATED')

    def __iter_data(self):
        for message in self.pubsub.listen():
            data = message.get('data')
            if message['type'] == 'message':
                app.logger.info(u'Sending message: {}'.format(data))
                yield data

    def register(self, client):
        """Register a WebSocket connection for Redis updates."""
        self.clients.append(client)

    def send(self, client, data):
        """Send given data to the registered client.
        Automatically discards invalid connections."""
        try:
            client.send(data)
        except Exception:
            self.clients.remove(client)

    def run(self):
        """Listens for new messages in Redis, and sends them to clients."""
        for data in self.__iter_data():
            for client in self.clients:
                gevent.spawn(self.send, client, data)

    def start(self):
        """Maintains Redis subscription in the background."""
        gevent.spawn(self.run)


chats = ChatBackend()
chats.start()


@app.route('/')
def hello():
    return render_template('index.html')


@sockets.route('/submit')
def inbox(ws):
    """Receives incoming chat messages, inserts them into Redis."""
    while not ws.closed:
        # Sleep to prevent *constant* context-switches.
        gevent.sleep(0.1)
        message = ws.receive()

        if message:
            app.logger.info(u'Inserting message: {}'.format(message))
            if get_json_cmd(message) == REDIS_CHAN:
                redis.publish(REDIS_CHAN, message)
            elif get_json_cmd(message) == SET_CAD:
                sqlite_set(message)
            elif get_json_cmd(message) == GET_CAD:
                chats.send(ws, sqlite_get(message))
            elif get_json_cmd(message) == GET_ALL:
                chats.send(ws, sqlite_get_all(message))
            elif get_json_cmd(message) == DEL_CAD:
                sqlite_del(message)
            elif get_json_cmd(message) == GET_EST:
                chats.send(ws, sqlite_get_estatisticas(message))
            elif get_json_cmd(message) == SET_UPD:
                sqlite_update(message)
            elif get_json_cmd(message) == PING:
                chats.send(ws, '{ "cmd": "ping" }')


@sockets.route('/receive')
def outbox(ws):
    """Sends outgoing chat messages, via `ChatBackend`."""
    chats.register(ws)

    while not ws.closed:
        # Context switch while `ChatBackend.start` is running in the background.
        gevent.sleep(0.1)



