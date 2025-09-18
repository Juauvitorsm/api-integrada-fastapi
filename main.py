from database import Base, engine
from app.auth import endpoints as auth_endpoints
from app.api import endpoints as api_endpoints
from app.auth import models as auth_models
from app.api import models as api_models
from fastapi import FastAPI



Base.metadata.create_all(bind=engine)

app = FastAPI()


app.include_router(auth_endpoints.router, prefix="/auth", tags=["auth"])
app.include_router(api_endpoints.router, prefix="/api", tags=["api"])

@app.get("/")
def read_root():
    return {"message": "API integrada funcionando!"}