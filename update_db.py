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
    file_name = f'{date}_results.json'

    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM points;')
    conn.commit()

    template = '''
        INSERT INTO points (%s) VALUES %s;
    '''

    points = fetch_data(url)
    for point in points:
        lat = point['latitude']
        lng = point['longitude']
        columns = ['geom'] + list(point.keys())[2:]
        values = [f'Point({lng} {lat})'] + [point[column] for column in columns if column not in ['latitude', 'longitude', 'geom']]

        cursor.execute(template, (AsIs(','.join(columns)), tuple(values)))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    url = f'https://firms.modaps.eosdis.nasa.gov/api/area/csv/{config.key}/VIIRS_NOAA20_NRT/world/1'
    fetch_and_store(url)



