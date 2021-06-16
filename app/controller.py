import sys
sys.path.append('./')

from typing import List, Tuple
from app.model import Menu, Schedule, SoldOut, Like, Congestion
from app.scheme import MenuModel, NutritionModel, ScheduleModel, DayMenuModel, PermanentModel

from sqlalchemy.orm import Session
from sqlalchemy import func, exists, and_
from sqlalchemy.orm import aliased
import datetime

from app.config import MAX_SOLD_OUT_POST_PER_DAY, MAX_CONGESTION_POST_PER_DAY


def all_permanent(db: Session) -> PermanentModel:
    result = []

    inner_sold_out = aliased(SoldOut)
    like_query = db.query(Like.menu, func.count(Like.id).label('like_count')).group_by(Like.menu).subquery()
    data: List[Tuple[Menu, SoldOut, int]] = db.query(Menu, SoldOut, like_query.c.like_count) \
        .outerjoin(like_query, Menu.id == like_query.c.menu) \
        .outerjoin(SoldOut, Menu.id == SoldOut.menu) \
        .group_by(Menu.id) \
        .filter(
        ~exists().where(and_(SoldOut.menu == inner_sold_out.menu, inner_sold_out.timestamp > SoldOut.timestamp))) \
        .filter(Menu.is_permanent == True) \
        .group_by(SoldOut.id)\
        .group_by(like_query.c.like_count)\
        .all()

    for menu, sold_out, like_count in data:
        nutrition = NutritionModel(energy=menu.energy, protein=menu.protein, fat=menu.fat, salt=menu.salt)

        is_sold_out = sold_out is not None and sold_out.is_sold_out and sold_out.timestamp.date() == datetime.date.today()

        menu_data = MenuModel(id=menu.id, name=menu.name, price=menu.price, nutrition=nutrition,
                              is_sold_out=is_sold_out, like_count=like_count or 0)
        result.append(menu_data)

    return PermanentModel(menus=result)


def get_special(dates: List[datetime.date], db: Session) -> ScheduleModel:
    result = ScheduleModel(schedules=[])

    schedules = db.query(Schedule).filter(Schedule.date.in_(dates)).all()
    like_query = db.query(Like.menu, func.count(Like.id).label('like_count')).group_by(Like.menu).subquery()

    for schedule in schedules:
        inner_sold_out = aliased(SoldOut)
        menu_data = []
        for menu in (schedule.a_menu, schedule.b_menu):
            menu, sold_out, like_count = db.query(Menu, SoldOut, like_query.c.like_count) \
                .outerjoin(like_query, Menu.id == like_query.c.menu) \
                .outerjoin(SoldOut, Menu.id == SoldOut.menu) \
                .group_by(Menu.id) \
                .filter(
                ~exists().where(
                    and_(SoldOut.menu == inner_sold_out.menu, inner_sold_out.timestamp > SoldOut.timestamp))) \
                .filter(Menu.id == menu) \
                .first()

            nutrition = NutritionModel(energy=menu.energy, protein=menu.protein, fat=menu.fat, salt=menu.salt)
            is_sold_out = sold_out is not None and sold_out.is_sold_out and sold_out.timestamp.date() == datetime.date.today()
            menu_data.append(MenuModel(id=menu.id, name=menu.name, price=menu.price, nutrition=nutrition,
                                       is_sold_out=is_sold_out, like_count=like_count or 0))

        result.schedules.append(DayMenuModel(month=schedule.date.month, day=schedule.date.day,
                                             a_menu=menu_data[0], b_menu=menu_data[1]))

    return result


def like_this(menu_id: str, sub: str, db: Session) -> bool:
    if not is_valid_menu_id(menu_id, db):
        return False
    if db.query(Like).filter(Like.menu == menu_id, Like.by == sub).all():
        return False
    like = Like(menu=menu_id, by=sub)
    db.add(like)
    db.commit()

    return True


def dislike_this(menu_id: str, sub: str, db: Session) -> bool:
    data = db.query(Like).filter(Like.menu == menu_id, Like.by == sub).all()
    if not data:
        return False
    db.delete(data[0])
    db.commit()

    return True


def get_likes_by_sub(sub: str, db: Session) -> List[str]:
    likes: List[Like] = db.query(Like).filter(Like.by == sub).all()
    return [like.menu for like in likes]


def is_valid_menu_id(menu_id: str, db: Session) -> bool:
    return db.query(Menu).get(menu_id) is not None


def get_menu(menu_id: str, db: Session) -> MenuModel or None:
    inner_sold_out = aliased(SoldOut)
    like_query = db.query(Like.menu, func.count(Like.id).label('like_count')).group_by(Like.menu).subquery()
    data: List[Tuple[Menu, SoldOut, int]] = db.query(Menu, SoldOut, like_query.c.like_count) \
        .outerjoin(like_query, Menu.id == like_query.c.menu) \
        .outerjoin(SoldOut, Menu.id == SoldOut.menu) \
        .group_by(Menu.id) \
        .filter(
        ~exists().where(and_(SoldOut.menu == inner_sold_out.menu, inner_sold_out.timestamp > SoldOut.timestamp))) \
        .filter(Menu.id == menu_id) \
        .one_or_none()
    if not data:
        return None
    menu, sold_out, like_count = data

    nutrition = NutritionModel(energy=menu.energy, protein=menu.protein, fat=menu.fat, salt=menu.salt)

    is_sold_out = sold_out is not None and sold_out.is_sold_out and sold_out.timestamp.date() == datetime.date.today()

    menu_data = MenuModel(id=menu.id, name=menu.name, price=menu.price, nutrition=nutrition,
                          is_sold_out=is_sold_out, like_count=like_count or 0)
    return menu_data


def set_sold_out(menu_id: str, is_sold_out: bool, sub: str, db: Session) -> bool:
    today_datetime = datetime.datetime(datetime.datetime.today().year, datetime.datetime.today().month,
                                       datetime.datetime.today().day)
    if len(db.query(SoldOut).filter(SoldOut.by == sub,
                                    SoldOut.timestamp > today_datetime).all()) >= MAX_SOLD_OUT_POST_PER_DAY:
        return False
    if not is_valid_menu_id(menu_id, db):
        return False
    sold_out_data = SoldOut(menu=menu_id, timestamp=datetime.datetime.now(), is_sold_out=is_sold_out, by=sub)
    db.add(sold_out_data)
    db.commit()
    return True


def get_congestion(db: Session) -> int:
    today_datetime = datetime.datetime(datetime.datetime.today().year, datetime.datetime.today().month,
                                       datetime.datetime.today().day)
    congestion = db.query(Congestion).order_by(Congestion.timestamp.desc()) \
        .filter(Congestion.timestamp > today_datetime).first()
    return congestion.congestion if congestion else 0


def set_congestion(congestion: int, sub: str, db: Session) -> bool:
    today_datetime = datetime.datetime(datetime.datetime.today().year, datetime.datetime.today().month,
                                       datetime.datetime.today().day)
    if len(db.query(Congestion).filter(Congestion.by == sub,
                                       Congestion.timestamp > today_datetime).all()) >= MAX_CONGESTION_POST_PER_DAY:
        return False
    congestion = Congestion(congestion=congestion, timestamp=datetime.datetime.now(), by=sub)
    db.add(congestion)
    db.commit()
    return True
