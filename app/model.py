import datetime

import uuid
from sqlalchemy import Column, String, Integer, Float, Date, Boolean, ForeignKey, DateTime
from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

import config

meta = MetaData()

engine = create_engine(
    config.DATABASE_URI, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def clear_database():
    session = SessionLocal()
    meta = Base.metadata
    for table in reversed(meta.sorted_tables):
        try:
            session.execute(table.delete())
        except:
            pass
    session.commit()


def create_database():
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Menu(Base):
    __tablename__ = 'menu_table'

    id = Column(String, primary_key=True, default=lambda: uuid.uuid4().hex)

    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)

    energy = Column(Integer, nullable=False)
    protein = Column(Float, nullable=False)
    fat = Column(Float, nullable=False)
    salt = Column(Float, nullable=False)

    is_permanent = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Menu(id='{self.id}', name='{self.name}', price='{self.price}', nutrition=({self.energy}, {self.protein}, {self.fat}, {self.salt}))>"


class Like(Base):
    __tablename__ = 'like_table'

    id = Column(String, primary_key=True, default=lambda: uuid.uuid4().hex)

    menu = Column(String, ForeignKey(Menu.id, name="fk_menu_00"))
    by = Column(String, nullable=False, index=True)

    def __repr__(self):
        return f"<Like(id='{self.id}', menu='{self.menu}', by='{self.by}')>"


class Schedule(Base):
    __tablename__ = 'schedule_table'

    id = Column(String, primary_key=True, default=lambda: uuid.uuid4().hex)

    date = Column(Date, index=True, nullable=False, default=datetime.date.today())
    a_menu = Column(String, ForeignKey(Menu.id, name="fk_menu_a"))
    b_menu = Column(String, ForeignKey(Menu.id, name="fk_menu_b"))

    def __repr__(self):
        return f"<Schedule(id='{self.id}', date='{self.date}', a_menu='{self.a_menu}', b_menu='{self.b_menu}')>"


class SoldOut(Base):
    __tablename__ = 'sold_out_table'

    id = Column(String, primary_key=True, default=lambda: uuid.uuid4().hex)
    menu = Column(String, ForeignKey(Menu.id, name="fk_menu_00"))
    timestamp = Column(DateTime, default=datetime.datetime.now)
    by = Column(String)

    is_sold_out = Column(Boolean)

    def __repr__(self):
        return f"<SoldOut(id='{self.id}', menu='{self.menu}', timestamp='{self.timestamp}', is_sold_out={self.is_sold_out})>"


class Congestion(Base):
    __tablename__ = 'congestion_table'

    id = Column(String, primary_key=True, default=lambda: uuid.uuid4().hex)
    congestion = Column(Integer, nullable=False)
    # 0: vacant
    # 1: middle
    # 2: crowded
    timestamp = Column(DateTime, default=datetime.datetime.now)
    by = Column(String)

    def __repr__(self):
        return f"<Congestion(id='{self.id}', congestion='{self.congestion}', timestamp='{self.timestamp}')>"
