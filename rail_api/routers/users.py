from fastapi import APIRouter,Depends,HTTPException,Body
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
    res=crud.add_ticket(db,user,details)
    return res

@router.get("/getckt",status_code=201)
async def get_tickets(
    user:schemas.UserName=Depends(get_user_details),
    db:Session=Depends(get_db)
):
    res=crud.get_tickets(db,user)
    return res

