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
    id:str=Field("00")
    name:str=Field(...)
    abv:str=Field(...)
    dist:int=Field(...)


class outStation(BaseModel):
    status:str=Field("ok")
    id:str=Field("00")
    name:str=Field(...)
    abv:str=Field(...)
    dist:int=Field(...)

    class Config:
        from_attributes=True


class Station_id(BaseModel):
    id:str=Field("00")

class upStaion(BaseModel):
    id:Optional[str]=Field("00")
    name:Optional[str]=Field(None)
    abv:Optional[str]=Field(None)
    dist:Optional[int]=Field(None)

#---------------------------------------------------------
#Trains

class Train(BaseModel):
    id:str=Field("0000")
    name:str=Field(...)
    src:str=Field(...)
    des:str=Field(...)
    stops:list[str]=Field(...)
    price:float=Field(0)
    mainQuota:int=Field(80)
    remQuota:int=Field(20)
    speed:int=Field(60)

class outTrain(BaseModel):
    status:str=Field("ok")
    id:str=Field("0000")
    name:str=Field(...)
    src:str=Field(...)
    des:str=Field(...)
    stops:str=Field(...)
    price:float=Field(...)
    mainQuota:int=Field(...)
    remQuota:int=Field(...)
    speed:int=Field(...)
    deprecated:int=Field(...)
    
    class Config:
        from_attributes=True


class Train_id(BaseModel):
    id:str=Field("0000")

class baseTrain(BaseModel):
    id:str=Field("0000")
    name:Optional[str]=Field(None)
    src:Optional[str]=Field(None)
    des:Optional[str]=Field(None)
    price:Optional[float]=Field(None)
    mainQuota:Optional[int]=Field(None)
    remQuota:Optional[int]=Field(None)
    speed:Optional[int]=Field(None)
    deprecated:int=Field(0)

    class Config:
        from_attributes=True

class upTrain(baseTrain):
    stops:Optional[list[str]]=Field(None)

class inTrain(baseTrain):
    stops:Optional[str]=Field(None)


#----------------------------------------

class Routes(BaseModel):
    trainId:str=Field("0000")
    day:int=Field(1)
    departure:str=Field("0000")

class outRoutes(BaseModel):
    status:str=Field("ok")
    id:int=Field(...)
    trainId:str=Field(...)
    day:int=Field(1)
    departure:datetime.time=Field(...)
    # deprecated:bool=Field(...)

    class Config:
        from_attributes=True

    
class Route_id(BaseModel):
    id:int=Field(...)

class upRoute(BaseModel):
    id:int=Field(...)
    trainId:Optional[str]=Field(None)
    day:Optional[int]=Field(None)
    departure:Optional[str]=Field(None)
    # deprecated:Optional[bool]=Field(None)

#-----------------------------------------------

class avTrain(BaseModel):
    src:str=Field(...)
    des:str=Field(...)
    date:datetime.date=Field(...)

class resTrain(BaseModel):
    status:str=Field("ok")
    id:str=Field(...)
    name:str=Field(...)
    price:float=Field(...)
    speed:float=Field(...)
    dist:float=Field(...)
    dep:datetime.datetime=Field(...)
    arr:datetime.datetime=Field(...)
    routeId:int=Field(...)
    date:datetime.date=Field(...)
    quota:bool=Field(...)


class seatAvl(BaseModel):
    rId:int=Field(...)
    date:datetime.date=Field(...)
    quota:bool=Field(...)

class resSeat(BaseModel):
    avl:int=Field(...)
    wt:int=Field(...)


#------------------------------------------------------

class bookTickets(BaseModel):
    rId:int=Field(...)
    date:datetime.date=Field(...)
    src:str=Field(...)
    des:str=Field(...)
    numT:int=Field(...)
    names:list[str]=Field(...)
    ages:list[int]=Field(...)
    quota:bool=Field(...)

class resPNR(BaseModel):
    status:str=Field("OK")
    pnr:str=Field(...)
