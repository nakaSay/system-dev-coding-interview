from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas, auth
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_session = Depends(get_db)


@app.get("/health-check")
def health_check(db: Session = db_session):
    return {"status": "ok"}


@app.post("/users/")
def create_user(user: schemas.UserCreate, db: Session = db_session):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = crud.create_user(db=db, user=user)
    return {"db_user": db_user, "x_api_token": auth.create_tokens(db_user.id)}


@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = db_session, current_user_id: str = Depends(auth.get_current_user_id)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = db_session, current_user_id: str = Depends(auth.get_current_user_id)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/users/{user_id}/delete", response_model=schemas.User)
def read_user(user_id: int, db: Session = db_session, current_user_id: str = Depends(auth.get_current_user_id), skip: int = 0, limit: int = 100,):
    delete_user = crud.get_user(db, user_id=user_id)
    if delete_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    delete_user.is_active = False

    first_active_user = crud.get_first_active_user(db, delete_user.id)
    for item in delete_user.items:
        item.owner_id = first_active_user.id

    crud.update_user(db, delete_user)
    crud.update_user(db, first_active_user)

    return delete_user

@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
    user_id: int, item: schemas.ItemCreate, db: Session = db_session, current_user_id: str = Depends(auth.get_current_user_id)
):
    return crud.create_user_item(db=db, item=item, user_id=user_id)

@app.get("/items/", response_model=List[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = db_session, current_user_id: str = Depends(auth.get_current_user_id)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items

@app.get("/me/items", response_model=List[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = db_session, current_user_id: str = Depends(auth.get_current_user_id)):
    items = crud.get_owner_items(db, current_user_id, skip=skip, limit=limit)
    return items