import sqlite3
import json
from pathlib import Path


def init_db():
    file_name = r"database.db"
    file_obj = Path(file_name)
    if file_obj.is_file():
        return False
    else:
        connection = sqlite3.connect('database.db')
        with open('schema.sql') as f:
            connection.executescript(f.read())
        connection.close()
        return True


def get_json_cmd(data):
    cmd = json.loads(data)
    return cmd["cmd"]


def sqlite_set(message):
    cmd = json.loads(message)
    connection = sqlite3.connect('database.db')
    cur = connection.cursor()
    cur.execute("INSERT INTO cadastros (titulo, nome, sobrenome, telefone, email, endereco, cidade, cep, texto) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (cmd["titulo"], cmd["nome"], cmd["sobrenome"], cmd["telefone"], cmd["email"], cmd["endereco"],
                 cmd["cidade"], cmd["cep"], cmd["texto"])
                )
    connection.commit()
    connection.close()


def sqlite_update(message):
    cmd = json.loads(message)
    connection = sqlite3.connect('database.db')
    cur = connection.cursor()
    cur.execute("update cadastros set titulo =\"" + cmd["titulo"] + "\", nome =\"" + cmd["nome"] + "\", sobrenome =\""
                "" + cmd["sobrenome"] + "\", telefone =\"" + cmd["telefone"] + "\", email =\"" + cmd["email"] + "\""
                ", endereco =\"" + cmd["endereco"] + "\", cidade =\"" + cmd["cidade"] + "\", cep =\""
                "" + cmd["cep"] + "\", texto =\"" + cmd["texto"] + "\" where ID =\"" + cmd["ID"] + "\";")
    connection.commit()
    connection.close()


def sqlite_del(message):
    cmd = json.loads(message)
    connection = sqlite3.connect('database.db')
    cur = connection.cursor()
    cur.execute("DELETE FROM cadastros WHERE ID = " + cmd["ID"])
    connection.commit()
    connection.close()


def sqlite_get(message):
    cmd = json.loads(message)
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    cur = connection.cursor()
    rows = cur.execute("SELECT * FROM cadastros WHERE " + cmd["coluna"] + ' = ' + "\"" + cmd["dados"] + "\"").fetchall()
    connection.close()
    r = json.dumps([dict(ix) for ix in rows], ensure_ascii=False)
    return "{ \"cmd\": \"" + cmd["cmd"] + "\"" + ", \"resp\":" + r + " }"


def sqlite_get_all(message):
    cmd = json.loads(message)
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    cur = connection.cursor()
    count = cur.execute("SELECT COUNT(*) FROM cadastros;").fetchone()[0]
    rows = cur.execute("SELECT * FROM cadastros order by \"name\"").fetchall()
    connection.close()
    r = json.dumps([dict(ix) for ix in rows], ensure_ascii=False)
    return "{ \"cmd\": \"" + cmd["cmd"] + "\"" + ", \"count\": " + str(count) + ", " + "\"resp\":" + r + " }"


def sqlite_get_estatisticas(message):
    cmd = json.loads(message)
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    cur = connection.cursor()
    count = cur.execute("SELECT COUNT(*) FROM (select cidade, count(cidade) as cidades_count, "
                        "count(cidade)*100.0 / (select count(*) from cadastros) as cidades_percent "
                        "from cadastros group by cidade order by 3 desc);").fetchone()[0]
    rows = cur.execute("select cidade, count(cidade) as cidades_count, "
                       "round((count(cidade)*100.0 / (select count(*) from cadastros)),2) "
                       "as cidades_percent from cadastros group by cidade order by 3 desc;").fetchall()
    connection.close()
    r = json.dumps([dict(ix) for ix in rows], ensure_ascii=False)
    return "{ \"cmd\": \"" + cmd["cmd"] + "\"" + ", \"count\": " + str(count) + ", " + "\"resp\":" + r + " }"

