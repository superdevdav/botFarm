import hashlib

# Функция для хэширования пароля
def hash_password(pswd):
      """Hashes a string using the SHA-256 algorithm."""
      hash_object = hashlib.sha256()
      hash_object.update(pswd.encode('utf-8'))
      return hash_object.hexdigest()