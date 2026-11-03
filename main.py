"""FastAPI application: calculator endpoints plus secure user registration."""

import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app import crud, operations
from app.database import Base, engine, get_db
from app.schemas.user import UserCreate, UserRead

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Create database tables on startup. The calculator still works if the DB is down."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables are ready")
    except OperationalError as exc:  # pragma: no cover
        logger.warning("Database not reachable at startup: %s", exc)
    yield


app = FastAPI(title="FastAPI Calculator with Secure Users", lifespan=lifespan)
templates = Jinja2Templates(directory="templates")


class OperationRequest(BaseModel):
    """Two operands for a calculator operation."""

    a: float
    b: float


class OperationResponse(BaseModel):
    """Result of a calculator operation."""

    result: float


@app.get("/")
def index(request: Request):
    """Serve the calculator web page."""
    return templates.TemplateResponse(request, "index.html")


@app.get("/health")
def health():
    """Simple health check used by Docker."""
    return {"status": "ok"}


OPERATIONS = {
    "add": operations.add,
    "subtract": operations.subtract,
    "multiply": operations.multiply,
    "divide": operations.divide,
}


@app.post("/{operation}", response_model=OperationResponse)
def calculate(operation: str, payload: OperationRequest):
    """Run add, subtract, multiply or divide on the two operands."""
    func = OPERATIONS.get(operation)
    if func is None:
        raise HTTPException(status_code=404, detail=f"Unknown operation: {operation}")
    try:
        result = func(payload.a, payload.b)
    except ValueError as exc:
        logger.error("%s failed: %s", operation, exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    logger.info("%s(%s, %s) = %s", operation, payload.a, payload.b, result)
    return OperationResponse(result=result)


@app.post("/users/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """Register a new user. The password is hashed before it is stored."""
    try:
        user = crud.create_user(db, user_in)
    except crud.DuplicateUserError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    logger.info("Registered user %s", user.username)
    return user


@app.get("/users/{user_id}", response_model=UserRead)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Return a user's public details (never the password hash)."""
    user = crud.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)