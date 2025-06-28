"""Модуль для парсинга объявлений с сайта и сохранения результатов
в JSON krimscoe_atp_full_advertisement.
"""

import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup


def parse_advertisements(
    input_file: str | None = None,
    output_file: str | None = None,
) -> list[dict] | None:
    """Парсит объявления из входного файла, извлекает содержимое по
    URL и сохраняет результат в выходной файл.
    """
    if input_file is None:
        input_file = str(Path(__file__).parent / 'krimscoe_atp_advertisement.json')
    if output_file is None:
        output_file = str(Path(__file__).parent / 'krimscoe_atp_full_advertisement.json')

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    with Path.open(input_file, encoding='utf-8') as f:
        advertisements = json.load(f)

    results = []

    for index, ad in enumerate(advertisements, 1):
        print(f"Processing ad {index}/{len(advertisements)}")
        content = _parse_single_advertisement(ad['url'], headers)
        if content:
            content.update({
                'date': ad.get('date'),
                'original_title': ad.get('title'),
            })
            results.append(content)

    with Path.open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    return results


def _parse_single_advertisement(url: str, headers: dict) -> dict | None:
    """Загружает страницу объявления по URL и извлекает содержимое."""
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    content_section = soup.select_one('section.error_area.text_area')

    if content_section is None:
        return None

    for element in content_section(['script', 'style', 'div.b_date']):
        element.decompose()

    title_element = soup.select_one('section.banner_area h1')
    title_text = title_element.get_text(strip=True) if title_element else None

    return {
        'title': title_text,
        'text': content_section.get_text('\n', strip=True),
        'original_url': url,
    }
