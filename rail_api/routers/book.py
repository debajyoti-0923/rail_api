from fastapi import APIRouter,Depends,HTTPException,Body,status

from .. import crud
from .. import schemas
from ..dependencies import get_db,get_user_details
from .. import dependencies as dep
from sqlalchemy.orm import Session


router=APIRouter(
    prefix="/book",
    tags=["book"],
    responses={404:{"description":"Not found"}}
)
'''
get src dest day get train
'''

@router.post("/avl_trn",response_model=list[schemas.resTrain],status_code=201)
async def get_trains(
    *,
    attr:schemas.avTrain=Body(...),
    db:Session=Depends(get_db)
):
    response=crud.get_av_trains(db,attr)
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


# @router.post("/test")
# async def add_inv(
#     *,
#     db:Session=Depends(get_db),
#     data:schemas.inv=Body(...)
# ):
#     crud.testinv(db)

@router.post("/avl_seat")
async def seat_status(
    *,
    db:Session=Depends(get_db),
    data:schemas.seatAvl=Body(...)
):
    response=crud.get_seat_av(db,data)
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