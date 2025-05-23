"""Модуль для парсинга ссылок на объявления с сайта и сохранения
их в JSON krimscoe_atp_advertisement.
"""

import json
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup


def parse_advertisement() -> list[dict[str, Any]]:
    """Парсит объявления с сайта и возвращает список словарей с данными."""
    url = 'https://atp-tek.com/obyavleniya/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,'
        ' like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    advertisement_cards = soup.select('div.col-xs-12.col-sm-6.col-md-4')

    advertisement = []

    for card in advertisement_cards:
        title_tag = card.select_one('div.our_blog_content a h3')
        link_tag = card.select_one('a[href]')
        date_tag = card.select_one('.b_date span')
        description_tag = card.select_one('div.our_blog_content p')

        announcement = {
            'title': title_tag.get_text(strip=True),
            'url': link_tag['href'],
            'date': date_tag.get_text(strip=True) if date_tag else None,
            'short_description': description_tag.get_text(strip=True) if description_tag else None,
        }
        advertisement.append(announcement)

    return advertisement


def save_to_json(data: list[dict[str, Any]], filename: str) -> None:
    """Сохраняет данные в JSON-файл."""
    with Path.open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main() -> None:
    """Основная функция вызывает парсер."""
    advertisement = parse_advertisement()

    save_to_json(advertisement, 'krimscoe_atp_advertisement.json')

if __name__ == '__main__':
    main()
