-- Migracoes incrementais. Idempotente.

-- Campos extras no animal
ALTER TABLE animal ADD COLUMN IF NOT EXISTS telefone     VARCHAR(30);
ALTER TABLE animal ADD COLUMN IF NOT EXISTS idade        VARCHAR(40);
ALTER TABLE animal ADD COLUMN IF NOT EXISTS peso         VARCHAR(40);
ALTER TABLE animal ADD COLUMN IF NOT EXISTS motivo       VARCHAR(255);
ALTER TABLE animal ADD COLUMN IF NOT EXISTS diagnostico  TEXT;
ALTER TABLE animal ADD COLUMN IF NOT EXISTS medicamentos TEXT;
ALTER TABLE animal ADD COLUMN IF NOT EXISTS alergias     VARCHAR(255);
ALTER TABLE animal ADD COLUMN IF NOT EXISTS veterinario  VARCHAR(120);

-- Clinica (cada clinica tem suas baias e usuarios)
CREATE TABLE IF NOT EXISTS clinica (
    id_clinica   SERIAL PRIMARY KEY,
    nome         VARCHAR(120) NOT NULL,
    qtd_baias    INT NOT NULL DEFAULT 6
);

ALTER TABLE usuario ADD COLUMN IF NOT EXISTS id_clinica INT;
ALTER TABLE baia ADD COLUMN IF NOT EXISTS id_clinica INT;

-- Clinica padrao para dados que ja existem
INSERT INTO clinica (id_clinica, nome, qtd_baias)
VALUES (1, 'Clinica Padrao', 6)
ON CONFLICT (id_clinica) DO NOTHING;

SELECT setval(pg_get_serial_sequence('clinica', 'id_clinica'),
              GREATEST((SELECT COALESCE(MAX(id_clinica), 1) FROM clinica), 1));

UPDATE usuario SET id_clinica = 1 WHERE id_clinica IS NULL;
UPDATE baia SET id_clinica = 1 WHERE id_clinica IS NULL;

-- Numero da baia e unico por clinica (nao global)
ALTER TABLE baia DROP CONSTRAINT IF EXISTS baia_numero_key;
CREATE UNIQUE INDEX IF NOT EXISTS idx_baia_clinica_numero ON baia(id_clinica, numero);

ALTER TABLE usuario DROP CONSTRAINT IF EXISTS fk_usuario_clinica;
ALTER TABLE usuario
    ADD CONSTRAINT fk_usuario_clinica
    FOREIGN KEY (id_clinica) REFERENCES clinica(id_clinica);

ALTER TABLE baia DROP CONSTRAINT IF EXISTS fk_baia_clinica;
ALTER TABLE baia
    ADD CONSTRAINT fk_baia_clinica
    FOREIGN KEY (id_clinica) REFERENCES clinica(id_clinica);
