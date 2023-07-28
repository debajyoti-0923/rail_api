from fastapi import APIRouter,Depends,HTTPException
from .. import schemas
from ..dependencies import get_db,get_user_details

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