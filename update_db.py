import psycopg2
import logging
import requests
import config
from psycopg2.extensions import AsIs
from datetime import datetime

logging.basicConfig(level=logging.WARNING)
FETCH = True

def db_connect():
    conn = psycopg2.connect(
        host=config.host,
        port=config.port,
        database=config.database,
        user=config.user,
        password=config.password
    )
    return conn

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def fetch_data(url):
    logging.info('Fetching data... %s', url)
    r = requests.get(url)

    logging.info('Processing data...')
    text = r.text.split('\n')
    headers = text[0].split(',')
    data = [row.split(',') for row in text[1:]]  # [lat, lnt, ...], [lat, lng, ...]

    ret = []
    for row in data:
        d = {k: v for k, v in zip(headers, row)}
        ret.append(d)

    return ret

def fetch_and_store(url):
    date = datetime.now().strftime('%Y-%m-%d')

    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM points;')
    conn.commit()

    points = fetch_data(url)
    values = []
    for point in points:
        values.append([x for x in point.values()])

    for value_chunk in chunks(values, 50):
        args = ', '.join(f'(ST_SetSRID(ST_MakePoint({x[0]}, {x[1]}), 4326),' + cursor.mogrify('%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', x).decode('utf-8') for x in value_chunk)
        cursor.execute("INSERT INTO points VALUES " + args)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    url = f'https://firms.modaps.eosdis.nasa.gov/api/area/csv/{config.key}/VIIRS_NOAA20_NRT/world/2'
    fetch_and_store(url)

