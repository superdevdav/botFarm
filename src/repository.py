from database import UsersOrm, new_session
from schemas import USER, USER_add
from sqlalchemy.sql import text
from sqlalchemy.exc import DBAPIError
import datetime

class UserRepository:
      
      # Получение всех пользователей из БД
      @classmethod
      async def get_all_users(cls) -> list:
            async with new_session() as session:
                  query = text('SELECT * FROM users')
                  result = await session.execute(query)
                  users = [dict(zip(result.keys(), row)) for row in result.fetchall()]
                  return users

      
      # Наложение блокировки на пользователя
      @classmethod
      async def acquire_lock(cls, id):
            flag_acquired = None # Флаг на блокировку
            flag_internal_error = False # Флаг на внутр. ошибку сервера
            try:
                  async with new_session() as session:
                        query = text('UPDATE users SET locktime = :timestamp WHERE id = :id AND locktime IS NULL;')
                        result = await session.execute(query, {'timestamp': str(datetime.datetime.now().timestamp()), 'id': id})
                        # Проверяем, была ли произведена блокировка
                        if result.rowcount > 0:
                              await session.flush()
                              await session.commit()
                              flag_acquired = True
                        else:
                              # Блокировка уже установлена
                              flag_acquired = False
            except Exception as _:
                  flag_internal_error = True
            return (flag_acquired, flag_internal_error)

      
      # Снятие блокировки с пользователя
      @classmethod
      async def release_lock(cls, id):
            flag_released = None # Флаг на снятие блокировки
            flag_internal_error = None # Флаг на внутр. ошибку сервера
            try:
                  async with new_session() as session:
                        query = text('UPDATE users SET locktime = NULL WHERE id = :id;')
                        await session.execute(query, {'id': id})
                        await session.flush()
                        await session.commit()
                        flag_released = True
                        flag_internal_error = False
            except Exception as _:
                  flag_internal_error = True
                  flag_released = False
            return (flag_released, flag_internal_error)
      
      
      # Добавление пользователя в БД
      @classmethod
      async def insert_user(cls, data: USER):
            flag_inserted = None
            try:
                  async with new_session() as session:
                        user_dict = data.model_dump()
                        user = UsersOrm(**user_dict)
                        session.add(user)
                        await session.flush()
                        await session.commit()
                        flag_inserted = True
                        return user.id
            except Exception as _:
                  flag_inserted = False
            return flag_inserted


      # Обновление данных пользователя
      @classmethod
      async def update_user(cls, id, data: USER_add):
            flag_updated = False
            try:
                  async with new_session() as session:
                        user_dict = data.model_dump()

                        # Составление sql запроса
                        sqlStatement = text('''
                        UPDATE users 
                        SET 
                              login = :login, 
                              password = :password, 
                              env = :env, 
                              domain = :domain 
                        WHERE id = :id
                        ''')

                        # Передача значений через параметры запроса
                        await session.execute(sqlStatement, {
                        'login': user_dict['login'] if user_dict['login'] != '_' else None,
                        'password': user_dict['password'] if user_dict['password'] != '_' else None,
                        'env': user_dict['env'] if user_dict['env'] != '_' else None,
                        'domain': user_dict['domain'] if user_dict['domain'] != '_' else None,
                        'id': id
                        })
                        await session.flush()
                        await session.commit()
                        flag_updated = True
            except DBAPIError as _:
                  flag_updated = False
            return flag_updated


      # Удаление пользователя по id из БД
      @classmethod
      async def delete_user(cls, id):
            flag_deleted = None
            try:
                  async with new_session() as session:
                        query = text('DELETE FROM users WHERE id = :id;')
                        await session.execute(query, {'id': id})
                        await session.flush()
                        await session.commit()
                        flag_deleted = True
            except DBAPIError:
                  flag_deleted = False
            return flag_deleted