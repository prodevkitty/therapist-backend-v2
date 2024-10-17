
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.tool import Tool
from models.user_tool import UserTool
from database import get_db
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class ToolCreate(BaseModel):
    name: str
    description: str
    category: str
    content: str

class ToolResponse(BaseModel):
    id: int
    name: str
    description: str
    category: str
    content: str

    class Config:
        orm_mode = True

class UserToolCreate(BaseModel):
    user_id: int
    tool_id: int

class UserToolResponse(BaseModel):
    id: int
    user_id: int
    tool_id: int
    interaction_date: datetime

    class Config:
        orm_mode = True


@router.post("/tools", response_model=ToolResponse)
def create_tool(tool: ToolCreate, db: Session = Depends(get_db)):
    db_tool = Tool(**tool.dict())
    db.add(db_tool)
    db.commit()
    db.refresh(db_tool)
    return db_tool

@router.get("/tools", response_model=list[ToolResponse])
def get_tools(db: Session = Depends(get_db)):
    return db.query(Tool).all()

@router.post("/user_tools", response_model=UserToolResponse)
def create_user_tool(user_tool: UserToolCreate, db: Session = Depends(get_db)):
    db_user_tool = UserTool(**user_tool.dict())
    db.add(db_user_tool)
    db.commit()
    db.refresh(db_user_tool)
    return db_user_tool

@router.get("/user_tools/{user_id}", response_model=list[UserToolResponse])
def get_user_tools(user_id: int, db: Session = Depends(get_db)):
    return db.query(UserTool).filter(UserTool.user_id == user_id).all()