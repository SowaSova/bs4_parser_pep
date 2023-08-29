# utils.py
import logging

from requests import RequestException

from constants import EXPECTED_STATUS
from exceptions import ParserFindTagException


def get_response(session, url):
    try:
        response = session.get(url)
        response.encoding = "utf-8"
        return response
    except RequestException:
        logging.exception(
            f"Возникла ошибка при загрузке страницы {url}", stack_info=True
        )


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f"Не найден тег {tag} {attrs}"
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag


def validate_status(status):
    if status in EXPECTED_STATUS:
        return True
    else:
        logging.ERROR(
            f"Статус: {status} отсутствует в списке ожидаемых статусов."
        )
        pass


def list_dict_compare(preview_status, detail_status, url, result):
    if detail_status in EXPECTED_STATUS[preview_status]:
        index = [x[0] for x in result].index(detail_status)
        result[index] = (detail_status, result[index][1] + 1)
        index_total = [x[0] for x in result].index("TOTAL")
        result[index_total] = ("TOTAL", result[index_total][1] + 1)
    else:
        logging.exception(
            f"""
                Несовпадающие статусы:
                {url}
                Статус в карточке: {detail_status}
                Ожидаемые статусы: {EXPECTED_STATUS[preview_status]}
            """
        )
    return result
