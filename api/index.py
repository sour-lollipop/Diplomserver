from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pymongo import MongoClient
from models import User, Showplace
from uuid import uuid4
from pydantic import BaseModel, EmailStr

# from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
security = HTTPBasic()

# # Разрешить запросы с определенных источников
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Установите здесь домены, с которых разрешены запросы (или используйте "*", чтобы разрешить все домены)
#     allow_methods=["*"],  # Установите здесь разрешенные HTTP-методы
#     allow_headers=["*"],  # Установите здесь разрешенные заголовки
# )

# Подключение к MongoDB
client = MongoClient("mongodb+srv://akmaral:aktolkyn2018@cluster0.pcya0p3.mongodb.net/")
db = client["mydatabase"]
user_collection = db["users"]
showplace_collection = db["showplaces"]
# *******************************
# ТЕСТОВЫЕ ЗАПРОСЫ
client_collection = db['test_clients']

# Модель пользователя
class Client(BaseModel):
    user_name: str
    user_email: str
    user_phone: str
    password: str

# Роут для создания пользователя
@app.post('/clients')
def create_user(client: Client):
    # Проверка наличия пользователя с таким email
    existing_user = client_collection.find_one({'user_email': client.user_email})
    if existing_user:
        return {'message': 'User with this email already exists'}

    # Создание нового пользователя
    user_dict = client.dict()
    client_collection.insert_one(user_dict)

# *******************************
    return {'message': 'User created successfully'}
# Аутентификация пользователя
def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    user = user_collection.find_one({"user_email": credentials.username})
    if user and user["password"] == hash(credentials.password):
        return user
    raise HTTPException(status_code=401, detail="Invalid username or password")

# Создание пользователя
@app.post("/users")
def create_user(user: User):
    user_id = str(uuid4())
    user.user_id = user_id
    user_dict = user.dict()
    user_dict['password'] = hash(user_dict["password"])
    if not user.user_email.count("@") == 1:
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    if user_collection.find_one({"user_email": user.user_email}):
        return {"message": "This email already exists"}
    elif user_collection.find_one({"user_phone": user.user_email}):
        return {"message": "This phone already exists"}
    else:
        user_collection.insert_one(user_dict) 
        return {"message": "User created successfully"}

# Поиск пользователя
@app.get("/users/{_id}")
def get_user(_id: str, authenticated_user: User = Depends(authenticate)):
    user = user_collection.find_one({"user_id": _id})
    if user:
        return User(**user)
    else:
        raise HTTPException(status_code=404, detail="User not found")

# Редактирование пользователя
@app.put("/users/{_id}")
def update_user(_id: str, user: User, image: UploadFile = File(...), authenticated_user: User = Depends(authenticate)):
    user_dict = user.dict(exclude_unset=True)
    user = user_collection.update_one({"user_id": _id}, {"$set": user_dict})
    return {"message": "User updated successfully"}

# Обновление аватара пользователя
@app.put("/users_image/{_id}")
def upload_user_image(_id: str, image: UploadFile = File(...), authenticated_user: User = Depends(authenticate)):
    user = user_collection.find_one({"user_id": _id})
    if user:
        user_image = image.file.read()
        user_collection.update_one({"user_id": _id}, {"$set": {"user_image": user_image}})
        return {"message": "Image uploaded successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")

# Удаление пользователя
@app.delete("/users/{_id}")
def delete_user(_id: str, authenticated_user: User = Depends(authenticate)):
    user_collection.delete_one({"user_id": _id})
    return {"message": "User deleted successfully"}

# Создание достопромичательности
@app.post("/showplaces")
def create_showplace(
                    showplace_title_en: str,
                    showplace_title_ru: str, 
                    showplace_title_kz: str, 
                    description_en: str,
                    description_ru: str,
                    description_kz: str,
                    image: UploadFile = File(...),
                    authenticated_user: User = Depends(authenticate)
                    ):
    showplace_image = image.file.read()
    showplace_id = str(uuid4())
    Showplace = {
        "showplace_id": showplace_id,
        "showplace_title_en" : showplace_title_en,
        "showplace_title_ru": showplace_title_ru, 
        "showplace_title_kz": showplace_title_kz,
        "showplace_images": showplace_image,
        "description_en": description_en,
        "description_ru": description_ru,
        "description_kz": description_kz,
        "marked_count": 0
    }
    if showplace_collection.find_one({'showplace_title_en': showplace_title_en}):
        return {"message": "this showplace exist"}
    else:
        showplace_collection.insert_one(Showplace)
        return {"message": "Showplace created successfully"}

# Поиск достопромичательности
@app.get("/showplaces/{_id}")
def get_showplace(_id: str, authenticated_user: User = Depends(authenticate)):
    showplace = showplace_collection.find_one({"showplace_id": _id})
    if showplace:
        return Showplace(**showplace)
    else:
        raise HTTPException(status_code=404, detail="Showplace not found")

# Редактирование достопромичательности
@app.put("/showplaces/{_id}")
def update_showplace(_id: str, showplace_title_en: str,
                    showplace_title_ru: str, 
                    showplace_title_kz: str, 
                    description_en: str,
                    description_ru: str,
                    description_kz: str,
                    image: UploadFile = File(...),
                    authenticated_user: User = Depends(authenticate)
                    ):
    showplace_image = image.file.read()
    Showplace = {
        "showplace_title_en" : showplace_title_en,
        "showplace_title_ru": showplace_title_ru, 
        "showplace_title_kz": showplace_title_kz,
        "showplace_images": showplace_image,
        "description_en": description_en,
        "description_ru": description_ru,
        "description_kz": description_kz
    }
    showplace_collection.update_one({"showplace_id": _id}, {"$set": Showplace})
    return {"message": "Showplace updated successfully"}

# Удаление достопромичательности
@app.delete("/showplaces/{_id}")
def delete_showplace(_id: str, authenticated_user: User = Depends(authenticate)):
    showplace_collection.delete_one({"showplace_id": _id})
    return {"message": "Showplace deleted successfully"}