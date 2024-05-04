import uuid
import datetime
from fastapi import APIRouter
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from repository import UserRepository
from schemas import USER, USER_add
from typing import Annotated
from utils import hash_password

router = APIRouter()

# Авторизация
oauth_scheme = OAuth2PasswordBearer(tokenUrl='/token')
@router.post('/token')
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
      return {'access_token': form_data.username, 'token_type': 'bearer'}



# Базовый маршрут
@router.get('/', status_code=200)
async def base_page():
      return "Welcome на Ботоферму ;)"



# Создание нового пользователя
@router.post('/create_user')
async def create_user(user_request: Annotated[USER_add, "USER_add", Depends()], token: str = Depends(oauth_scheme)):
      # Проверка на корректность env и domain из запроса
      if user_request.env in ('prod', 'preprod', 'stage') and user_request.domain in ('canary', 'regular'):
            user = USER (
                  id=uuid.uuid4(),
                  created_at=str(datetime.datetime.now()),
                  login=user_request.login,
                  password=user_request.password,
                  project_id=uuid.uuid4(),
                  env=user_request.env,
                  domain=user_request.domain
            )

            # Шифрование пароля
            user.password = hash_password(user.password)
            
            result = await UserRepository.insert_user(user)
            if result: # Проверка на внутреннюю ошибку сервера
                  return JSONResponse(content={'message': 'пользователь создан', 'id': str(user.id)}, status_code=201)
            return JSONResponse(content={'message': 'Internal Server Error'}, status_code=500)
      return JSONResponse(content={'message': 'некорректное значение env или domain'}, status_code=400)



# Получение списка всех пользователей
@router.get('/get_users')
async def get_users(token: str = Depends(oauth_scheme)):
      return await UserRepository.get_all_users()



# Удаление пользователя по id
@router.delete('/delete_user/{id}')
async def delete_user(id, token: str = Depends(oauth_scheme)):
      flag_deleted = await UserRepository.delete_user(id)
      if flag_deleted == True: # Проверка на внутреннюю ошибку сервера
            return JSONResponse(content={'message': 'пользователь удален'})
      elif flag_deleted == False:
            return JSONResponse(content={'message': 'пользователя с данным id не существует'})
      return JSONResponse(content={'message': 'Internal Server Error'}, status_code=500)



# Обновление пользователя по id
@router.patch('/update_user/{id}')
async def update_user(id, user_request: Annotated[USER_add, "USER_add", Depends()], token: str = Depends(oauth_scheme)):
      if user_request.env in ('prod', 'preprod', 'stage') and user_request.domain in ('canary', 'regular'):
            user = USER_add (
                  login=user_request.login,
                  password=user_request.password,
                  env=user_request.env,
                  domain=user_request.domain
            )
            user.password = hash_password(user.password)

            flag_updated = await UserRepository.update_user(id, user)
            if flag_updated:
                  return JSONResponse(content={'message': 'данные пользователя обновлены'})
            return JSONResponse(content={'message': 'пользователя с данным id не существует'})
      return JSONResponse(content={'message': 'некорректное значение env или domain'}, status_code=400)



# Наложение блокировки на пользователя (выдача для E2E-теста)
@router.patch('/acquire_lock/{id}')
async def acquire_lock(id, token: str = Depends(oauth_scheme)):
      flag_acquired, flag_internal_error = await UserRepository.acquire_lock(id)
      if not flag_internal_error: # Проверка на внутреннюю ошибку сервера
            if flag_acquired: # Проверка на блокировку
                  return JSONResponse(content={'message': 'Блокировка наложена'})
            return JSONResponse(content={'message': 'Данный пользователь занят'})
      return JSONResponse(content={'message': 'Internal Server Error'}, status_code=500)



# Снятие блокировки с пользователя
@router.patch('/release_lock/{id}')
async def release_lock(id, token: str = Depends(oauth_scheme)):
      flag_released, flag_internal_error = await UserRepository.release_lock(id)
      if not flag_internal_error: # Проверка на внутреннюю ошибку сервера
            if flag_released: # Проверка на блокировку
                  return JSONResponse(content={'message': 'Блокировка снята'})
      return JSONResponse(content={'message': 'Internal Server Error'}, status_code=500)