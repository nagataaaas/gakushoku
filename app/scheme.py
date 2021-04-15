from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from fastapi import Query


class NutritionModel(BaseModel):
    energy: int
    protein: float
    fat: float
    salt: float


class MenuModel(BaseModel):
    id: str
    name: str
    price: int
    is_sold_out: bool
    like_count: int
    is_liked: bool = False

    nutrition: NutritionModel


class PermanentModel(BaseModel):
    menus: List[MenuModel]


class DayMenuModel(BaseModel):
    month: int
    day: int

    a_menu: MenuModel
    b_menu: MenuModel


class ScheduleModel(BaseModel):
    schedules: List[DayMenuModel]


class SoldOutPostRequest(BaseModel):
    menu_id: str
    is_sold_out: bool
    token: str


class LikePostRequest(BaseModel):
    menu_id: str
    token: str


class MyLikesModel(BaseModel):
    likes: List[str]


class CongestionPostRequest(BaseModel):
    congestion: int
    token: str

class CongestionModel(BaseModel):
    congestion: int