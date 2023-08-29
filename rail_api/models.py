from sqlalchemy.orm import relationship,Mapped,mapped_column
from sqlalchemy import ForeignKey
from .database import base

from datetime import time,date as dt


class User(base):
    __tablename__="users"

    id:Mapped[int]=mapped_column(primary_key=True)
    first_name:Mapped[str]=mapped_column(nullable=False)
    last_name:Mapped[str]=mapped_column(nullable=False)
    username:Mapped[str]=mapped_column(nullable=False,unique=True)
    email:Mapped[str]=mapped_column(nullable=False,unique=True)
    hashed_password:Mapped[str]=mapped_column(nullable=False)
    admin:Mapped[bool]
    tickets:Mapped[list["Tickets"]]=relationship(back_populates="user")


class Station(base):
    __tablename__="station"

    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(nullable=False)
    abv:Mapped[str]=mapped_column(nullable=False)
    dist:Mapped[int]=mapped_column(nullable=False)
    

class Train(base):
    __tablename__="train"

    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(nullable=False)
    src:Mapped[int]=mapped_column(nullable=False)
    des:Mapped[int]=mapped_column(nullable=False)
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
    trainId:Mapped[int]=mapped_column(ForeignKey("train.id"))
    day:Mapped[int]=mapped_column(nullable=False)
    departure:Mapped[time]=mapped_column(nullable=False)
    # deprecated:Mapped[bool]=mapped_column(default=False)
    trains:Mapped["Train"]=relationship(back_populates="routines")
    invs:Mapped[list["Inventory"]]=relationship(back_populates="routine_")

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



class Inventory(base):
    __tablename__="inventory"

    id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
    rid:Mapped[int]=mapped_column(ForeignKey("routine.id"))
    date:Mapped[dt]=mapped_column()
    mainAvl:Mapped[int]=mapped_column(nullable=False)
    remAvl:Mapped[int]=mapped_column(nullable=False)
    canceled:Mapped[int]=mapped_column(nullable=False)
    routine_:Mapped["Routine"]=relationship(back_populates="invs")
    tickets:Mapped[list["Tickets"]]=relationship(back_populates="invs")


class Tickets(base):
    __tablename__="tickets"

    id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
    pnr:Mapped[str]=mapped_column(nullable=False)
    invId:Mapped[int]=mapped_column(ForeignKey("inventory.id"))
    src:Mapped[int]=mapped_column(nullable=False)
    des:Mapped[int]=mapped_column(nullable=False)
    dep:Mapped[time]=mapped_column(nullable=False)
    arr:Mapped[time]=mapped_column(nullable=False)
    dist:Mapped[int]=mapped_column(nullable=False)
    price:Mapped[int]=mapped_column(nullable=False)
    quota:Mapped[bool]=mapped_column(nullable=False)
    userId:Mapped[int]=mapped_column(ForeignKey("users.id"))
    name:Mapped[str]=mapped_column(nullable=False)
    age:Mapped[int]=mapped_column(nullable=False)
    seatNo:Mapped[int]=mapped_column(nullable=True)
    status:Mapped[int]=mapped_column(nullable=False)   #Confirm-1 ; W-0 ; cancel-2
    invs:Mapped["Inventory"]=relationship(back_populates="tickets")
    user:Mapped["User"]=relationship(back_populates="tickets")


#     confirms:Mapped["Confirm"]=relationship(back_populates="ticket")
#     waitings:Mapped["Waiting"]=relationship(back_populates="ticket")
#     cancels:Mapped["Cancel"]=relationship(back_populates="ticket")


# class Confirm(base):
#     __tablename__="confirm"

#     id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
#     tId:Mapped[int]=mapped_column(ForeignKey("tickets.id"))
#     pnr:Mapped[str]=mapped_column(nullable=False)
#     ticket:Mapped["Tickets"]=relationship(back_populates="confirms")

# class Waiting(base):
#     __tablename__="waiting"

#     id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
#     tId:Mapped[int]=mapped_column(ForeignKey("tickets.id"))
#     pnr:Mapped[str]=mapped_column(nullable=False)
#     ticket:Mapped["Tickets"]=relationship(back_populates="waitings")
    
# class Cancel(base):
#     __tablename__="cancel"

#     id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
#     tId:Mapped[int]=mapped_column(ForeignKey("tickets.id"))
#     pnr:Mapped[str]=mapped_column(nullable=False)
#     ticket:Mapped["Tickets"]=relationship(back_populates="cancels")