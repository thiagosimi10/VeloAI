#!/bin/sh
# Executado automaticamente pela imagem oficial do Postgres na primeira inicialização
# do volume de dados (/docker-entrypoint-initdb.d/). Cria a role `veloai_app`, usada
# exclusivamente pelo Backend para conectar ao Banco Master e aos bancos de tenant —
# nunca a role administrativa (`veloai_admin`), conforme 18-DATABASE-02 e
# 29-SECURITY.md ("Nunca utilizar usuário postgres na aplicação").
set -e

: "${POSTGRES_APP_USER:?POSTGRES_APP_USER não definido}"
: "${POSTGRES_APP_PASSWORD:?POSTGRES_APP_PASSWORD não definido}"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    DO \$do\$
    BEGIN
        IF NOT EXISTS (
            SELECT FROM pg_catalog.pg_roles WHERE rolname = '${POSTGRES_APP_USER}'
        ) THEN
            CREATE ROLE "${POSTGRES_APP_USER}" LOGIN PASSWORD '${POSTGRES_APP_PASSWORD}'
                NOCREATEDB NOCREATEROLE NOSUPERUSER;
        END IF;
    END
    \$do\$;
EOSQL
