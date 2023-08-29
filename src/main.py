import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup as bs
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, PEPS_LIST_URL
from outputs import control_output
from utils import find_tag, get_response, list_dict_compare, validate_status


def pep(session):
    response = get_response(session, PEPS_LIST_URL)
    if not response:
        return

    soup = bs(response.text, "lxml")

    main_section = find_tag(soup, "section", attrs={"id": "index-by-category"})
    pep_sections = main_section.find_all("section")

    results = [("Статус", "Общее количество")]
    seen = set()
    for key, values in EXPECTED_STATUS.items():
        for value in values:
            if value not in seen:
                results.append((value, 0))
                seen.add(value)
    seen.clear()
    results.append(("TOTAL", 0))

    for section in tqdm(pep_sections):
        table = section.find("table")
        for strings in table.find_all("tr"):
            cells = strings.find_all("td")
            if len(cells) > 0:
                first_column_tag = cells[0]
                preview_status = first_column_tag.text[1:]

                second_column_tag = cells[1]
                href = second_column_tag.a["href"]
                pep_detail_url = urljoin(PEPS_LIST_URL, href)
                response = get_response(session, pep_detail_url)
                soup = bs(response.text, "lxml")

                list_info = find_tag(
                    soup, "dl", attrs={"class": "rfc2822 field-list simple"}
                )
                status_tag = list_info.find(
                    lambda tag: tag.name == "dt"
                    and tag.text == "Status:"
                    or tag.text == "Status"
                )
                detail_status = status_tag.find_next_sibling().text
                if validate_status(preview_status):
                    results = list_dict_compare(
                        preview_status, 
                        detail_status, pep_detail_url, results
                    )
    return results


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, "whatsnew/")

    response = get_response(session, whats_new_url)
    if not response:
        return

    soup = bs(response.text, "lxml")

    main_div = find_tag(
        soup, "section", attrs={"id": "what-s-new-in-python"}
        )
    div_with_ul = find_tag(
        main_div, "div", attrs={"class": "toctree-wrapper"}
        )
    sections_by_python = div_with_ul.find_all(
        "li", attrs={"class": "toctree-l1"}
    )

    results = [("Ссылка на статью", "Заголовок", "Редактор, Автор")]

    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, "a")
        href = version_a_tag["href"]
        version_link = urljoin(whats_new_url, href)

        response = get_response(session, version_link)
        if not response:
            continue

        soup = bs(response.text, "lxml")
        h1 = find_tag(soup, "h1")
        dl = find_tag(soup, "dl")
        dl_text = dl.text.replace("\n", "")
        results.append((version_link, h1.text, dl_text))

    return results


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    if not response:
        return

    soup = bs(response.text, "lxml")

    sidebar = find_tag(soup, "div", attrs={"class": "sphinxsidebar"})
    ul_tags = sidebar.find_all("ul")

    for ul in ul_tags:
        if "All versions" in ul.text:
            a_tags = ul.find_all("a")
            break
    else:
        raise Exception("Не найден список c версиями Python")

    results = [("Ссылка на документацию", "Версия", "Статус")]
    pattern = r"Python (?P<version>\d\.\d+) \((?P<status>.*)\)"

    for a_tag in a_tags:
        link = a_tag["href"]

        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ""

        results.append((link, version, status))

    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, "download.html")

    response = get_response(session, downloads_url)
    if not response:
        return

    soup = bs(response.text, "lxml")

    table = find_tag(soup, "table", attrs={"class": "docutils"})
    pdf_a4_tag = find_tag(table, "a", {"href": re.compile(r".+pdf-a4\.zip$")})
    pdf_a4_link = pdf_a4_tag["href"]
    archive_url = urljoin(downloads_url, pdf_a4_link)

    filename = archive_url.split("/")[-1]
    download_dir = BASE_DIR / "downloads"
    download_dir.mkdir(exist_ok=True)
    archive_path = download_dir / filename

    response = session.get(archive_url)
    with open(archive_path, "wb") as file:
        file.write(response.content)

    logging.info(f"Архив был загружен и сохранён: {archive_path}")


MODE_TO_FUNCTION = {
    "whats-new": whats_new,
    "latest-versions": latest_versions,
    "download": download,
    "pep": pep,
}


def main():
    configure_logging()
    logging.info("Парсер запущен!")

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()

    logging.info(f"Аргументы командной строки: {args}")

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)

    if results is not None:
        control_output(results, args)

    logging.info("Парсер завершил работу.")


if __name__ == "__main__":
    main()
