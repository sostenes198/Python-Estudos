from typing import List, Optional
import os
import logging
import datetime
import jwt
from functools import wraps

from fastapi import FastAPI, Depends, HTTPException, status, Header, Query
from pydantic import BaseModel
import joblib
import numpy as np
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, desc
from sqlalchemy.orm import declarative_base, sessionmaker, Session

JWT_SECRET = "MY_SECRET_HERE"

JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = 3600

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('api_modelo')

DB_URL = "sqlite:///predictions.db"
engine = create_engine(DB_URL, echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)


class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    sepal_length = Column(Float, nullable=False)
    sepal_width = Column(Float, nullable=False)
    petal_length = Column(Float, nullable=False)
    petal_width = Column(Float, nullable=False)
    predicted_class = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC))


Base.metadata.create_all(engine)
model = joblib.load('modelo_iris.pkl')
logger.info('Modelo carregado com sucesso')

TEST_USERNAME = 'admin'
TEST_PASSWORD = 'secret'

def create_token(username):
    payload = {
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # pegar token do header Authorization: Bearer <token>
        # decodificar e checar expiração
        return f(*args, **kwargs)

    return decorated


# --------- deps ---------
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(authorization: str = Header(...)) -> str:
    """
    Lê o header Authorization: Bearer <token>, valida e retorna o username.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token ausente ou inválido",
        )
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido"
        )
    username = payload.get("username")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token sem username"
        )
    return username


# ===== Schemas =====
class LoginIn(BaseModel):
    username: str
    password: str


class TokenOut(BaseModel):
    token: str

class PredictIn(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float


class PredictOut(BaseModel):
    predicted_class: int


class PredictionOut(BaseModel):
    id: int
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float
    predicted_class: int
    created_at: datetime.datetime


app = FastAPI()
predictions_cache: dict[tuple[float, float, float, float], int] = {}


# ===== Endpoint =====
@app.post("/login", response_model=TokenOut)
def login(body: LoginIn):
    if body.username == TEST_USERNAME and body.password == TEST_PASSWORD:
        return TokenOut(token=create_token(body.username))
    raise HTTPException(status_code=401, detail="Credenciais inválidas")


@app.post("/predict", response_model=PredictOut)
def predict(
    body: PredictIn,
    username: str = Depends(get_current_user),  # valida o Bearer token
    db: Session = Depends(get_db),
):
    # features normalizadas/validadas pelo Pydantic
    features = (body.sepal_length, body.sepal_width, body.petal_length, body.petal_width)

    # cache
    if features in predictions_cache:
        predicted_class = predictions_cache[features]
        logger.info("Cache hit para %s", features)
    else:
        try:
            input_data = np.array([features], dtype=float)  # shape (1, 4)
            prediction = model.predict(input_data)
            predicted_class = int(prediction[0])
        except Exception as e:
            logger.exception("Erro ao rodar o modelo: %s", e)
            raise HTTPException(
                status_code=500, detail="Falha ao executar a predição"
            )
        predictions_cache[features] = predicted_class
        logger.info("Cache atualizado para %s", features)

    # persistência
    try:
        rec = Prediction(
            sepal_length=features[0],
            sepal_width=features[1],
            petal_length=features[2],
            petal_width=features[3],
            predicted_class=predicted_class,
        )
        db.add(rec)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.exception("Erro ao salvar no banco: %s", e)
        # não bloqueia a resposta de predição; apenas registra o erro

    return PredictOut(predicted_class=predicted_class)

@app.get("/predictions", response_model=List[PredictionOut])
def list_predictions(
    limit: int = Query(10, ge=1, le=100, description="Quantos registros retornar"),
    offset: int = Query(0, ge=0, description="Registro inicial para paginação"),
    username: str = Depends(get_current_user),  # Proteção via Bearer token
    db: Session = Depends(get_db),
):
    """
    Lista as predições armazenadas no banco.
    Parâmetros opcionais:
    - limit: número de registros a retornar (padrão 10)
    - offset: deslocamento inicial (padrão 0)
    Exemplo: /predictions?limit=5&offset=10
    """
    preds = (
        db.query(Prediction)
        .order_by(desc(Prediction.id))
        .limit(limit)
        .offset(offset)
        .all()
    )

    return [
        PredictionOut(
            id=p.id,
            sepal_length=p.sepal_length,
            sepal_width=p.sepal_width,
            petal_length=p.petal_length,
            petal_width=p.petal_width,
            predicted_class=p.predicted_class,
            created_at=p.created_at,
        )
        for p in preds
    ]

if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=5000, log_level=logger.level, reload=True)