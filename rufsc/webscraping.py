import datetime as dt
from typing import Optional

import pandas as pd
import requests
import tabula as tb
from bs4 import BeautifulSoup


def get_menu() -> Optional[dict]:
    url = "https://restaurante.joinville.ufsc.br/cardapio-da-semana/"
    pdf_link = get_pdf_link(url)
    pdf_table = get_pdf_table(pdf_link)

    # Extract data from the PDF Table
    today_menu = None
    ranges = [slice(11 * i, 11 * (1 + i)) for i in range(3)]  # 0:11, 11:22, 22:33
    for i in range(3):
        pdf_today_date = pdf_table[dt.datetime.today().isoweekday()][11 * i]
        pdf_today_date = dt.datetime.strptime(pdf_today_date, "%d/%m/%Y").date()

        # Get today's menu
        if pdf_today_date == dt.date.today():
            today_menu = pdf_table[dt.datetime.today().isoweekday()][ranges[i]]
            break

    if today_menu is not None:
        menu = {
            "Data": [],
            "Preparações Fixas": [],
            "Carne": [],
            "Complemento": [],
            "Saladas": [],
            "Molho para salada": [],
            "Sobremesa": [],
        }
        for i, item in enumerate(today_menu):
            menu[get_menu_header(i)].append(item.capitalize())
        return menu
    else:
        # No menu for today. Maybe they didn't add it yet.
        return None


def get_pdf_link(url: str) -> Optional[str]:
    # Request and find PDF menus
    page = requests.get(url)
    page_content = page.content
    page_soup = BeautifulSoup(page_content, "html.parser")

    p = page_soup.find("p").find_all("a")
    pdfs = [link.get("href") for link in p if "Cardápio" in link.get("href")]

    return pdfs[-1]


def get_pdf_table(pdf_link: str) -> pd.DataFrame:
    # Pandas DataFrame creation from PDF
    pandas_options = {
        "names": list(range(1, 8)),  # ISO weekday numbers (1=Monday, 2=Tuesday, etc.)
    }
    pdf_table = (
        tb.read_pdf(pdf_link, pages=1, pandas_options=pandas_options, lattice=True)[0]
        .drop([0, 1])  # Remove NaN and Column names
        .reset_index()
    )
    return pdf_table


def get_menu_header(i: int) -> str:
    if i == 0:
        return "Data"
    elif 1 <= i <= 3:
        return "Preparações Fixas"
    elif i == 4:
        return "Carne"
    elif 5 <= i <= 6:
        return "Complemento"
    elif i == 7:
        return "Molho para salada"
    elif 8 <= i <= 9:
        return "Saladas"
    elif i == 10:
        return "Sobremesa"
