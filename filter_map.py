import ast
import logging
import argparse
import update_db
from tqdm import tqdm

def parse_args():
    parser = argparse.ArgumentParser(description='Global Fire Map')
    parser.add_argument('-d', action='store_true',
                        help='Enable debug logs')
    parser.add_argument('countries', metavar='countries', type=str, nargs='+',
                        help='Country codes to query')
    return parser.parse_args()

def db_points_within(countries, cursor, all_countries=False):
    points = []
    if all_countries:
        cursor.execute('''SELECT
            points.geom,
            points.lat,
            points.lng,
            points.bright_ti4,
            points.scan,
            points.track,
            points.acq_date,
            points.acq_time,
            points.satellite,
            points.instrument,
            points.confidence,
            points.version,
            points.bright_ti5,
            points.frp,
            points.daynight
            FROM points;
        ''')
        points.extend(cursor.fetchall())
    else:
        for country in countries:
            print(country)
            cursor.execute('''SELECT
                points.geom,
                points.lat,
                points.lng,
                points.bright_ti4,
                points.scan,
                points.track,
                points.acq_date,
                points.acq_time,
                points.satellite,
                points.instrument,
                points.confidence,
                points.version,
                points.bright_ti5,
                points.frp,
                points.daynight
                FROM points
                JOIN countries
                    ON ST_WITHIN(points.geom, countries.geom)
                    AND countries.iso_a3 = %s;
            ''', (country,))
            points.extend(cursor.fetchall())

    ret = []
    for point in tqdm(points):
        point_dict = {
            'lat': point[1],
            'lng': point[2],
            'bright_ti4': point[3],
            'scan': point[4],
            'track': point[5],
            'acq_date': point[6],
            'acq_time': point[7],
            'satellite': point[8],
            'instrument': point[9],
            'confidence': point[10],
            'version': point[11],
            'bright_ti5': point[12],
            'frp': point[13],
            'daynight': point[14],
        }
        ret.append(point_dict)

    return ret


if __name__ == '__main__':
    args = parse_args()
    if args.d:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.DEBUG)

    countries = map(lambda x: f"{x.upper()}", args.countries)

    conn = update_db.db_connect()
    cursor = conn.cursor()
    ret = db_points_within(countries, cursor, True)
    conn.close

    print(ret)

