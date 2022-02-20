# fastapi-ivanova-clothes

Neste repositório temos a criação de bancos de dados, uma forma de validação de dados por meio do Pydantic e autenticação e autorização por meio do pyjwt.

## Criando o ambiente virtual

> python -m venv ./venv

Ativando:

> source ./venv/bin/activate

## Instalando as dependências

> pip install fastapi uvicorn sqlalchemy databases asyncpg psycopg2 psycopg2-binary alembic config pydantic
> pip install email-validator passlib[bcrypt] pyjwt

ou

> pip install -r requirements.txt


## Levantando os containers

> docker-compose up

## Variáveis de ambiente

Acesse o arquivo .env e configure conforme as suas necessidades.
Para descobrir o IP de um container basta digitar:

> docker inspect id_container | grep IPAddress


# Criando o banco de dados

> alembic init migrations
> alembic revision --autogenerate -m "Initial"
> alembic upgrade head

## Rodando o servidor (UVICORN)

> python -m uvicorn main:app --reload

## Interface Swagger / OpenAPI

> localhost:8000/docs
