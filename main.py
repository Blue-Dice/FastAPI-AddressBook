"""FastAPI Address Book Application"""

from typing import List
from fastapi import FastAPI, Query, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from geopy.distance import geodesic

Base = declarative_base()

class Address(Base):
    """
    Model class for addresses.
    
    Attributes:
        __tablename__ (str): The name of the table in the database.
        id (int): The unique identifier for an address.
        name (str): The name associated with the address.
        latitude (float): The latitude coordinate of the address.
        longitude (float): The longitude coordinate of the address.
    """
    __tablename__ = 'addresses'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)

class AddressCreate(BaseModel):
    """
    Model class for creating addresses.
    
    Attributes:
        name (str): The name associated with the address.
        latitude (float): The latitude coordinate of the address.
        longitude (float): The longitude coordinate of the address.
    """
    name: str
    latitude: float
    longitude: float

class AddressUpdate(BaseModel):
    """
    Model class for updating addresses.
    
    Attributes:
        name (str, optional): The updated name associated with the address.
        latitude (float, optional): The updated latitude coordinate of the address.
        longitude (float, optional): The updated longitude coordinate of the address.
    """
    name: str
    latitude: float
    longitude: float

class AddressInDB(AddressCreate):
    """
    Model class for addresses stored in the database.
    
    Attributes:
        id (int): The unique identifier for an address.
        name (str): The name associated with the address.
        latitude (float): The latitude coordinate of the address.
        longitude (float): The longitude coordinate of the address.
    """
    id: int

class DistanceQuery(BaseModel):
    """
    Model class for distance query parameters.
    
    Attributes:
        latitude (float): The latitude coordinate of the center point.
        longitude (float): The longitude coordinate of the center point.
        distance (float): The distance in kilometers.
    """
    latitude: float
    longitude: float
    distance: float

app = FastAPI()

SQLALCHEMY_DATABASE_URL = "sqlite:///./addresses.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Function to get a database session.
    
    Yields:
        Session: The database session object.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/addresses/", response_model=AddressInDB)
def create_address(address: AddressCreate, db: Session = Depends(get_db)):
    """
    Endpoint to create a new address.
    
    Args:
        address (AddressCreate): The address data to be created.
        db (Session, optional): The database session dependency. Defaults to Depends(get_db).
    
    Returns:
        AddressInDB: The created address with its ID.
    """
    db_address = Address(**address.model_dump())
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address

@app.put("/addresses/{address_id}", response_model=AddressInDB)
def update_address(
    address_id: int,
    address_update: AddressUpdate,
    db: Session = Depends(get_db)
):
    """
    Endpoint to update an existing address.
    
    Args:
        address_id (int): The ID of the address to be updated.
        address_update (AddressUpdate): The updated address data.
        db (Session, optional): The database session dependency. Defaults to Depends(get_db).
    
    Returns:
        AddressInDB: The updated address.
    """
    db_address = db.query(Address).filter(Address.id == address_id).first()
    if db_address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    for field, value in address_update.model_dump().items():
        if value is not None:
            setattr(db_address, field, value)
    db.commit()
    db.refresh(db_address)
    return db_address

@app.delete("/addresses/{address_id}", response_model=AddressInDB)
def delete_address(address_id: int, db: Session = Depends(get_db)):
    """
    Endpoint to delete an existing address.
    
    Args:
        address_id (int): The ID of the address to be deleted.
        db (Session, optional): The database session dependency. Defaults to Depends(get_db).
    
    Returns:
        AddressInDB: The deleted address.
    """
    db_address = db.query(Address).filter(Address.id == address_id).first()
    if db_address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    db.delete(db_address)
    db.commit()
    return db_address

@app.get("/addresses/distance/", response_model=List[AddressInDB])
def get_addresses_within_distance(
        latitude: float = Query(..., description="Latitude of the center point"),
        longitude: float = Query(..., description="Longitude of the center point"),
        distance: float = Query(..., description="Distance in kilometers"),
        db: Session = Depends(get_db)
    ):
    """
    Endpoint to retrieve addresses within a given distance from a specified location.
    
    Args:
        latitude (float): Latitude coordinate of the center point.
        longitude (float): Longitude coordinate of the center point.
        distance (float): Distance in kilometers.
        db (Session, optional): The database session dependency. Defaults to Depends(get_db).
    
    Returns:
        List[AddressInDB]: A list of addresses within the specified distance of the given location.
    """
    addresses = db.query(Address).all()
    within_distance = []
    location = (latitude, longitude)
    for address in addresses:
        address_location = (address.latitude, address.longitude)
        if geodesic(location, address_location).kilometers <= distance:
            within_distance.append(address)
    return within_distance
