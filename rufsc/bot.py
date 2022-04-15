import datetime as dt
import os
import time

import schedule
import telebot

from rufsc.webscraping import get_menu

API_KEY = os.getenv("RUFSC_BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
bot = telebot.TeleBot(API_KEY)


def prettify_menu_msg(menu: dict) -> str:
    menu_msg = ""
    if menu is not None:
        for header, meal in menu.items():
            menu_msg += f"{header}\n"
            for m in meal:
                menu_msg += f"      {m}\n"
            menu_msg += "\n"
        menu_msg += "*Cardápio sujeito a alterações."
    else:
        menu_msg += (
            f"Cardápio para o dia {dt.date.today().strftime('%d/%m/%Y')} não disponível"
        )
    return menu_msg


def send_today_menu():
    menu_msg = prettify_menu_msg(get_menu())
    bot.send_message(CHANNEL_ID, menu_msg)


def run(run_time: str):
    send_today_menu()
    schedule.every().day.at(run_time).do(send_today_menu)
    while True:
        schedule.run_pending()
        time.sleep(3600)
