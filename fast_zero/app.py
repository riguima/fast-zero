from fastapi import FastAPI

from fast_zero.routers import auth, tasks, users

app = FastAPI()
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(tasks.router)
