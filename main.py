"""
Execute this file to run the server local
"""

import configparser
import sys

import uvicorn
from fastapi import FastAPI

config = configparser.ConfigParser()

config.read("config.ini")

for key, value in config.items("pythonpath"):
    sys.path.append(value)

from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")
from fastapi.middleware.cors import CORSMiddleware

from modules.auth.app import router as auth_router
from modules.product.app import router as product_router
from modules.user.app import router as user_router

app = FastAPI()

origins = ["http://127.0.0.1:8000"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # max_age=3600,
)


@app.options("/{path:path}")
async def options_handler(request, response, path):
    response.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin", "*")
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return {"message": "ok"}


app.include_router(user_router)
app.include_router(auth_router)
app.include_router(product_router)

if __name__ == "__main__":
    uvicorn.run("main:app", port=8001, reload=True)
