from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel

app = FastAPI()

DATABASE_URL = "sqlite:///./leave.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ---------------- MODELS ----------------
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    role = Column(String)

class Leave(Base):
    __tablename__ = "leaves"
    id = Column(Integer, primary_key=True)
    employee_name = Column(String)
    reason = Column(String)
    start_date = Column(String)
    end_date = Column(String)
    status = Column(String, default="Pending")

Base.metadata.create_all(bind=engine)

# ---------------- SCHEMAS ----------------
class UserCreate(BaseModel):
    username: str
    password: str
    role: str

class LoginRequest(BaseModel):
    username: str
    password: str

class LeaveRequest(BaseModel):
    employee_name: str
    reason: str
    start_date: str
    end_date: str

# ---------------- DB ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------- REGISTER ----------------
@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="User exists")

    db.add(User(**user.dict()))
    db.commit()
    return {"message": "User created"}

# ---------------- LOGIN ----------------
@app.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()

    if not user or user.password != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"username": user.username, "role": user.role}

# ---------------- APPLY LEAVE ----------------
@app.post("/leave")
def apply_leave(data: LeaveRequest, db: Session = Depends(get_db)):
    leave = Leave(**data.dict())
    db.add(leave)
    db.commit()
    return {"message": "Leave applied successfully"}

# ---------------- GET LEAVES ----------------
@app.get("/leaves")
def get_leaves(db: Session = Depends(get_db)):
    leaves = db.query(Leave).all()

    # Convert to JSON properly (IMPORTANT FIX)
    return [
        {
            "id": l.id,
            "employee_name": l.employee_name,
            "reason": l.reason,
            "start_date": l.start_date,
            "end_date": l.end_date,
            "status": l.status,
        }
        for l in leaves
    ]

# ---------------- UPDATE ----------------
@app.put("/leave/{leave_id}")
def update_leave(leave_id: int, status: str, db: Session = Depends(get_db)):
    leave = db.query(Leave).filter(Leave.id == leave_id).first()

    if not leave:
        raise HTTPException(status_code=404, detail="Not found")

    leave.status = status
    db.commit()
    return {"message": "Updated"}