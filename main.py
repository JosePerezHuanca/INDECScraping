from fastapi import FastAPI
from routes import ipc

app=FastAPI()
app.include_router(ipc.router)
