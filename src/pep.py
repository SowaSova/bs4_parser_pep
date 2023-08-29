import logging
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup as bs
from tqdm import tqdm

PEPS_LIST_URL = "https://peps.python.org/"
EXPECTED_STATUS = {
    "A": ("Active", "Accepted"),
    "D": ("Deferred",),
    "F": ("Final",),
    "P": ("Provisional",),
    "R": ("Rejected",),
    "S": ("Superseded",),
    "W": ("Withdrawn",),
    "": ("Draft", "Active"),
}


if __name__ == "__main__":
    session = requests_cache.CachedSession()
    session.cache.clear()

    response = session.get(PEPS_LIST_URL)
    response.encoding = "utf-8"

    soup = bs(response.text, "lxml")
    head_section = soup.find("section", id="index-by-category")
    sections = head_section.find_all("section")

    result = [("Статус", "Общее количество")]
    for key, values in EXPECTED_STATUS.items():
        for value in values:
            result.append((value, 0))
    result.append(("TOTAL", 0))

    for section in tqdm(sections):
        title = section.a.text
        table = section.find("table")
        for row in table.find_all("tr"):
            strings = row.find_all("td")
            if len(strings) > 0:
                first_column_tag = strings[0]
                preview_status = first_column_tag.text[1:]
                second_column_tag = strings[1]
                pep_href = second_column_tag.a["href"]
                print(pep_href)
                pep_url = urljoin(PEPS_LIST_URL, pep_href)

                response = session.get(pep_url)
                response.encoding = "utf-8"

                soup = bs(response.text, "lxml")

                field_list = soup.find(
                    "dl", attrs={"class": "rfc2822 field-list simple"}
                )
                status_tag = field_list.find(
                    lambda tag: tag.name == "dt"
                    and tag.text == "Status:"
                    or tag.text == "Status"
                )
                status = status_tag.find_next_sibling().string
                if preview_status in EXPECTED_STATUS:
                    if status in EXPECTED_STATUS[preview_status]:
                        index = [x[0] for x in result].index(status)
                        result[index] = (status, result[index][1] + 1)
                        index_total = [x[0] for x in result].index("TOTAL")
                        result[index_total] = (
                            "TOTAL",
                            result[index_total][1] + 1,
                        )
                    else:
                        logging.INFO(
                            f"Несовпадающие статусы:\n{pep_url}\nСтатус в карточке: {status}\nОжидаемые статусы: {EXPECTED_STATUS[preview_status]}"
                        )
                else:
                    logging.ERROR(
                        f"Статус: {preview_status} отсутствует в списке ожидаемых статусов."
                    )
