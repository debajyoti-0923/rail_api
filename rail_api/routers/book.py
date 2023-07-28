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
get src dest day get bus
'''

@router.post("/get_trn",status_code=201)
async def get_trains(
    *,
    attr:schemas.avTrain=Body(...),
    db:Session=Depends(get_db)
):
    response=crud.get_av_trains(db,attr)
    return response