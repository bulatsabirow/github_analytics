from fastapi import FastAPI

from app.views import router

app = FastAPI(title="Github Analytics")
app.include_router(router)
