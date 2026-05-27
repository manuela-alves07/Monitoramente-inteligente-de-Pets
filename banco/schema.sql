-- Esquema do banco (PostgreSQL). Rode em monitoramento_pets (local ou Neon).

CREATE TABLE usuario (
    id_usuario       SERIAL PRIMARY KEY,
    nome             VARCHAR(120) NOT NULL,
    email            VARCHAR(150) NOT NULL UNIQUE,
    senha_hash       VARCHAR(255) NOT NULL,
    perfil           VARCHAR(50) NOT NULL
);

CREATE TABLE log_acesso (
    id_log           SERIAL PRIMARY KEY,
    id_usuario       INT NOT NULL,
    acao             VARCHAR(120) NOT NULL,
    endpoint         VARCHAR(255),
    data_hora        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_log_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario)
        ON DELETE CASCADE
);

CREATE TABLE baia (
    id_baia          SERIAL PRIMARY KEY,
    numero           VARCHAR(20) NOT NULL UNIQUE,
    localizacao      VARCHAR(120),
    status           VARCHAR(30) NOT NULL
);

CREATE TABLE camera (
    id_camera        SERIAL PRIMARY KEY,
    id_baia          INT NOT NULL,
    ip_stream        VARCHAR(255) NOT NULL,
    status           VARCHAR(30) NOT NULL,
    ultima_conexao   TIMESTAMP,
    CONSTRAINT fk_camera_baia
        FOREIGN KEY (id_baia)
        REFERENCES baia(id_baia)
        ON DELETE CASCADE
);

CREATE TABLE animal (
    id_animal            SERIAL PRIMARY KEY,
    nome                 VARCHAR(100),
    especie              VARCHAR(80) NOT NULL,
    raca                 VARCHAR(80),
    data_nascimento      DATE,
    tutor                VARCHAR(120),
    status_internacao    VARCHAR(50) NOT NULL,
    data_entrada         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    id_baia              INT NOT NULL,
    CONSTRAINT fk_animal_baia
        FOREIGN KEY (id_baia)
        REFERENCES baia(id_baia)
        ON DELETE RESTRICT
);

CREATE TABLE evento (
    id_evento        SERIAL PRIMARY KEY,
    id_animal        INT NOT NULL,
    origem_camera    INT,
    tipo_evento      VARCHAR(100) NOT NULL,
    confianca_ia     DECIMAL(5,2),
    data_hora        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_evento_animal
        FOREIGN KEY (id_animal)
        REFERENCES animal(id_animal)
        ON DELETE CASCADE,
    CONSTRAINT fk_evento_camera
        FOREIGN KEY (origem_camera)
        REFERENCES camera(id_camera)
        ON DELETE SET NULL,
    CONSTRAINT chk_confianca
        CHECK (confianca_ia IS NULL OR (confianca_ia >= 0 AND confianca_ia <= 100))
);

CREATE TABLE alerta (
    id_alerta        SERIAL PRIMARY KEY,
    id_animal        INT NOT NULL,
    tipo_alerta      VARCHAR(100) NOT NULL,
    descricao        TEXT,
    status           VARCHAR(30) NOT NULL,
    criado_em        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolvido_em     TIMESTAMP,
    CONSTRAINT fk_alerta_animal
        FOREIGN KEY (id_animal)
        REFERENCES animal(id_animal)
        ON DELETE CASCADE
);

CREATE INDEX idx_log_usuario ON log_acesso(id_usuario);
CREATE INDEX idx_camera_baia ON camera(id_baia);
CREATE INDEX idx_animal_baia ON animal(id_baia);
CREATE INDEX idx_evento_animal ON evento(id_animal);
CREATE INDEX idx_evento_camera ON evento(origem_camera);
CREATE INDEX idx_alerta_animal ON alerta(id_animal);
CREATE INDEX idx_evento_data ON evento(data_hora);
CREATE INDEX idx_alerta_status ON alerta(status);
