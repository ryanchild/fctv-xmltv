import pandas as pd
from zoneinfo import ZoneInfo
from datetime import datetime
import sys
import requests
import io
from xmltv import xmltv_helpers
from xmltv.models import xmltv
from pathlib import Path

def make_fcgov_url():
    date = datetime.now().strftime('%Y-%m-%d')
    url = f'https://www.fcgov.com/fctv/ajax-schedule-helper.php?date={date}'
    return url

def get_schedule(url, last_program_end) -> pd.DataFrame:
    data = requests.get(url)
    html = io.StringIO(data.text)
    df = pd.read_html(html, skiprows=1, index_col=0, parse_dates=True)[0]
    df.rename_axis('start', inplace=True)
    df = df.drop(df.columns[[1]], axis=1)
    df.columns = ['description']
    df.reset_index(inplace=True)
    df['end'] = df.start.shift(-1, fill_value=last_program_end)
    return df

def make_program(start_time, end_time, description):
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
    url = make_fcgov_url()
    midnight = pd.Timestamp.now().ceil('D').to_pydatetime()
    try:
        schedule = get_schedule(url, midnight)
    except ValueError:
        print("no schedule found.  not posted yet?")
        return 1

    tv = xmltv.Tv()
    channel = xmltv.Channel(
        id='FCTV',
        display_name=['Fort Collins TV']
    )
    tv.channel.append(channel)

    for _, row in schedule.iterrows():
        start = row['start'].replace(tzinfo=ZoneInfo('US/Mountain'))
        end = row['end'].replace(tzinfo=ZoneInfo('US/Mountain'))
        description = row['description']
        program = make_program(start, end, description)
        tv.programme.append(program)

    xmltv_file = Path('./fctv.xml')
    xmltv_helpers.write_file_from_xml(xmltv_file, tv)

if __name__ == '__main__':
    sys.exit(main())