from typing import Annotated 
from pydantic import BaseModel, EmailStr, Field, StringConstraints, ConfigDict 
 
NameStr = Annotated[str, StringConstraints(min_length=2, max_length=25, pattern=r"^[A-Za-z]+$")] #name is allowed alphabet letters only - no numbers or special characters 
UserNameStr = Annotated[str, StringConstraints(min_length=2, max_length=9)] 
PasswordStr = Annotated[str, StringConstraints(min_length=7, max_length=50)]
 
class UserCreate(BaseModel): 
    name: NameStr 
    email: EmailStr 
    password: PasswordStr
    age: int = Field(gt=12) 
    user_name: UserNameStr  
 
class UserRead(BaseModel): 
    user_id: int 
    name: NameStr 
    email: EmailStr 
    password: PasswordStr
    age: int 
    user_name: UserNameStr 
 
    model_config = ConfigDict(from_attributes=True)