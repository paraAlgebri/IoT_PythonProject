from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, Path
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import os

# Database configurations
DATABASE_USER = os.getenv("POSTGRES_USER", "postgres")
DATABASE_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
DATABASE_HOST = os.getenv("POSTGRES_HOST", "db")
DATABASE_PORT = os.getenv("POSTGRES_PORT", "5432")
DATABASE_NAME = os.getenv("POSTGRES_DB", "postgres")

DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ProcessedAgentDataInDB(Base):
    __tablename__ = "processed_agent_data"

    id = Column(Integer, primary_key=True, index=True)
    road_state = Column(String, nullable=False)
    x = Column(Float)
    y = Column(Float)
    z = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)
    timestamp = Column(DateTime)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Pydantic models
class Accelerometer(BaseModel):
    x: float
    y: float
    z: float


class GPS(BaseModel):
    latitude: float
    longitude: float


class AgentData(BaseModel):
    accelerometer: Accelerometer
    gps: GPS
    timestamp: int


class ProcessedAgentData(BaseModel):
    road_state: str
    agent_data: AgentData


class ProcessedAgentDataUpdate(BaseModel):
    road_state: Optional[str] = None
    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timestamp: Optional[int] = None


app = FastAPI()


@app.post("/processed_agent_data/")
async def create_data(data: ProcessedAgentData, db: Session = Depends(get_db)):
    # Перетворення Unix timestamp у datetime
    timestamp = datetime.fromtimestamp(data.agent_data.timestamp)

    db_item = ProcessedAgentDataInDB(
        road_state=data.road_state,
        x=data.agent_data.accelerometer.x,
        y=data.agent_data.accelerometer.y,
        z=data.agent_data.accelerometer.z,
        latitude=data.agent_data.gps.latitude,
        longitude=data.agent_data.gps.longitude,
        timestamp=timestamp
    )

    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return {"id": db_item.id, "message": "Data successfully stored"}


@app.get("/processed_agent_data/")
async def get_all_data(db: Session = Depends(get_db)):
    data = db.query(ProcessedAgentDataInDB).all()
    return data


@app.get("/processed_agent_data/{item_id}")
async def get_data_by_id(item_id: int = Path(..., description="ID запису для отримання"),
                         db: Session = Depends(get_db)):
    data = db.query(ProcessedAgentDataInDB).filter(ProcessedAgentDataInDB.id == item_id).first()
    if data is None:
        raise HTTPException(status_code=404, detail=f"Запис з ID {item_id} не знайдено")
    return data


@app.put("/processed_agent_data/{item_id}")
async def update_data(
        item_id: int = Path(..., description="ID запису для оновлення"),
        data: ProcessedAgentDataUpdate = None,
        db: Session = Depends(get_db)
):
    db_item = db.query(ProcessedAgentDataInDB).filter(ProcessedAgentDataInDB.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail=f"Запис з ID {item_id} не знайдено")

    update_data_dict = data.dict(exclude_unset=True)

    # Обробка timestamp, якщо він присутній у запиті
    if "timestamp" in update_data_dict:
        update_data_dict["timestamp"] = datetime.fromtimestamp(update_data_dict["timestamp"])

    for key, value in update_data_dict.items():
        setattr(db_item, key, value)

    db.commit()
    db.refresh(db_item)
    return db_item


@app.delete("/processed_agent_data/{item_id}")
async def delete_data(item_id: int = Path(..., description="ID запису для видалення"), db: Session = Depends(get_db)):
    db_item = db.query(ProcessedAgentDataInDB).filter(ProcessedAgentDataInDB.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail=f"Запис з ID {item_id} не знайдено")

    db.delete(db_item)
    db.commit()
    return {"message": f"Запис з ID {item_id} успішно видалено"}


# WebSocket Support
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, data: Dict[str, Any]):
        for connection in self.active_connections:
            await connection.send_text(json.dumps(data))


manager = ConnectionManager()


@app.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(json.loads(data))
    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
