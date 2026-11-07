#!/usr/bin/env python3

from datetime import datetime, timedelta
import sys
import requests
import logging
from xmltv import xmltv_helpers
from xmltv.models import xmltv
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)


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
    logging.info(f"Fetching schedule from {url}")
    try:
        response = requests.get(url, headers={'Accept': 'application/json'}, timeout=30)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        logging.warning(f"Failed to fetch schedule for {day.strftime('%Y-%m-%d')}: {e}")
        return

    schedule_items = data.get('schedule', {}).get('scheduleItems', [])
    logging.info(f"Found {len(schedule_items)} items for {day.strftime('%Y-%m-%d')}")

    for item in schedule_items:
        title = item.get('title')
        if not title:
            continue
        try:
            start = datetime.fromisoformat(item['runDateTime'])
            end = datetime.fromisoformat(item['endDateTime'])
        except (KeyError, ValueError) as err:
            logging.warning(f"Error parsing date in item {item}: {err}")
            continue
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

    Retrieves the schedule for today and the next two days, processes the schedule,
    and writes the XMLTV file.
    """
    tv = xmltv.Tv()
    channel = xmltv.Channel(
        id='FCTV',
        display_name=['Fort Collins TV']
    )
    tv.channel.append(channel)

    today = datetime.now()
    total_programs = 0

    for i in range(3):
        day = today + timedelta(days=i)
        for start, end, title in get_schedule_from_cablecast(day):
            program = make_program(start, end, title)
            tv.programme.append(program)
            total_programs += 1

    logging.info(f'Total programmes collected: {total_programs}')

    if total_programs == 0:
        logging.error('No programmes collected; aborting to avoid overwriting with empty guide data.')
        return 1

    output_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('./fctv.xml')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    xmltv_helpers.write_file_from_xml(output_path, tv)
    logging.info(f'Successfully wrote XMLTV file to {output_path}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
