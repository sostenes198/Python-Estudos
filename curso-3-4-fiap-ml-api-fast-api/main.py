from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel


# ----- Schemas -----
class ItemBase(BaseModel):
    name: str
    description: str | None = None
    price: float | None = None
    quantity: int | None = None


class Item(ItemBase):  # usado para armazenamento/retorno
    id: int


app = FastAPI(
    title='My FastAPI API',
    version='1.0.0',
    description='My FastAPI API',
)

users = {
    "user1": "password",
    "user2": "password"
}

security = HTTPBasic()


def verify_password(credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username
    password = credentials.password

    if username in users and users[username] == password:
        return username

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Basic"},
    )


items: List[Item] = []


@app.get('/')
async def home():
    return "Hello, FastApi"


@app.get('/hello')
async def hello(username: str = Depends(verify_password)):
    return f"Hello {username}, AuthenticatedFastApi"


@app.get('/items')
async def get_items():
    return items


@app.post('/items')
async def post_items(item: Item):
    items.append(item)

    return item


@app.put('/items/{item_id}')
async def put_items(item_id: int, updated_item: ItemBase):
    index = next((i for i, item in enumerate(items) if item.id == item_id), None)
    if index is not None:
        data = updated_item.model_dump(exclude_unset=True)
        for k, v in data.items():
            setattr(items[index], k, v)
        return items[index]

    raise HTTPException(status_code=404, detail="Item not found")


@app.delete('/items/{item_id}')
async def delete_items(item_id: int):
    index = next((i for i, item in enumerate(items) if item.id == item_id), None)
    if index is not None:
        removed_item = items.pop(index)
        return removed_item

    raise HTTPException(status_code=404, detail="Item not found")


if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=5000, log_level="info", reload=True)
