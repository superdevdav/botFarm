import uuid
from pydantic import BaseModel
from typing import Optional

# Сущность пользователя для запроса на добавление
class USER_add(BaseModel):
      login: str
      password: str
      env: str # название окружения (prod, preprod, stage)
      domain: str # тип пользователя (canary, regular)

# Сущность пользователя
class USER(USER_add):
      id: uuid.UUID # UUID пользователя
      created_at: str
      project_id: uuid.UUID # UUID проекта, к которому принадлежит пользователь
      locktime: Optional[str] = None # временная метка (timestamp)