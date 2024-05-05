import datetime

from sqlalchemy import insert

from db import SessionLocal
from models import User


class CrudUser:

    def __enter__(self):
        """ Opening connection with DB"""
        self._db = SessionLocal()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ Closing the connection """
        self._db.close()
        if exc_val:
            raise

    def user_exist(self, tg_id: int):
        """ Проверка существования пользователя """

        if not self._db.query(User).get(tg_id):
            return False
        return True

    def add_user(self, tg_id: int, username: str, interaction: str):
        """Создание пользователя"""

        if self._db.query(User).filter(User.id == tg_id).count():
            print("User already exists")

        try:
            stmt = insert(User).values({"id": tg_id, "username": username, "interaction": interaction})
            self._db.execute(stmt)
            self._db.commit()
        except:
            print("error: User already exists")

    def change_values(self, tg_id: int, interaction: str = None, last_msg_time: bool = False, status: str = None):
        """interaction - Изменяет interaction при каждой отправке сообщения пользователю
         last_msg_time - Изменяет время последнего сообщения от пользователя
         status - Изменяет статус пользователя
         """

        # Достаём User, редактируем переданные поля
        user = self._db.query(User).get(tg_id)

        if not user:
            print("User not found")
            raise Exception('User not found')

        if interaction:
            user.interaction = interaction

        if last_msg_time:
            user.last_msg_time = datetime.datetime.now()

        if status:
            user.status = status
            user.status_updated_at = datetime.datetime.now()

        self._db.add(user)
        self._db.commit()

    def get_all_alive_users_by_interaction(self, iteraction: str) -> list:
        """Получаем всех пользователей со статусом alive и нужным iteraction """
        try:
            users = self._db.query(User).filter(User.status == 'alive').filter(User.interaction == iteraction)
            u = []
            for i in users:
                u.append({"id": i.id, "last_msg_time": i.last_msg_time})
            return u


        except:
            return []


if __name__ == '__main__':
    with CrudUser() as c:
        d = c.get_all_alive_users_by_interaction(iteraction='three')
        print(d)
