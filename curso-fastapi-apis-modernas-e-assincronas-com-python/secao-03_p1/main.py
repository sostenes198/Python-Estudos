from typing import Any, List
from fastapi import FastAPI, HTTPException, status, Path, Query, Header, Depends
from fastapi.responses import JSONResponse

from models import Curso, cursos
from time import sleep


def fake_db():
    try:
        print('Abrindo conexão com o banco de dados')
        sleep(1)
    finally:
        print('Fechando conexão com o banco de dados')
        sleep(1)


app = FastAPI(
    title='Estudos FastApi',
    version='0.0,1',
    description='Uma API para estudos do FastApi')


@app.get('/cursos',
         summary='Retorna todos os curso',
         description='Description',
         response_model=dict[int, Curso],
         response_description="Cursos encontrados com sucesso")
async def get_cursos(db: Any = Depends(fake_db)):
    return cursos


@app.get('/cursos/{curso_id}')
async def get_curso_by_id(curso_id: int):
    try:
        return cursos[curso_id]
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso não encontrado")


@app.post('/cursos')
async def post_curso(curso: Curso):
    if curso.id not in cursos:
        cursos[curso.id] = curso
        return curso
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'Já existe um curso com o id {curso.id}')


@app.put('/cursos/{curso_id}')
async def put_curso(curso_id: int, curso: Curso):
    if curso_id in cursos:
        cursos[curso_id] = curso
        return curso
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não existe um curso com o id {curso_id}')


@app.delete('/cursos/{curso_id}')
async def put_curso(curso_id: int):
    if curso_id in cursos:
        del cursos[curso_id]
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não existe um curso com o id {curso_id}')


@app.get('/calculadora')
async def calcular(a: int = Query(default=None), b: int = Query(default=None), c: int = Query(default=None), x_geek: str = Header(default=None)):
    soma: int = a + b + c

    print(f'X-GEEK {x_geek}')

    return {"resultado": soma}


if __name__ == '__main__':
    import uvicorn


    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info", reload=True)
