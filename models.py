import datetime

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from db import Base
from sqlalchemy.dialects.postgresql import array


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, unique=True)  # tg id
    created_at = Column(DateTime, default=datetime.datetime.now)
    status = Column(String, default="alive")
    status_updated_at = Column(DateTime, default=datetime.datetime.now)
    last_msg_time = Column(DateTime, default=datetime.datetime.now)
    interaction = Column(String, default='zero')  # взаимодействие c пользователем
    username = Column(String)  # Имя пользователя

# TODO: Для полей 'status' и "interaction" можно создать отдельную таблицы статусов и взаимодействий и подтягивать из них данные.
#  В целях экономии времени это не было реализовано
