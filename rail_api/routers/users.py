from fastapi import APIRouter,Depends,HTTPException,Body,status
from .. import schemas,crud
from ..dependencies import get_db,get_user_details
from sqlalchemy.orm import Session

router=APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404:{"description":"Not found"}}
)

'''
authenticate
user info
user active tickets
user past tickets
'''

@router.get("/info",response_model=schemas.UserBase,status_code=201)
async def get_user_info(
    user:schemas.UserBase=Depends(get_user_details)
):
    return user


@router.post("/book")
async def book_ticket(
    *,
    details:schemas.bookTickets=Body(...),
    user:schemas.UserName=Depends(get_user_details),
    db:Session=Depends(get_db)
):
    response=crud.add_ticket(db,user,details)
    try:
        if response.status=="failed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=dict(response),
                headers={"WWW-Authenticate": "Bearer"}
            )
    except AttributeError:
        pass
    return response

@router.get("/getckt",status_code=201)
async def get_tickets(
    user:schemas.UserName=Depends(get_user_details),
    db:Session=Depends(get_db)
):
    response=crud.get_tickets(db,user)
    try:
        if response.status=="failed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=dict(response),
                headers={"WWW-Authenticate": "Bearer"}
            )
    except AttributeError:
        pass
    return response


@router.post("/cancel")
async def cancel_ticket(
    *,
    user:schemas.UserName=Depends(get_user_details),
    details:schemas.cancel_ticks=Body(...),
    db:Session=Depends(get_db)
):
    response=crud.cancel_ticket(db,details)
    try:
        if response.status=="failed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=dict(response),
                headers={"WWW-Authenticate": "Bearer"}
            )
    except AttributeError:
        pass
    return response


