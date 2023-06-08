import uvicorn
from typing import Annotated
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import crud


app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
  username: str
  email: str | None = None
  full_name: str | None = None
  disabled: bool | None = None


def fake_decode_token(token):
  return User(username=token + "fakedecoded",
              email="john@example.com",
              full_name="John Doe")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
  user = fake_decode_token(token)
  return user


@app.get("/users/me")
async def read_users_me(current_user: Annotated[User,
                                                Depends(get_current_user)]):
  return current_user


app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_methods=["*"],
  allow_headers=["*"],
  allow_credentials=False,
)


@app.get("/")
def main():
  return RedirectResponse(url="/docs")


@app.get("/items/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
  return {"token": token}


@app.get("/api/stocks")
async def get_stocks():
  stocks = crud.get_stock_data()
  return stocks

@app.get("/api/stocks/{ticker}")
async def get_single_stock(ticker: str):
  stock = await crud.get_single_stock(ticker);
  return stock;


if __name__ == "__main__":
  uvicorn.run(app, host="0.0.0.0", port=10000)
