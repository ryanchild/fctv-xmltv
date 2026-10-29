#!/usr/bin/env python3.9

from datetime import datetime
import sys
import requests
import logging
from xmltv import xmltv_helpers
from xmltv.models import xmltv
from pathlib import Path


def get_schedule_from_cablecast(day):
    """
    Retrieve the schedule from the Fort Collins Government (FCGov) Cablecast JSON API.

    Uses the Remix loader data endpoint which returns exact start and end datetimes
    for every schedule item, avoiding the need to infer end times from the next
    programme's start time.

    Args:
        day (datetime): The date for which to retrieve the schedule.

    Yields:
        tuple: A tuple containing the start datetime, end datetime, and program title.
    """
    url = make_fcgov_url(day)
    response = requests.get(url, headers={'Accept': 'application/json'})
    response.raise_for_status()
    data = response.json()

    for item in data.get('schedule', {}).get('scheduleItems', []):
        title = item['title']
        start = datetime.fromisoformat(item['runDateTime'])
        end = datetime.fromisoformat(item['endDateTime'])
        logging.info(f'{start}: {title}')
        yield start, end, title


def make_fcgov_url(day):
    """
    Generate the Cablecast JSON API URL for the given day's schedule.

    The URL uses the Remix _data query parameter to retrieve the schedule loader
    data as JSON directly, without parsing HTML.

    Args:
        day (datetime or None): The date for which to generate the URL. If None, the current date is used.

    Returns:
        str: The generated URL for the specified date.
    """
    if day is None:
        day = datetime.now()
    date = day.strftime('%Y-%m-%d')
    url = (
        f'https://reflect-vod-fcgov.cablecast.tv/internetchannel/schedule'
        f'?currentDay={date}&site=1&_data=routes%2F_shell.schedule'
    )
    return url


def make_program(start_time, end_time, title):
    """
    Create an XMLTV program entry.

    Args:
        start_time (datetime): The start time of the program.
        end_time (datetime): The end time of the program.
        title (str): The title of the program.

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
        title=title
    )
    return program


def main():
    """
    Main function to generate the XMLTV file for Fort Collins TV.

    Retrieves the schedule for the next three days, processes the schedule,
    and writes the XMLTV file.
    """
    tv = xmltv.Tv()
    channel = xmltv.Channel(
        id='FCTV',
        display_name=['Fort Collins TV']
    )
    tv.channel.append(channel)

    for i in list(range(3)):
        day = datetime.now().replace(day=datetime.now().day + i)
        for start, end, title in get_schedule_from_cablecast(day):
            program = make_program(start, end, title)
            tv.programme.append(program)

    xmltv_file = Path('./fctv.xml')
    xmltv_helpers.write_file_from_xml(xmltv_file, tv)


if __name__ == '__main__':
    sys.exit(main())
