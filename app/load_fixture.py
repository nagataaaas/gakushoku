import sys
sys.path.append('./')

import json
import datetime
import uuid
import random

from app.model import SessionLocal, Menu, Schedule, clear_database, create_database, SoldOut, Like

from typing import List

def uuid_from_text(text: str) -> str:
    return uuid.uuid5(uuid.NAMESPACE_URL, text).hex


def load_permanent(permanent_json: List[dict]) -> List[str]:
    menus = [Menu(id=uuid_from_text(menu['name']), name=menu['name'], price=menu['price'],
                  energy=menu['nutrition']['energy'],
                  protein=menu['nutrition']['protein'], fat=menu['nutrition']['fat'],
                  salt=menu['nutrition']['salt'], is_permanent=True) for menu in permanent_json]
    session = SessionLocal()
    session.add_all(menus)
    session.commit()
    try:
        return [menu.id for menu in menus]
    finally:
        session.close()


def load_special(special_json: dict) -> List[str]:
    menu_dict = {}
    session = SessionLocal()
    for date, value in special_json.items():
        schedule = Schedule(date=datetime.datetime.fromisoformat(date).date())
        if value['A']['name'] not in menu_dict:
            menu = Menu(id=uuid_from_text(value['A']['name']), name=value['A']['name'], price=380,
                        energy=value['A']['nutrition']['energy'],
                        protein=value['A']['nutrition']['protein'], fat=value['A']['nutrition']['fat'],
                        salt=value['A']['nutrition']['salt'], is_permanent=False)
            session.add(menu)
            menu_dict[value['A']['name']] = menu.id
        schedule.a_menu = menu_dict[value['A']['name']]
        if value['B']['name'] not in menu_dict:
            menu = Menu(id=uuid_from_text(value['B']['name']), name=value['B']['name'], price=320,
                        energy=value['B']['nutrition']['energy'],
                        protein=value['B']['nutrition']['protein'], fat=value['B']['nutrition']['fat'],
                        salt=value['B']['nutrition']['salt'], is_permanent=False)
            session.add(menu)
            menu_dict[value['B']['name']] = menu.id
        schedule.b_menu = menu_dict[value['B']['name']]
        session.add(schedule)
    session.commit()
    try:
        return list(menu_dict.values())
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
    with open('app/fixture/permanent.json', 'r', encoding='utf-8') as f:
        permanent_json = json.load(f)
    with open('app/fixture/special.json', 'r', encoding='utf-8') as f:
        special_json = json.load(f)

    ps = load_permanent(permanent_json)
    ls = load_special(special_json)

    load_like(400, ps+ls)

    session = SessionLocal()
    session.add(SoldOut(menu=ps[0], timestamp=datetime.datetime.now(), is_sold_out=True))
    session.commit()

    session.close()

    return ps + ls


if __name__ == '__main__':
    main()
