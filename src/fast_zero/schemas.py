from pydantic import BaseModel, EmailStr


class MessageSchema(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublicSchema(BaseModel):
    username: str
    email: EmailStr


class UserDB(UserPublicSchema):
    id: int


class UserList(BaseModel):
    users: list[UserPublicSchema]
