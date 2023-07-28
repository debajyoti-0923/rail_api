from sqlalchemy.orm import Session

from . import models
from . import schemas,dependencies
from passlib.context import CryptContext

from sqlalchemy import or_,and_,join
from . import database

import datetime
pwd_context=CryptContext(schemes=["bcrypt"],deprecated=["auto"])

def chk_time(t:str):
    if int(t[:2])>=0 and int(t[:2])<24 and int(t[2:])>=0 and int(t[2:])<60:
        return True
    else:
        return False
    
#------------------------------------------------------------
def get_user(db:Session,username:str=None,email:str=None):
    if username is not None:
        return db.query(models.User).filter(models.User.username==username).first()
    elif email is not None:
        return db.query(models.User).filter(models.User.email==email).first()
    else:
        return None
    
def create_user(db:Session,user:schemas.UserCreate):
    db_user=models.User(first_name=user.first_name,last_name=user.last_name,username=user.username,email=user.email,hashed_password=pwd_context.hash(user.password),admin=dependencies.authenticate_admin(user.admin_pass))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

#------------------------------------------------
def chk_staiton(db:Session,stns:list):
    for i in stns:
        res=get_station(db,i)
        if res.status=="failed":
            return schemas.error(status="failed",detail="id doesn't exists")
    return schemas.ok()
        

def get_station(db:Session,stn:str=None):
    if stn is None:
        data=db.query(models.Station).all()
        if data==[]:
            return schemas.error(status="failed",detail="value doesn't exists")
        return data
    else:
        data=db.query(models.Station).filter(models.Station.id==stn).first()
        if data is None:
            return schemas.error(status="failed",detail="value doesn't exists")
        return schemas.outStation.model_validate(data)

def create_station(db:Session,stn:schemas.Station):
    res=get_station(db,stn.id)
    if res.status=="ok":
        return schemas.error(status="failed",detail="value already exists")
    db_stn=models.Station(id=stn.id,name=stn.name,abv=stn.abv,dist=stn.dist)
    db.add(db_stn)
    db.commit()
    db.refresh(db_stn)
    return schemas.outStation.model_validate(stn)

def remove_station(db:Session,stn:schemas.Station_id):
    res=get_station(db,stn.id)
    if res.status=="failed":
        return schemas.error(status="failed",detail="value doesn't exists")
    db.query(models.Station).filter(models.Station.id==stn.id).delete(synchronize_session=False)
    response=db.query(models.Train).filter(or_(
        models.Train.stops.like(f"{stn.id}-%"),
        models.Train.stops.like(f"%-{stn.id}-%"),
        models.Train.stops.like(f"%-{stn.id}"),
    )).all()

    for i in response:
        db.query(models.Train).filter(models.Train.id==i.id).update({"deprecated":True})
        db.query(models.Routine).filter(models.Routine.trainId==i.id).update({"deprecated":True})
    
    db.commit()
    return res

def modify_station(db:Session,stn:schemas.upStaion):
    res=get_station(db,stn.id)
    if res.status=="failed":
        return schemas.error(status="failed",detail="value doesn't exists")
    db.query(models.Station).filter(models.Station.id==stn.id).update(stn.model_dump(exclude_unset=True))
    db.commit()
    db_stn=db.query(models.Station).filter(models.Station.id==stn.id).first()
    return schemas.outStation.model_validate(db_stn)

#----------------------------------------------------------------------

def get_train(db:Session,trn:str=None):
    if trn is None:
        data=db.query(models.Train).all()
        if data==[]:
            return schemas.error(status="failed",detail="value doesn't exists")
        return data
    else:
        data=db.query(models.Train).filter(models.Train.id==trn).first()
        if data is None:
            return schemas.error(status="failed",detail="value doesn't exists")
 
        return schemas.outTrain.model_validate(data)
    
def add_train(db:Session,trn:schemas.Train):
    res=get_train(db,trn.id)
    if res.status=="ok":
        return schemas.error(status="failed",detail="value already exists")
    
    if trn.src!=trn.stops[0] or trn.des!=trn.stops[-1] :
        return schemas.error(status="failed",detail="bad values")
    
    res=chk_staiton(db,trn.stops)
    if res.status=="failed":
        return res
    
    upStr='-'.join(trn.stops)

    db_trn=models.Train(id=trn.id,name=trn.name,src=trn.src,des=trn.des,stops=upStr,price=trn.price,mainQuota=trn.mainQuota,remQuota=trn.remQuota,speed=trn.speed)
    db.add(db_trn)
    db.commit()
    db.refresh(db_trn)
    return schemas.outTrain.model_validate(db_trn)

def remove_train(db:Session,trn:schemas.Train_id):
    res=get_train(db,trn.id)
    if res.status=="failed":
        return schemas.error(status="failed",detail="value doesn't exists")
    db.query(models.Train).filter(models.Train.id==trn.id).delete(synchronize_session=False)
    db.query(models.Routine).filter(models.Routine.trainId==trn.id).update({"deprecated":True})
    db.commit()
    return res
    
def modify_train(db:Session,trn:schemas.upTrain):
    res=get_train(db,trn.id)

    if res.status=="failed":
        return schemas.error(status="failed",detail="value doesn't exists")
    data=trn.model_dump()

    try:
        db_trn=db.query(models.Train).filter(models.Train.id==trn.id).first()

        if data["stops"]:
            res=chk_staiton(db,data["stops"])
            if res.status=="failed":
                return res
            if db_trn.src!=data["stops"][0] or db_trn.des!=data["stops"][-1]:
                return schemas.error(status="failed",detail="bad values")
            data["stops"]='-'.join(data["stops"])

    except :
        pass
    
    dbModel=schemas.inTrain.model_validate(data)
   
    db.query(models.Train).filter(models.Train.id==trn.id).update(dbModel.model_dump(exclude_none=True))
    db.commit()
    
    return schemas.outTrain.model_validate(dbModel)

#------------------------------------------------------------------------------------------

def get_routes(db:Session)->list[schemas.outRoutes]:
    res=db.query(models.Routine).all()
    
    if res==[]:
        return schemas.error(status="failed",detail="value doesn't exists")
    return res

def get_route(db:Session,id:int):
    res=db.query(models.Routine).filter(models.Routine.id==id).first()  
    if res is None:
        return schemas.error(status="failed",detail="value doesn't exists")
    return schemas.outRoutes.model_validate(res)

def add_routes(db:Session,r:schemas.Routes):
    res=get_train(db,r.trainId)
    if res.status=="failed":
        return res
    if r.day not in (1,2,3,4,5,6,7):
        return schemas.error(status="failed",detail="bad values")

    db_model=models.Routine(**r.model_dump())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)

    return r

def rem_route(db:Session,id:int):
    res=get_route(db,id)
    if res.status=="failed":
        return res
    db.query(models.Routine).filter(models.Routine.id==id).delete(synchronize_session=False)
    db.commit()
    return res

def mod_route(db:Session,r:schemas.upRoute):
    dbRoute=db.query(models.Routine).filter(models.Routine.id==r.id).first()
    if dbRoute is None:
        return schemas.error(status="failed",detail="bad values")
    
    res=get_train(db=db,trn=dbRoute.trainId)
    if res.status=="failed":
        return res
    if r.day is not None and r.day not in (1,2,3,4,5,6,7):
        return schemas.error(status="failed",detail="bad values")
    db.query(models.Routine).filter(models.Routine.id==r.id).update(r.model_dump(exclude_none=True))
    db.commit()

    dbRoute=schemas.outRoutes.model_validate(dbRoute).model_dump()
    dbRoute.update(r.model_dump(exclude_none=True))

    return schemas.outRoutes.model_validate(dbRoute)

#--------------------------------------------------------------------------------
#book

def get_av_trains(db:Session,attr:schemas.avTrain):
    # avTrains=db.query(models.Train).filter(models.Train.stops.like(f"%{attr.src}%-%{attr.des}%")).all()
    d=attr.date.isoweekday()

    response=db.query(models.Train).join(models.Routine).filter(models.Routine.day==d).filter(models.Train.stops.like(f"%{attr.src}%-%{attr.des}%")).all()
    
    # for i in response:
    #     print(i.name,i.id)

    return response

# -- SQLite
# SELECT * FROM train INNER JOIN routine ON train.id==routine.trainId WHERE day=1 AND (stops LIKE "%11%")



