from pydantic import BaseModel, ConfigDict, EmailStr

from fast_zero.models import TaskState


class Message(BaseModel):
    message: str


class User(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    username: str
    email: EmailStr
    id: int
    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    users: list[UserPublic]


class Token(BaseModel):
    access_token: str
    token_type: str


class FilterPage(BaseModel):
    offset: int = 0
    limit: int = 100


class Task(BaseModel):
    title: str
    description: str
    state: TaskState


class TaskPublic(Task):
    id: int


class TaskList(BaseModel):
    tasks: list[TaskPublic]


class FilterTask(FilterPage):
    title: str | None = None
    description: str | None = None
    state: TaskState | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    state: TaskState | None = None
