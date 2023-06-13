from pydantic import BaseModel, EmailStr
from bson import ObjectId
from typing import Optional
# Модель User
class User(BaseModel):
    user_id: str
    user_name: str
    user_email: EmailStr  
    user_phone: str
    password: str
    lang: str
    user_favorites: str 
    user_image: Optional[bytes]

# Модель Showplace
class Showplace(BaseModel):
    showplace_id: str
    showplace_title_en: str
    showplace_title_ru: str
    showplace_title_kz: str
    showplace_image: Optional[bytes]
    description_en: str
    description_ru: str
    description_kz: str
    marked_count: int
 