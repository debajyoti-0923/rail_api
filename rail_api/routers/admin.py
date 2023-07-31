from fastapi import APIRouter,Depends,HTTPException,Body,status

from .. import crud
from .. import schemas
from ..dependencies import get_db,get_user_details
from .. import dependencies as dep
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm


router=APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={404:{"description":"Not found"}}
)

'''
fix update cretae new upudate schema
add timetable feature
new routine
modify routine
delete routine

'''
@router.get("/info",response_model=schemas.UserBase,status_code=201)
async def get_user_info(
    user:schemas.UserBase=Depends(dep.get_admin_details)
):
    return user

@router.post("/login",response_model=schemas.Token,status_code=201)
async def admin_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db:Session=Depends(get_db)
):
    user = dep.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.admin:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You are not a admin",
                headers={"WWW-Authenticate":"Bearer"}
            )
    access_token = dep.create_access_token(data={"sub": user.username,"admin":user.admin})
    return {"access_token": access_token, "token_type": "bearer"} 
#-------------------------------------------------------------------------------------------
@router.get("/get_stn",response_model=list[schemas.Station],status_code=201,tags=["Station"])
async def get_station(
    *,
    user:schemas.UserBase=Depends(dep.get_admin_details),
    db:Session=Depends(get_db),
):
    response=crud.get_station(db)
    try:
        if response.detail:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=dict(response),
                headers={"WWW-Authenticate":"Bearer"}
            )
    except AttributeError:
        pass
    return response


@router.post("/add_stn",response_model=schemas.outStation,status_code=201,tags=["Station"])
async def add_station(
    *,
    user:schemas.UserBase=Depends(dep.get_admin_details),
    station:schemas.Station=Body(...,description="get station details"),
    db:Session=Depends(get_db)
):
    response=crud.create_station(db=db,stn=station)
    if response.status=="failed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=dict(response),
            headers={"WWW-Authenticate": "Bearer"}
        )
    return response



@router.delete("/rem_stn",response_model=schemas.outStation,status_code=201,tags=["Station"])
async def remove_station(
    *,
    user:schemas.UserBase=Depends(dep.get_admin_details),
    db:Session=Depends(get_db),
    station:schemas.Station_id=Body(...,description="stn to be removed")
):
    response=crud.remove_station(db=db,stn=station)
    try:
        if response.detail:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=dict(response),
                headers={"WWW-Authenticate": "Bearer"}
            )
    except AttributeError:
        pass
    return response

@router.patch("/mod_stn",response_model=schemas.outStation,status_code=201,tags=["Station"])
async def modify_station(
    *,
    user:schemas.UserBase=Depends(dep.get_admin_details),
    db:Session=Depends(get_db),
    station:schemas.upStaion=Body(...,description="stn to be modified")
):
    response=crud.modify_station(db=db,stn=station)
    try:
        if response.detail:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=dict(response),
                headers={"WWW-Authenticate": "Bearer"}
            )
    except AttributeError:
        pass
    return response


# #-------------------------------------------------------------------------------------------

@router.get("/get_trn",response_model=list[schemas.outTrain],status_code=201,tags=["Train"])
async def get_train(
    *,
    user:schemas.UserBase=Depends(dep.get_admin_details),
    db:Session=Depends(get_db)
):
    response=crud.get_train(db)
    try:
        if response.detail:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=dict(response),
                headers={"WWW-Authenticate":"Bearer"}
            )
    except AttributeError:
        pass
    return response



@router.post("/add_trn",response_model=schemas.outTrain,status_code=201,tags=["Train"])
async def add_train(
    *,
    user:schemas.UserBase=Depends(dep.get_admin_details),
    train:schemas.Train=Body(...,description="post train details"),
    db:Session=Depends(get_db)
):
    response=crud.add_train(db=db,trn=train)
    try:
        if response.detail:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=dict(response),
                headers={"WWW-Authenticate":"Bearer"}
            )
    except AttributeError:
        pass
    return response


@router.delete("/rem_trn",response_model=schemas.outTrain,status_code=201,tags=["Train"])
async def remove_train(
    *,
    user:schemas.UserBase=Depends(dep.get_admin_details),
    train:schemas.Train_id=Body(...,description="train id"),
    db:Session=Depends(get_db)
):
    response=crud.remove_train(db=db,trn=train)
    try:
        if response.detail:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=dict(response),
                headers={"WWW-Authenticate": "Bearer"}
            )
    except AttributeError:
        pass
    return response


@router.patch("/mod_trn",response_model=schemas.outTrain,status_code=201,tags=["Train"])
async def modify_train(
    *,
    user:schemas.UserBase=Depends(dep.get_admin_details),
    train:schemas.upTrain=Body(...,description="modify train details "),
    db:Session=Depends(get_db)
):
    response=crud.modify_train(db=db,trn=train)
    try:
        if response.detail:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=dict(response),
                headers={"WWW-Authenticate": "Bearer"}
            )
    except AttributeError:
        pass
    return response

#----------------------------------------------------------------------------------

@router.get("/get_route",response_model=list[schemas.outRoutes],status_code=201,tags=["Routines"])
async def get_routes(
    *,
    user:schemas.UserBase=Depends(dep.get_admin_details),
    db:Session=Depends(get_db)
):
    response=crud.get_routes(db)
    try:
        if response.detail:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=dict(response),
                headers={"WWW-Authenticate":"Bearer"}
            )
    except AttributeError:
        pass
    return response

@router.post("/add_route",response_model=schemas.Routes,status_code=201,tags=["Routines"])
async def add_routes(
    *,
    user:schemas.UserBase=Depends(dep.get_admin_details),
    r:schemas.Routes=Body(...),
    db:Session=Depends(get_db)
):
    response=crud.add_routes(db=db,r=r)
    try:
        if response.detail:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=dict(response),
                headers={"WWW-Authenticate":"Bearer"}
            )
    except AttributeError:
        pass
    return response

@router.delete("/rem_route",response_model=schemas.outRoutes,status_code=201,tags=["Routines"])
async def remove_routes(
    *,
    user:schemas.UserBase=Depends(dep.get_admin_details),
    id:schemas.Route_id=Body(...),
    db:Session=Depends(get_db)
):
    response=crud.rem_route(db=db,id=id.id)
    
    if response.status=="failed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=dict(response),
            headers={"WWW-Authenticate": "Bearer"}
        )
    return response

@router.patch("/mod_route",response_model=schemas.outRoutes,status_code=201,tags=["Routines"])
async def modify_routes(
    *,
    user:schemas.UserBase=Depends(dep.get_admin_details),
    route:schemas.upRoute=Body(...),
    db:Session=Depends(get_db)
):
    response=crud.mod_route(db=db,r=route)
    
    if response.status=="failed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=dict(response),
            headers={"WWW-Authenticate": "Bearer"}
        )
    return response

