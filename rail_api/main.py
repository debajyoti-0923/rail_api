from fastapi import Depends,FastAPI,HTTPException,status,Form

from . import models
from . import crud, schemas
from .database import sessionlocal,engine
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from .dependencies import get_db,authenticate_user,create_access_token

crud.populate()
models.base.metadata.create_all(bind=engine)
app=FastAPI()

'''
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
dt=datetime.now()

scheduler=BackgroundScheduler()
scheduler.add_job(populate,'interval',days=1,start_date=dt)
scheduler.start()



@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()
''' 


#routes
from .routers import users,admin,book
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(book.router)



@app.get("/")
async def root():
    return {"detail":"devu rail api"}

@app.post("/token", response_model=schemas.Token,status_code=201,tags=["authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),db:Session=Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username,"admin":user.admin})
    # print(is_admin,user.admin)
    # if is_admin:
    #     if user.admin:
    #         return {"access_token": access_token, "token_type": "bearer"}   
    #     else:
    #         raise HTTPException(
    #             status_code=status.HTTP_401_UNAUTHORIZED,
    #             detail="You are not a admin",
    #             headers={"WWW-Authenticate":"Bearer"}
    #         )
    return {"access_token": access_token, "token_type": "bearer"}   


@app.post("/username",description="If username exists",status_code=201,tags=["authentication"])
async def if_username_exists(
    user:schemas.UserName,
    db:Session=Depends(get_db)
):
    db_user=crud.get_user(db=db,username=user.username)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )
    
    return {"detail":"OK"}

@app.post("/register",response_model=schemas.UserEmail,status_code=201,tags=["authentication"])
async def register_user(
    user:schemas.UserCreate,
    db:Session=Depends(get_db)
):
    db_user_name=crud.get_user(db=db,username=user.username)
    db_user_email=crud.get_user(db=db,email=user.email)
    if db_user_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    if db_user_name:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )
    response=crud.create_user(db=db,user=user)
    return schemas.UserEmail(username=response.username,email=response.email)
