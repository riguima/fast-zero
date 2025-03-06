from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from fast_zero.schemas import Message

app = FastAPI()


@app.get('/', response_model=Message)
def read_root():
    return {'message': 'Hello World'}


@app.get('/html', response_class=HTMLResponse)
def read_root_html():
    return '<h1>Hello World</h1>'
