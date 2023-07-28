from sqlalchemy.orm import relationship,Mapped,mapped_column
from sqlalchemy import ForeignKey
from .database import base

from datetime import time


class User(base):
    __tablename__="users"

    id:Mapped[int]=mapped_column(primary_key=True)
    first_name:Mapped[str]=mapped_column(nullable=False)
    last_name:Mapped[str]=mapped_column(nullable=False)
    username:Mapped[str]=mapped_column(nullable=False,unique=True)
    email:Mapped[str]=mapped_column(nullable=False,unique=True)
    hashed_password:Mapped[str]=mapped_column(nullable=False)
    admin:Mapped[bool]


class Station(base):
    __tablename__="station"

    id:Mapped[str]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(nullable=False)
    abv:Mapped[str]=mapped_column(nullable=False)
    dist:Mapped[int]=mapped_column(nullable=False)
    

class Train(base):
    __tablename__="train"

    id:Mapped[str]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(nullable=False)
    src:Mapped[str]=mapped_column(nullable=False)
    des:Mapped[str]=mapped_column(nullable=False)
    stops:Mapped[str]=mapped_column(nullable=False)
    price:Mapped[float]=mapped_column(nullable=False)
    mainQuota:Mapped[int]=mapped_column(nullable=False)
    remQuota:Mapped[int]=mapped_column(nullable=False)
    speed:Mapped[int]=mapped_column(nullable=False)
    deprecated:Mapped[bool]=mapped_column(default=False)
    routines:Mapped[list["Routine"]]=relationship(back_populates="trains")


class Routine(base):
    __tablename__="routine"

    id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
    trainId:Mapped[str]=mapped_column(ForeignKey("train.id"))
    day:Mapped[int]=mapped_column(nullable=False)
    departure:Mapped[str]=mapped_column(nullable=False)
    deprecated:Mapped[bool]=mapped_column(default=False)
    trains:Mapped["Train"]=relationship(back_populates="routines")

#inital booking inventory
#cancelled inventory

'''
prebooking window 1 month
date trainId mainquota remqouta 

if mainquota full -> waiting if cancelled inv => (waiting -> confirm)
                  -> waiting if chart prepared and remquota free => waiting -> confirm
if remquota full -> waiting if cancelled inv => waiting -> confirm
                 -> waiting if chart prepared and mainquota free => waiting -> congirm
'''


