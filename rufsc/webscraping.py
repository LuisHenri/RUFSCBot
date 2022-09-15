import datetime as dt
from typing import Optional

import pandas as pd
import requests
import tabula as tb
from bs4 import BeautifulSoup


def get_menu() -> Optional[dict]:
    today = dt.date.today()
    url = "https://restaurante.joinville.ufsc.br/cardapio-da-semana/"
    pdf_link = get_pdf_link(url, today)
    if not pdf_link:
        return None
    pdf_table = get_pdf_table(pdf_link)

    # Extract data from the PDF Table
    # today_menu = None
    # ranges = [slice(11 * i, 11 * (1 + i)) for i in range(3)]  # 0:11, 11:22, 22:33
    # for i in range(3):
    #     pdf_today_date = pdf_table[11 * i]
    #     try:
    #         pdf_today_date = dt.datetime.strptime(pdf_today_date, "%d/%m/%Y").date()
    #     except ValueError:
    #         break
    #
    #     # Get today's menu
    #     if pdf_today_date == today:
    #         today_menu = pdf_table[ranges[i]]
    #         break

    if pdf_table is not None:
        today_date = today.strftime("%d/%m/%Y")
        menu = {
            "Data": [today_date, _weekday2name[today.isoweekday()]],
            "Preparações Fixas": [],
            "Carne": [],
            "Complemento": [],
            "Saladas": [],
            "Molho para salada": [],
            "Sobremesa": [],
        }
        for i, item in enumerate(pdf_table):
            food = (
                item.replace("FIXO: ", "")
                .replace("FIXO:", "")
                .replace("PTS", "Proteína texturizada de soja")
                .replace("\r", " ")
                .capitalize()
            )
            menu[get_menu_header(i)].append(food)
        return menu
    else:
        # No menu for today. Maybe they didn't add it yet.
        return None


def get_pdf_link(url: str, today: dt.date) -> Optional[str]:
    # Request and find PDF menus
    page = requests.get(url)
    page_content = page.content
    page_soup = BeautifulSoup(page_content, "html.parser")

    p = [p.find("a") for p in page_soup.find_all("p") if p.find("a")]
    pdfs = [
        link.get("href")
        for link in p
        if _number2month[today.month] in link.get("href").lower()
    ]
    pdf_link = pdfs[0] if pdfs else None

    return pdf_link


def get_pdf_table(pdf_link: str) -> pd.DataFrame:
    # Pandas DataFrame creation from PDF
    pandas_options = {
        "names": list(range(1, 8)),  # ISO weekday numbers (1=Monday, 2=Tuesday, etc.)
    }
    pdf_table = (
        tb.read_pdf(pdf_link, pandas_options=pandas_options, lattice=False)[0]
        .drop([0, 1])[dt.date.today().isoweekday()]  # Filter by the day of the week
        .fillna("Não foi possível obter informações")
        .reset_index(drop=True)
    )
    return pdf_table


def get_menu_header(i: int) -> str:
    if 0 <= i <= 2:
        return "Preparações Fixas"
    elif i == 3:
        return "Carne"
    elif 4 <= i <= 5:
        return "Complemento"
    elif i == 6:
        return "Molho para salada"
    elif 7 <= i <= 8:
        return "Saladas"
    elif i == 9:
        return "Sobremesa"


_weekday2name = {
    1: "Segunda-feira",
    2: "Terça-feira",
    3: "Quarta-feira",
    4: "Quinta-feira",
    5: "Sexta-feira",
    6: "Sábado",
    7: "Domingo",
}

_number2month = {
    1: "janeiro",
    2: "fevereiro",
    3: "março",
    4: "abril",
    5: "maio",
    6: "junho",
    7: "julho",
    8: "agosto",
    9: "setembro",
    10: "outubro",
    11: "novembro",
    12: "dezembro",
}

if __name__ == "__main__":
    print(get_menu())
