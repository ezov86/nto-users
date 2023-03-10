import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import load_config

from app.api.endpoints import tg_router, tokens_router
from app.db import connect_to_db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'DELETE', 'PATCH'],
    allow_headers=['*'],
)

app.include_router(tg_router)
app.include_router(tokens_router)


@app.on_event('startup')
async def startup():
    load_config()
    connect_to_db()
    # create_admin_if_not_exists()


@app.on_event('shutdown')
async def shutdown():
    ...


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
