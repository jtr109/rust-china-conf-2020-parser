import datetime
import re
import typing

import pydantic
import requests
from bs4 import BeautifulSoup


class Lesson(pydantic.BaseModel):
    start_time: datetime.time
    end_time: datetime.time
    title: str
    detail: str


class Schedule(pydantic.BaseModel):
    date: datetime.date
    lessons: typing.List[Lesson]


def get_html(url: str) -> str:
    response = requests.get(url=url)
    response.raise_for_status()
    return response.content.decode()


def parse_html(html_doc: str) -> BeautifulSoup:
    return BeautifulSoup(html_doc, 'html.parser')


def find_dom_with_main_tag_and_schedule_class(soup: BeautifulSoup) -> BeautifulSoup:
    return soup.find('main', class_='schedule')


def zip_schedule_of_each_day(main_dom: BeautifulSoup) -> typing.Iterable[typing.Tuple[BeautifulSoup, BeautifulSoup]]:
    date_doms: BeautifulSoup = main_dom.findChildren(class_='date', recursive=False)
    schedule_content_doms: BeautifulSoup = main_dom.findChildren(class_='schedule_content', recursive=False)
    return zip(date_doms, schedule_content_doms)


def parse_time(time_string: str) -> datetime.time:
    return datetime.datetime.strptime(time_string, '%H:%M').time()


def parse_detail(detail: BeautifulSoup) -> str:
    return detail.text.strip().replace('\r', '').replace('\t', '')


def group_lesson_doms(schedule_content_dom: BeautifulSoup):
    i = 0
    doms = list(schedule_content_dom.findChildren(recursive=False))
    while i < len(doms):
        yield Lesson(
            start_time=parse_time(doms[i].string),
            end_time=parse_time(doms[i+1].string),
            title=doms[i+2].string,
            detail=parse_detail(doms[i+5]),
        )
        i += 6


def parse_date(date_string: str) -> datetime.date:
    pattern = r'\s*Day\s\d+:\s(\w+)\s(\d+),\s(\d+)\s.+'
    m = re.match(pattern, date_string)
    if not m:
        raise Exception(f'unexpected date string: {date_string}')
    month, day, year = m.groups()
    date_pattern = '%B %d, %Y'
    return datetime.datetime.strptime(f'{month} {day}, {year}', date_pattern).date()


def daily_schedule_dom_to_schedule(date_dom: BeautifulSoup, schedule_content_dom: BeautifulSoup) -> Schedule:
    return Schedule(
        date=parse_date(date_string=date_dom.string),
        lessons=list(group_lesson_doms(schedule_content_dom=schedule_content_dom))
    )


def convert_main_dom_to_schedule_list(main_dom: BeautifulSoup) -> typing.Iterable[Schedule]:
    return [
        daily_schedule_dom_to_schedule(date_dom=date_dom, schedule_content_dom=schedule_content_doms)
        for (date_dom, schedule_content_doms)
        in zip_schedule_of_each_day(main_dom=main_dom)
    ]


def parse_schedule() -> typing.Iterable[Schedule]:
    schedule_url = 'https://2020conf.rustcc.cn/schedule.html'
    soup = parse_html(get_html(schedule_url))
    main_dom = find_dom_with_main_tag_and_schedule_class(soup=soup)
    return convert_main_dom_to_schedule_list(main_dom=main_dom)


if __name__ == "__main__":
    schedules = parse_schedule()
    print(schedules)
