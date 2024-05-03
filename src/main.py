# uvicorn main:app --reload
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from contextlib import asynccontextmanager
from database import create_tables
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../tests")))
from router import router as user_router

@asynccontextmanager
async def lifespan(app: FastAPI):
      await create_tables()
      print('INFO:     База данных создана')
      yield
      print('INFO:     Выключение')

app = FastAPI(lifespan=lifespan)
app.include_router(user_router)