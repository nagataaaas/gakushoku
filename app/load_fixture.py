import datetime
import random
import uuid
from typing import List

from app.fixture.create_data import special_menu, permanent_menu
from app.model import SessionLocal, Menu, Schedule, clear_database, create_database, SoldOut, Like


def uuid_from_text(text: str) -> str:
    return uuid.uuid5(uuid.NAMESPACE_URL, text).hex


def load_permanent(permanent_data: List[Menu]) -> List[str]:
    session = SessionLocal()
    for menu in permanent_data:
        menu.id = uuid_from_text(menu.name)
    session.add_all(permanent_data)
    session.commit()
    try:
        return [menu.id for menu in permanent_data]
    finally:
        session.close()


def load_special(special_data: dict):
    menu_dict = set()
    session = SessionLocal()
    for date, menu in special_data.items():
        schedule = Schedule(date=date)
        session.add_all([menu['A'], menu['B']])
        session.commit()
        schedule.a_menu = menu['A'].id
        schedule.b_menu = menu['B'].id
        menu_dict.add(menu['A'].id)
        menu_dict.add(menu['B'].id)
        session.add(schedule)
    session.commit()
    try:
        return list(menu_dict)
    finally:
        session.close()


def load_like(all_sum: int, ids: List[str]):
    session = SessionLocal()
    for i in range(all_sum):
        session.add(Like(menu=random.choice(ids), by=uuid_from_text(str(i))))
    session.commit()
    session.close()


def main():
    clear_database()
    create_database()

    permanent_data = permanent_menu()
    special_data = special_menu()

    ps = load_permanent(permanent_data)
    ls = load_special(special_data)

    load_like(400, ps + ls)

    session = SessionLocal()
    session.add(SoldOut(menu=ps[0], timestamp=datetime.datetime.now(), is_sold_out=True))
    session.commit()

    session.close()

    return ps + ls


if __name__ == '__main__':
    main()
