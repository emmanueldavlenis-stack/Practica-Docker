from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from app.app.database import SessionLocal, engine
from app.app.models import User, Base
from prometheus_client import Counter, generate_latest
from fastapi.responses import Response


app = FastAPI()
USER_CREATED = Counter("user_created", "Number of users created")
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@app.post("/users")
def create_user(name: str, age: int, db: Session = Depends(get_db)):
    user = User(name=name, age=age)
    db.add(user)
    db.commit()
    db.refresh(user)
    USER_CREATED.inc()
    return user


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")