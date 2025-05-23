"""Модуль для парсинга маршрутов с сайта и сохранения их в JSON krimscoe_atp_routes."""

import json
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup, Tag


def parse_atp_routes(output_file: str = 'krimscoe_atp_routes.json') -> list[dict] | None:
    """Фунция парсит маршруты автобусов."""
    url = 'https://atp-tek.com/marshrutyi/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }

    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    routes = []
    panels = soup.select('div#accordion_left div.panel, div#accordion_right div.panel')

    for panel in panels:
        route = _parse_single_route(panel)
        if route:
            routes.append(route)

    with Path.open(output_file, 'w', encoding='utf-8') as f:
        json.dump(routes, f, ensure_ascii=False, indent=2)

    return routes


def _parse_single_route(panel: Tag) -> dict:
    route = {}
    title_tag = panel.select_one('h4.panel-title a')

    if not title_tag:
        return {}

    title = title_tag.get_text(strip=True)
    route['title'] = title
    match = re.search(r'№(\d+$[^)]*$|\d+)', title)
    route['number'] = match.group(0) if match else ''

    first_p = panel.select_one('div.panel-body > p:first-child')
    if first_p:
        has_strong = first_p.find('strong') is not None
        has_no_schedule_tags = first_p.find('b') is None and first_p.find('span') is None
        if has_strong or has_no_schedule_tags:
            route['description'] = first_p.get_text(strip=True)

    paragraphs = panel.select('div.panel-body > p')
    schedule_items = paragraphs[1:] if 'description' in route else paragraphs
    route['schedule'] = _parse_schedule(schedule_items)

    return route


def _parse_schedule(schedule_items: Tag) -> list[dict]:
    schedule = []
    current_schedule = {}

    for item in schedule_items:
        spans = item.select('span')
        if item.find('b'):
            if current_schedule:
                schedule.append(current_schedule)

            schedule_text = item.get_text()
            parts = schedule_text.split(':', 1) if ':' in schedule_text else [schedule_text, '']

            current_schedule = {
                'departure_info': parts[0].strip(),
                'times': [span.get_text(strip=True) for span in spans],
            }
        elif current_schedule:
            current_schedule['times'].extend([span.get_text(strip=True) for span in spans])

        if current_schedule:
            schedule.append(current_schedule)

    return schedule
