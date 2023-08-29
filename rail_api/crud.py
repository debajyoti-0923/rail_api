from sqlalchemy.orm import Session

from . import models
from . import schemas,dependencies,database
from passlib.context import CryptContext
import os

from sqlalchemy import or_,and_,join,func
from . import database

import json
from datetime import time,timedelta,datetime,date as dt
pwd_context=CryptContext(schemes=["bcrypt"],deprecated=["auto"])
rqstId=0
seatStat={0:"Waiting",1:"Confirm",2:"Canceled"}

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
        

def get_station(db:Session,stn:int=None):
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
    
    db.query(models.Train).filter(or_(
        models.Train.stops.like(f"{stn.id}-%"),
        models.Train.stops.like(f"%-{stn.id}-%"),
        models.Train.stops.like(f"%-{stn.id}"),
    )).update({"deprecated":True},synchronize_session=False)

    # for i in response:
    #     db.query(models.Train).filter(models.Train.id==i.id).update({"deprecated":True})
    #     db.query(models.Routine).filter(models.Routine.trainId==i.id).update({"deprecated":True})
    
    db.commit()
    return res

def modify_station(db:Session,stn:schemas.upStaion):
    res=get_station(db,stn.id)
    if res.status=="failed":
        return schemas.error(status="failed",detail="value doesn't exists")
    db.query(models.Station).filter(models.Station.id==stn.id).update(stn.model_dump(exclude_unset=True),synchronize_session=False)
    db.commit()
    db_stn=db.query(models.Station).filter(models.Station.id==stn.id).first()
    return schemas.outStation.model_validate(db_stn)

#----------------------------------------------------------------------

def get_train(db:Session,trn:int=None):
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
    
    if str(trn.src)!=trn.stops[0] or str(trn.des)!=trn.stops[-1] :
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
    # db.query(models.Routine).filter(models.Routine.trainId==trn.id).update({"deprecated":True})
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
   
    db.query(models.Train).filter(models.Train.id==trn.id).update(dbModel.model_dump(exclude_none=True),synchronize_session=False)
    db.commit()
    res=db.query(models.Train).filter(models.Train.id==trn.id).first()
    return schemas.outTrain.model_validate(res)

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

    try:    
        depTime=time(int(r.departure[:2]),int(r.departure[2:]))
    except ValueError:
        return schemas.error(status="failed",detail="bad values")

    # r.departure=depTime
    db_model=models.Routine(**r.model_dump())
    db_model.departure=depTime
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
    
    try:
        if r.departure:   
            depTime=time(int(r.departure[:2]),int(r.departure[2:]))
            r.departure=depTime
    except ValueError:
        return schemas.error(status="failed",detail="bad values")

    db.query(models.Routine).filter(models.Routine.id==r.id).update(r.model_dump(exclude_none=True),synchronize_session=False)
    db.commit()

    dbRoute=schemas.outRoutes.model_validate(dbRoute).model_dump()
    dbRoute.update(r.model_dump(exclude_none=True))

    return schemas.outRoutes.model_validate(dbRoute)

#--------------------------------------------------------------------------------
#book

def get_av_trains(db:Session,attr:schemas.avTrain):
    cDate=dt.today()
    if attr.date<cDate+timedelta(days=1) or attr.date>cDate+timedelta(days=14):
        return schemas.error(status="failed",detail="invalid date")
    d=attr.date.isoweekday()
    res=chk_staiton(db,[attr.src,attr.des])
    if res.status=="failed":
        return res
    response=db.query(
        models.Train.id,
        models.Train.name,
        models.Train.price,
        models.Train.speed,
        models.Train.mainQuota,
        models.Train.remQuota,
        models.Routine.departure,
        models.Train.src,
        models.Routine.id,
    ).join(models.Routine).filter(models.Routine.day==d).filter(models.Train.stops.like(f"%{attr.src}%-%{attr.des}%")).filter(models.Train.deprecated==0).all()
    
    dep_dist=db.query(models.Station.dist).filter(models.Station.id==attr.src).first()
    arr_dist=db.query(models.Station.dist).filter(models.Station.id==attr.des).first()
    dist=abs(dep_dist[0]-arr_dist[0])
    
    avTrns=[]
    for i in response:
        src_stn=db.query(models.Station.dist).filter(models.Station.id==i[7]).first()
        rlvDist=abs(src_stn[0]-dep_dist[0])

        pr=dist*i[2]
        absDep=datetime.combine(attr.date,i[6])
        dep=absDep+timedelta(hours=((rlvDist/i[3])))
        arr=dep+timedelta(hours=((dist/i[3])))

        res=schemas.resTrain(
            id=i[0],
            name=i[1],
            price=pr,
            speed=i[3],
            dist=dist,
            dep=dep,
            arr=arr,
            routeId=i[8],
            date=attr.date,
            quota=("main" if attr.src==i[7] else "remote")
        )

        avTrns.append(res)
    
    return avTrns

#change after creating booking tables
def get_seat_av(db:Session,data:schemas.seatAvl):
    res=chk_staiton(db,[data.src,data.des])
    if res.status=="failed":
        return res
    
    res=db.query(models.Inventory).filter(
        models.Inventory.rid==data.rId,
        models.Inventory.date==data.date
    ).first()

    if res is None:
        return schemas.error(status="failed",detail="invalid request")
    
    quota=(res.routine_.trains.src==data.src)
    
    if quota:
        r=schemas.resSeat(
            # invId=res.id,
            avl=0 if res.mainAvl<0 else res.mainAvl,
            wt=0 if res.mainAvl>=0 else abs(res.mainAvl)
        )
    else:
        r=schemas.resSeat(
            # invId=res.id,
            avl=0 if res.remAvl<0 else res.remAvl,
            wt=0 if res.remAvl>=0 else abs(res.remAvl)
        )
    return r

#-------------------------------------------------------------------

def transfer_if_av(db:Session,inv:models.Inventory,q:bool):
    if inv.canceled>0:
        wts=db.query(models.Tickets).filter(and_(
            models.Tickets.invId==inv.id,
            models.Tickets.quota==q,
            models.Tickets.status==0
        )).all()

        cans=db.query(models.Tickets).filter(and_(
            models.Tickets.invId==inv.id,
            models.Tickets.quota==q,
            models.Tickets.status==2
        )).all()

        cnt_delta=0

        for i in range(min(len(wts),len(cans))):
            db.query(models.Tickets).filter(models.Tickets.id==wts[i].id).update({"seatNo":cans[i].seatNo,"status":1})
            db.query(models.Tickets).filter(models.Tickets.id==cans[i].id).delete(synchronize_session=False)
            cnt_delta+=1
        if q:
            db.query(models.Inventory).filter(models.Inventory.id==inv.id).update({"mainAvl":inv.mainAvl+cnt_delta,"canceled":inv.canceled-cnt_delta})
        else:
            db.query(models.Inventory).filter(models.Inventory.id==inv.id).update({"remAvl":inv.remAvl+cnt_delta,"canceled":inv.canceled-cnt_delta})

        db.commit()
def add_ticket(db:Session,user:schemas.UserName,details:schemas.bookTickets):
    global rqstId
    res=chk_staiton(db,[details.src,details.des])
    if res.status=="failed":
        return res

    res=db.query(models.Inventory).filter(and_(
        models.Inventory.rid==details.rId,
        models.Inventory.date==details.date
    )).first()
    
    #ADDING TO TICKETS DB
    if res is None:
        return schemas.error(status="failed",detail="invalid request")
    quota=(res.routine_.trains.src==details.src)

    if details.numT!=len(details.names) or details.numT!=len(details.ages):
        return schemas.error(status="failed",detail="number of tickets and provided values doesn't match")
    
    dep_dist=db.query(models.Station.dist).filter(models.Station.id==details.src).first()
    arr_dist=db.query(models.Station.dist).filter(models.Station.id==details.des).first()
    src_dist=db.query(models.Station.dist).filter(models.Station.id==res.routine_.trains.src).first()
    dist=abs(dep_dist[0]-arr_dist[0])
    rlvDist=abs(src_dist[0]-dep_dist[0])

    absDep=datetime.combine(res.date,res.routine_.departure)
    dep=absDep+timedelta(hours=((rlvDist/res.routine_.trains.speed)))
    arr=dep+timedelta(hours=((dist/res.routine_.trains.speed)))

    pr=dist*res.routine_.trains.price
    cnt=db.query(func.count(models.Tickets.id)).first()
    
    if quota:
        avSeats=res.mainAvl
        startNo=(res.routine_.trains.mainQuota-res.mainAvl)+1
    else:
        avSeats=res.remAvl
        startNo=res.routine_.trains.mainQuota+(res.routine_.trains.remQuota-res.remAvl)+1

    

    dbModels:list[models.Tickets]=[]
    pnr=f"{res.routine_.trainId:04}{(rqstId):04}{user.id:03}"
    rqstId+=1
    cnt=0
    for i in range(min(details.numT,avSeats)):
        if details.names[i]=="" or details.ages[i]<=0:
            return schemas.error(status="failed",detail="Bad values for name or age")
        dbModel=models.Tickets(pnr=pnr,invId=res.id,src=details.src,dep=dep.time(),arr=arr.time(),des=details.des,dist=dist,price=pr,quota=quota,userId=user.id,name=details.names[i],age=details.ages[i],seatNo=startNo,status=1)
        dbModels.append(dbModel)
        startNo+=1
        cnt+=1

    for i in range(cnt,details.numT):
        dbModel=models.Tickets(pnr=pnr,invId=res.id,src=details.src,dep=dep.time(),arr=arr.time(),des=details.des,dist=dist,price=pr,quota=quota,userId=user.id,name=details.names[i],age=details.ages[i],status=0)
        dbModels.append(dbModel)
    db.add_all(dbModels)
    #MODIFYING INVENTORY
    if quota:
        db.query(models.Inventory).filter(
            models.Inventory.id==res.id
        ).update({"mainAvl":res.mainAvl-details.numT})
    else:
        db.query(models.Inventory).filter(
            models.Inventory.id==res.id
        ).update({"remAvl":res.remAvl-details.numT})

    db.commit()
    transfer_if_av(db,res,quota)

    return schemas.resPNR(pnr=pnr)

def get_tickets(db:Session,user:schemas.UserName):
    res=db.query(models.Tickets).filter(and_(
        models.Tickets.userId==user.id,
        models.Tickets.status!=2
        )).group_by(models.Tickets.pnr).all()
    
    tickets=[]
    for i in res:
        data=db.query(models.Tickets).filter(and_(
            models.Tickets.pnr==i.pnr,
            models.Tickets.status!=2
        ))
        psngr=[]
        
        for obj in data:
            pg=schemas.ticketEntity(
                id=obj.id,
                name=obj.name,
                age=obj.age,
                seatNo=obj.seatNo,
                status=seatStat[obj.status]
            )
            psngr.append(pg)

        res=schemas.Tickets(
            pnr=i.pnr,
            trainName=i.invs.routine_.trains.name,
            trianId=i.invs.routine_.trains.id,
            date=i.invs.date,
            src=get_station(db,i.src).name,
            des=get_station(db,i.des).name,
            dep=i.dep,
            arr=i.arr,
            passengers=psngr
        )
        tickets.append(res)
    return tickets

def get_pnr(db:Session,pnr:str):
    res=db.query(models.Tickets).filter(
        models.Tickets.pnr==pnr
    ).all()
    if res==[]:
        return schemas.error(status="failed",detail="invalid pnr")
    psngr=[]
    for obj in res:
        pg=schemas.ticketEntity(
            id=obj.id,
            name=obj.name,
            age=obj.age,
            seatNo=obj.seatNo,
            status=seatStat[obj.status]
        )
        psngr.append(pg)

    response=schemas.Tickets(
        pnr=pnr,
        trainName=res[0].invs.routine_.trains.name,
        trianId=res[0].invs.routine_.trains.id,
        date=res[0].invs.date,
        src=get_station(db,res[0].src).name,
        des=get_station(db,res[0].des).name,
        dep=res[0].dep,
        arr=res[0].arr,
        passengers=psngr
    )
    return response


def cancel_ticket(db:Session,tid:schemas.cancel_ticks):
    grp=db.query(models.Tickets).filter(models.Tickets.pnr==tid.pnr).first()
    
    if grp is None:
        return schemas.error(status="failed",detail="Wrong pnr")
    
    cnt_trn,cnt_del=0,0

    for i in tid.ids:
        res=db.query(models.Tickets).filter(models.Tickets.id==i).first()

        if res is None or res.pnr!=grp.pnr:
            return schemas.error(status="failed",detail="pnr-id mismatch")
            
        if res.status==0:
            db.query(models.Tickets).filter(models.Tickets.id==i).delete(synchronize_session=False)
            cnt_del+=1
        elif res.status==1:
            db.query(models.Tickets).filter(models.Tickets.id==i).update({"status":2})
            cnt_trn+=1
        
    if cnt_trn>0 or cnt_del>0:
        if grp.quota:
            db.query(models.Inventory).filter(models.Inventory.id==grp.invs.id).update({"mainAvl":grp.invs.mainAvl+cnt_del,"canceled":grp.invs.canceled+cnt_trn})
        else:
            db.query(models.Inventory).filter(models.Inventory.id==grp.invs.id).update({"remAvl":grp.invs.remAvl+cnt_del,"canceled":grp.invs.canceled+cnt_trn})

    db.commit()
    transfer_if_av(db,grp.invs,grp.quota)

    return schemas.ok()


#populate inventory
def populate():
    db=database.sessionlocal()
    db.query(models.Inventory).delete(synchronize_session=False)
    db.query(models.Tickets).delete(synchronize_session=False)

    currentDate=dt.today()
    # dates=[]
    for i in range(1,15):
        tDate=currentDate+timedelta(days=i)
        # dates.append(tDate)

        day=tDate.isoweekday()
        data=db.query(models.Routine).filter(models.Routine.day==day).all()
        for i in data:
            model=models.Inventory(
                rid=i.id,
                date=tDate,
                mainAvl=i.trains.mainQuota,
                remAvl=i.trains.remQuota,
                canceled=0
            )
            db.add(model)

    db.commit()

def generate_inv():
    db=database.sessionlocal()

    currentDate=dt.today()
    
    tDate=currentDate+timedelta(days=14)

    day=tDate.isoweekday()
    data=db.query(models.Routine).filter(models.Routine.day==day).all()

    invModels=[]
    for i in data:
        model=models.Inventory(
            rid=i.id,
            date=tDate,
            mainAvl=i.trains.mainQuota,
            remAvl=i.trains.remQuota,
            canceled=0
        )
        invModels.append(model)

    db.add_all(invModels)
    db.commit()

def generate_chart():
    db=database.sessionlocal()

    currentDate=dt.today()

    invs=db.query(models.Inventory).filter(models.Inventory.date==currentDate).all()


    for i in invs:
        folder_path=r"rail_api\logs\{0}".format(currentDate)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        relative=r"rail_api\logs\{0}\RID-{1}.txt".format(currentDate,i.rid)
        
        with open(relative,"w") as file:
            ticks=i.tickets
            json_str=""
            for z in ticks:
                dep_str=z.dep.strftime("%I:%M %p")
                arr_str=z.arr.strftime("%I:%M %p")
                data={
                    "id":z.id,
                    "pnr":z.pnr,
                    "invId":z.invId,
                    "src":z.src,
                    "des":z.des,
                    "dep":dep_str,
                    "arr":arr_str,
                    "dist":z.dist,
                    "price":z.price,
                    "quota":z.quota,
                    "userId":z.userId,
                    "name":z.name,
                    "age":z.age,
                    "seatNo":z.seatNo,
                    "status":z.status
                }
                json_data=json.dumps(data)
                json_str+=json_data+"\n"
                # print(data)
            file.write(json_str)

    db.query(models.Inventory).filter(models.Inventory.date==currentDate).delete(synchronize_session=False)
    db.commit()





