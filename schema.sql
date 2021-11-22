DROP TABLE IF EXISTS cadastros;

CREATE TABLE cadastros (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    titulo TEXT,
    nome TEXT NOT NULL,
    sobrenome TEXT NOT NULL,
    telefone TEXT,
    email TEXT NOT NULL,
    endereco TEXT,
    cidade TEXT,
    cep TEXT,
    texto
);
