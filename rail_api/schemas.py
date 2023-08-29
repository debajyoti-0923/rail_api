from pydantic import BaseModel,Field,EmailStr
from typing import Optional
import datetime
##user


class UserName(BaseModel):
    id:int=Field(None)
    username:str=Field(...,description="username",max_length=20)

class UserEmail(UserName):
    email:EmailStr=Field(...,description="email")

class UserBase(UserEmail):
    first_name:str=Field(...,description="first name")
    last_name:str=Field(...,description="last name")

class UserCreate(UserBase):
    password:str=Field(...,min_length=8)
    admin_pass:str=Field(None)


class Token(BaseModel):
    access_token:str
    token_type:str

class TokenData(BaseModel):
    username:str
#---------------------------------------------------------
#errors

class error(BaseModel):
    status:str
    detail:str

class ok(BaseModel):
    status:str=Field("ok")

#---------------------------------------------------------
#stations

class Station(BaseModel):
    id:int=Field(0)
    name:str=Field(...)
    abv:str=Field(...)
    dist:int=Field(...)


class outStation(BaseModel):
    status:str=Field("ok")
    id:int=Field(0)
    name:str=Field(...)
    abv:str=Field(...)
    dist:int=Field(...)

    class Config:
        from_attributes=True


class Station_id(BaseModel):
    id:int=Field(0)

class upStaion(BaseModel):
    id:Optional[int]=Field(0)
    name:Optional[str]=Field(None)
    abv:Optional[str]=Field(None)
    dist:Optional[int]=Field(None)

#---------------------------------------------------------
#Trains

class Train(BaseModel):
    id:int=Field(0)
    name:str=Field(...)
    src:int=Field(...)
    des:int=Field(...)
    stops:list[int]=Field(...)
    price:float=Field(0)
    mainQuota:int=Field(80)
    remQuota:int=Field(20)
    speed:int=Field(60)

class outTrain(BaseModel):
    status:str=Field("ok")
    id:int=Field(0)
    name:str=Field(...)
    src:int=Field(...)
    des:int=Field(...)
    stops:str=Field(...)
    price:float=Field(...)
    mainQuota:int=Field(...)
    remQuota:int=Field(...)
    speed:int=Field(...)
    deprecated:int=Field(...)
    
    class Config:
        from_attributes=True


class Train_id(BaseModel):
    id:int=Field(0)

class baseTrain(BaseModel):
    id:int=Field(0)
    name:Optional[str]=Field(None)
    src:Optional[int]=Field(None)
    des:Optional[int]=Field(None)
    price:Optional[float]=Field(None)
    mainQuota:Optional[int]=Field(None)
    remQuota:Optional[int]=Field(None)
    speed:Optional[int]=Field(None)
    deprecated:int=Field(0)

    class Config:
        from_attributes=True

class upTrain(baseTrain):
    stops:Optional[list[int]]=Field(None)

class inTrain(baseTrain):
    stops:Optional[str]=Field(None)


#----------------------------------------

class Routes(BaseModel):
    trainId:int=Field(0)
    day:int=Field(1)
    departure:str=Field("0000")

class outRoutes(BaseModel):
    status:str=Field("ok")
    id:int=Field(...)
    trainId:int=Field(...)
    day:int=Field(1)
    departure:datetime.time=Field(...)
    # deprecated:bool=Field(...)

    class Config:
        from_attributes=True

    
class Route_id(BaseModel):
    id:int=Field(...)

class upRoute(BaseModel):
    id:int=Field(...)
    trainId:Optional[int]=Field(None)
    day:Optional[int]=Field(None)
    departure:Optional[str]=Field(None)
    # deprecated:Optional[bool]=Field(None)

#-----------------------------------------------

class avTrain(BaseModel):
    src:int=Field(...)
    des:int=Field(...)
    date:datetime.date=Field(...)

class resTrain(BaseModel):
    status:str=Field("ok")
    id:int=Field(...)
    name:str=Field(...)
    price:float=Field(...)
    speed:float=Field(...)
    dist:float=Field(...)
    dep:datetime.datetime=Field(...)
    arr:datetime.datetime=Field(...)
    routeId:int=Field(...)
    date:datetime.date=Field(...)
    quota:str=Field(...)


class seatAvl(BaseModel):
    rId:int=Field(...)
    date:datetime.date=Field(...)
    src:int=Field(...)
    des:int=Field(...)


class resSeat(BaseModel):
    # invId:int=Field(...)
    avl:int=Field(...)
    wt:int=Field(...)


#------------------------------------------------------

class bookTickets(BaseModel):
    # invId:int=Field(...)
    rId:int=Field(...)
    date:datetime.date=Field(...)
    src:int=Field(...)
    des:int=Field(...)
    numT:int=Field(...)
    names:list[str]=Field(...)
    ages:list[int]=Field(...)

class resPNR(BaseModel):
    status:str=Field("OK")
    pnr:str=Field(...)

class ticketEntity(BaseModel):
    id:int
    name:str
    age:int
    seatNo:int|None=None
    status:str


class Tickets(BaseModel):
    pnr:str
    trainName:str
    trianId:int
    date:datetime.date
    src:str
    des:str
    dep:datetime.time
    arr:datetime.time
    passengers:list[ticketEntity]

class cancel_ticks(BaseModel):
    pnr:str
    ids:list[int]
