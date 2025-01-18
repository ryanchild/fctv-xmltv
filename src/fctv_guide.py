#!/usr/bin/env python3.9

from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
import sys
import requests
import logging
from xmltv import xmltv_helpers
from xmltv.models import xmltv
from pathlib import Path
from bs4 import BeautifulSoup


def process_fcgov_schedule_time(day, time_str):
    """
    Convert a time string to a datetime object for a given day.

    Args:
        day (datetime): The date for which to combine the time.
        time_str (str): The time string to convert.

    Returns:
        datetime: The combined datetime object.
    """
    if time_str == 'Now':
        return datetime.now()
    time_format = "%I:%M %p"
    time_obj = datetime.strptime(time_str, time_format).time()
    return datetime.combine(day, time_obj)


def get_schedule_from_cablecast(day):
    """
    Retrieve the schedule from the Fort Collins Government (FCGov) video on demand service.

    Args:
        day (datetime): The date for which to retrieve the schedule.

    Yields:
        tuple: A tuple containing the start datetime, end datetime, and program title.
    """
    url = make_fcgov_url(day)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    schedule = []
    schedule_rows = soup.find_all('div', class_='schedule-row clearfix')
    for row in schedule_rows:
        program_time = row.find('div', class_='plaque').find(
            'div').get_text(strip=True)
        program_datetime = process_fcgov_schedule_time(day, program_time)
        program_title = row.find(
            'div', class_='schedule-container').find('div').get_text(strip=True)
        schedule.append([program_datetime, program_title])

    for i, (program_datetime, program_title) in enumerate(schedule):
        logging.log(logging.INFO, 
            f'{day.strftime("%Y-%m-%d")} {program_datetime}: {program_title}')
        if i + 1 < len(schedule):
            next_program_datetime = schedule[i + 1][0]
            program_end = next_program_datetime
            logging.log(logging.INFO, 
                f'Next program at {next_program_datetime.strftime("%Y-%m-%d %H:%M:%S")}')
        else:
            logging.log(logging.INFO, 'Last program of the day, assume length of 1 hour')
            program_end = program_datetime + timedelta(hours=1)
        yield program_datetime, program_end, program_title


def make_fcgov_url(day):
    """
    Generate a URL for the Fort Collins Government (FCGov) video on demand schedule.

    Args:
        day (datetime or None): The date for which to generate the URL. If None, the current date is used.

    Returns:
        str: The generated URL for the specified date.
    """
    if day is None:
        day = datetime.now()
    date = day.strftime('%Y-%m-%d')
    url = f'https://reflect-vod-fcgov.cablecast.tv/CablecastPublicSite/schedule?currentDay={date}&site=1'
    return url


def make_program(start_time, end_time, description):
    """
    Create an XMLTV program entry.

    Args:
        start_time (datetime): The start time of the program.
        end_time (datetime): The end time of the program.
        description (str): The description of the program.

    Returns:
        xmltv.Programme: The created program entry.
    """
    program = xmltv.Programme(
        channel='FCTV',
        start=start_time.strftime('%Y%m%d%H%M%S %z'),
        stop=end_time.strftime('%Y%m%d%H%M%S %z'),
        episode_num=xmltv.EpisodeNum(
            system="original-air-date",
            content=[start_time.strftime("%Y-%m-%d")]
        ),
        title=description
    )
    return program


def main():
    """
    Main function to generate the XMLTV file for Fort Collins TV.

    Retrieves the schedule for today and tomorrow, processes the schedule,
    and writes the XMLTV file.
    """
    tv = xmltv.Tv()
    channel = xmltv.Channel(
        id='FCTV',
        display_name=['Fort Collins TV']
    )
    tv.channel.append(channel)

    today = datetime.now()
    tomorrow = datetime.now().replace(day=datetime.now().day + 1)
    for day in [today, tomorrow]:
        for start, end, description in get_schedule_from_cablecast(day):
            start = start.replace(tzinfo=ZoneInfo('US/Mountain'))
            end = end.replace(tzinfo=ZoneInfo('US/Mountain'))
            program = make_program(start, end, description)
            tv.programme.append(program)

    xmltv_file = Path('./fctv.xml')
    xmltv_helpers.write_file_from_xml(xmltv_file, tv)


if __name__ == '__main__':
    sys.exit(main())
