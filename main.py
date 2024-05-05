from datetime import datetime, timedelta
from threading import Thread
import time
import re

from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from pyrogram import errors

import models
from crud import CrudUser
from db import engine


models.Base.metadata.create_all(bind=engine)

INTERVAL1 = timedelta(minutes=6)
INTERVAL2 = timedelta(minutes=39)
INTERVAL3 = timedelta(days=1, hours=2)

API_HASH = "aABCDd"
API_ID = 123

STOP_WORDS = ['прекрасно', 'ожидать']  # in lower case

client = Client(name='me_client', api_id=API_ID, api_hash=API_HASH, parse_mode=ParseMode.HTML)


@client.on_message()
def all_message(client: Client, message: Message):
    if message.from_user:  # Если это сообщение от юзера, иначе игнор

        if not message.outgoing and message.chat.id > 0:  # Если это входящее сообщение и сообщение не из чата то обрабатываем
            with CrudUser() as c:
                if c.user_exist(tg_id=message.chat.id):  # Юзер существует
                    c.change_values(tg_id=message.chat.id, last_msg_time=True)
                else:  # Юзер еше не существует в БД
                    c.add_user(tg_id=message.chat.id, username=message.from_user.username, interaction='zero')
        else:
            if message.outgoing and message.chat.id > 0:  # Если это исходящее сообщение и сообщение не из чата то обрабатываем

                flag_stop = False
                for s in STOP_WORDS:
                    if re.findall(s, message.text.lower()):
                        flag_stop = True

                with CrudUser() as u:
                    if u.user_exist(tg_id=message.chat.id):
                        if flag_stop:
                            u.change_values(tg_id=message.chat.id, interaction='manual')
                    else:
                        u.add_user(tg_id=message.chat.id, username=message.chat.username, interaction='manual')

def bg_informer():
    while True:
        with CrudUser() as c:
            today = datetime.now()

            # Отправка сообщения через 6 минут
            users_zero = c.get_all_alive_users_by_interaction(iteraction='zero')
            for uz in users_zero:
                t_event1 = uz.get("last_msg_time") + INTERVAL1
                t_event1_delta = t_event1 + timedelta(minutes=1)

                if today >= t_event1 and today <= t_event1_delta:
                    try:
                        client.send_message(uz.get("id"),
                                            'Добрый день, пришлите свои контактные данные в ответном сообщении')
                        c.change_values(tg_id=uz.get("id"), interaction='one')
                    except (errors.UserDeactivated, errors.UserDeactivatedBan):
                        c.change_values(tg_id=uz.get("id"), status='dead')

            # Отправка сообщения через 39 минут
            users_one = c.get_all_alive_users_by_interaction(iteraction='one')
            for uo in users_one:
                t_event2 = uo.get("last_msg_time") + INTERVAL2
                t_event2_delta = t_event2 + timedelta(minutes=1)

                if today >= t_event2 and today <= t_event2_delta:
                    try:
                        client.send_message(uo.get("id"),
                                            'Ваша заявка принята, ссылка на мероприятие будет оправлена позже')
                        c.change_values(tg_id=uo.get("id"), interaction='two')
                    except (errors.UserDeactivated, errors.UserDeactivatedBan):
                        c.change_values(tg_id=uo.get("id"), status='dead')

            # Отправка сообщения через 1 день 2 часа
            users_three = c.get_all_alive_users_by_interaction(iteraction='two')
            for ut in users_three:
                t_event3 = ut.get("last_msg_time") + INTERVAL3
                t_event3_delta = t_event3 + timedelta(minutes=1)

                if today >= t_event3 and today <= t_event3_delta:
                    try:
                        client.send_message(ut.get("id"),
                                            'Ccылка на мероприятие готова! Добро пожаловать! link')
                        c.change_values(tg_id=ut.get("id"), interaction='three', status='finished')
                    except (errors.UserDeactivated, errors.UserDeactivatedBan):
                        c.change_values(tg_id=ut.get("id"), status='dead')

        time.sleep(59)


if __name__ == '__main__':
    Thread(target=bg_informer).start()
    client.run()
