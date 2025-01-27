from typing import Optional

from pydantic import BaseModel, Field


class CreateUserRequest(BaseModel):
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    username: str = Field(min_length=1)
    password: str = Field(min_length=6)
    role: str = Field(min_length=1)


class EditUserRequest(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1)
    last_name: Optional[str] = Field(None, min_length=1)
    username: Optional[str] = Field(None, min_length=1)
    password: Optional[str] = Field(None, min_length=6)
    role: Optional[str] = Field(None, min_length=1)

class EditPasswordRequest(BaseModel):
    old_password: str = Field(min_length=6)
    new_password: str = Field(min_length=6)
