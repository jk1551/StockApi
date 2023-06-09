import os

import uvicorn
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from fastapi.security import HTTPBearer, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import jwt
from fastapi.responses import RedirectResponse, FileResponse
from supabase import create_client, Client
import requests
import base64

app = FastAPI()
security = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

JWT_SECRET = "PW1xgKBqGUBMXRDX9h7lGWJONna13snPYdc3XND55033p0YViTRJnwGyT1B9p2yO3Z7s/7bvRiAnU3zphivmhA=="
JWT_ALGORITHM = "HS256"

import os
from supabase import create_client, Client

url: str = 'https://ofyjmaufhrjgyoffhhjw.supabase.co'
key: str = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9meWptYXVmaHJqZ3lvZmZoaGp3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE2ODM3NTMwNzcsImV4cCI6MTk5OTMyOTA3N30.Gu4Y8D-d63BRh2SdhERJd07C9fPvdXJQB1tM8VJEerg'
supabase: Client = create_client(url, key)

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}

class User(BaseModel):
  username: str
  email: str | None = None
  full_name: str | None = None
  disabled: bool | None = None

def verify_token(token: str = Depends(security)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None or username not in fake_users_db:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return fake_users_db[username]
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def fake_hash_password(password: str):
    return "fakehashed" + password
class UserInDB(User):
    hashed_password: str


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def fake_decode_token(token):
  return User(username=token + "fakedecoded",
              email="john@example.com",
              full_name="John Doe")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
  user = fake_decode_token(token)
  return user

@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = jwt.encode({"sub": user.username}, JWT_SECRET, algorithm=JWT_ALGORITHM)
    print(token)
    return {"access_token": token, "token_type": "bearer"}

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
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

@app.get("/html", response_class=HTMLResponse)
async def read_items():
    return """
    <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1>Look ma! HTML!</h1>
        </body>
    </html>
    """
@app.get("/fastapi", response_class=RedirectResponse)
async def redirect_fastapi():
    return "https://fastapi.tiangolo.com"

class PDFData(BaseModel):
    pdf: str

@app.post("/store_pdf")
def post_pdf(body: PDFData):
    print(body.pdf)
    table_name = 'pdf'
    data = {'id': 1, 'pdf_data': body.pdf}
    result = supabase.table(table_name).insert(data).execute()
    print(result)
    return "Success"

@app.get("/pdf")
def file_response(file_url):
    # Download the PDF file from the URL
    response = requests.get(file_url)

    # Check if the request was successful
    if response.status_code == 200:
        # Convert the PDF content to base64 bytes
        pdf_base64 = base64.b64encode(response.content)
        return {"base64": pdf_base64.decode('utf-8')}
    else:
        return {"error": "Failed to download the PDF file."}

if __name__ == "__main__":
  uvicorn.run(app, host="0.0.0.0", port=10000)
