import databases
import enum
import sqlalchemy
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.config import Config
from starlette.requests import Request
from pydantic import BaseModel, validator
from email_validator import validate_email, EmailNotValidError
from typing import Optional # typing é um pacote padrão do python (não precisa instalar).
from datetime import datetime
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
import enum


config = Config('.env')
DATABASE_URL = config('DATABASE_URL')
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()


# Classe para autorização
class UserRole(enum.Enum):
    super_admin = "super admin"
    admin = "admin"
    user = "user"


users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("email", sqlalchemy.String(120), unique=True),
    sqlalchemy.Column("password", sqlalchemy.String(255)),
    sqlalchemy.Column("full_name", sqlalchemy.String(200)),
    sqlalchemy.Column("phone", sqlalchemy.String(13)),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, nullable=False, server_default = sqlalchemy.func.now()),
    sqlalchemy.Column(
        "last_modified_at",
        sqlalchemy.DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
        onupdate=sqlalchemy.func.now(),
    ),
    sqlalchemy.Column("role", sqlalchemy.Enum(UserRole), nullable = False, server_default = UserRole.user.name)
)


class ColorEnum(enum.Enum):
    pink = "pink"
    black = "black"
    white = "white"
    yellow = "yellow"


class SizeEnum(enum.Enum):
    xs = "xs"
    s = "s"
    m = "m"
    l = "l"
    xl = "xl"
    xxl = "xxl"

clothes = sqlalchemy.Table(
    "clothes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(120)),
    sqlalchemy.Column("color", sqlalchemy.Enum(ColorEnum), nullable=False),
    sqlalchemy.Column("size", sqlalchemy.Enum(SizeEnum), nullable=False),
    sqlalchemy.Column("photo_url", sqlalchemy.String(255)),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.func.now()),
    sqlalchemy.Column(
        "last_modified_at",
        sqlalchemy.DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
        onupdate=sqlalchemy.func.now(),
    ),
)


class EmailField(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    # validate_email e EmailNotValidError importadas do pacote email_validator
    @classmethod
    def validate(cls, v) -> str:
        try:
            validate_email(v)
            return v
        except EmailNotValidError:
            raise ValueError("Email is not valid.")



class BaseUser(BaseModel):
    email: EmailField
    full_name: str

    @validator("full_name")
    def validate_full_name(cls, v):
        try:
            first_name, last_name = v.split()
            return v
        except Exception:
            raise ValueError("You should provide at least 2 names.")


# Validando a entrada de dados
class UserSignIn(BaseUser):
    password: str


# Validando a saída de dados
class UserSignOut(BaseUser):
    phone: Optional[str]
    created_at: datetime
    last_modified_at: datetime




app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

# Class de autenticação
class CustomHTTPBearer(HTTPBearer):
    async def __call__(
        self, request: Request
    ) -> Optional[HTTPAuthorizationCredentials]:
        res = await super().__call__(request)

        try:
            payload = jwt.decode(res.credentials, config("JWT_SECRET"), algorithms = ["HS256"])
            user = await database.fetch_one(users.select().where(users.c.id == payload["sub"]))
            request.state.user = user
            return payload
        except jwt.ExpiredSignatureError as ex:
            raise HTTPException(401, "The token is expired.")
        except jwt.InvalidTokenError as ex:
            raise HTTPException(401, "Invalid token.")


oauth2_scheme = CustomHTTPBearer()



def is_admin(request: Request):
    # Propriedade setada em CustomHTTPBearer
    user = request.state.user
    if not user or user["role"] not in (UserRole.super_admin, UserRole.admin):
        raise HTTPException(403, "You do not have permission.")



def create_access_token(user):
    try:
        payload = {
            "sub": user["id"],
            "exp": datetime.utcnow() + timedelta(minutes = 120)
        } 
        return jwt.encode(payload, config("JWT_SECRET"), algorithm = "HS256")
    except Exception as ex:
        raise ex


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/clothes/", dependencies = [Depends(oauth2_scheme)])
async def get_all_clothes(request: Request):
    return await database.fetch_all(clothes.select())


# Validando a saída
# @app.post("/register/", response_model = UserSignOut)
# Sem validar a saída
@app.post("/register/")
async def create_user(user: UserSignIn):
    user.password = pwd_context.hash(user.password)
    query = users.insert().values(**user.dict())
    id_ = await database.execute(query)
    # execute retorna o id, enquanto o fetch_one retorna o objeto criado no banco
    created_user = await database.fetch_one(users.select().where(users.c.id == id_))
    token = create_access_token(created_user)
    return { "token": token }
