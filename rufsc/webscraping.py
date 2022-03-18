import datetime as dt

import requests
from bs4 import BeautifulSoup


def get_menu():
    url = "https://ru.ufsc.br/ru/"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    table = soup.find("div", {"class": "content clearfix"}).find("tbody")
    table_lines = table.find_all("tr")

    headers = []
    for col in table_lines[0].find_all("td"):
        headers.extend(col.text.splitlines(False))

    meals = []
    table_lines.pop(0)
    for line in table_lines:
        for i, col in enumerate(line.find_all("td")):
            item = col.text.splitlines(False)
            if i == 0:
                menu_day = item[0].strip("\xa0")
                day = dt.datetime.strptime(menu_day, "%d.%m.%Y")
                if day.date() != dt.datetime.today().date():
                    break
            meals.append(item)

    # Maybe we can pack them up into a dict? \/
    # menu = {k: v for k, v in zip(headers, food)}
    # pprint(menu)
    print_menu(headers, meals)
    return headers, meals


def print_menu(headers, meals):
    for header, meal in zip(headers, meals):
        print(header)
        for m in meal:
            print("  ", m)


if __name__ == "__main__":
    get_menu()
