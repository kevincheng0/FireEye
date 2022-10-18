import ast
import logging
import argparse
import sys
import os
import psycopg2
import psycopg2.extras
import config
from tqdm import tqdm

def parse_args():
    parser = argparse.ArgumentParser(description='Global Fire Map')
    parser.add_argument('-d', action='store_true',
                        help='Enable debug logs')
    parser.add_argument('countries', metavar='countries', type=str, nargs='+',
                        help='Country codes to query')
    return parser.parse_args()

def db_connect():
    conn = psycopg2.connect(
        host=config.host,
        port=config.port,
        database=config.database,
        user=config.user,
        password=config.password
    )
    return conn

def db_points_within(countries, cursor, all_countries=False):
    points = []
    if all_countries:
        cursor.execute('''SELECT
            ST_AsGeoJSON(points.geom),
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
                ON ST_WITHIN(points.geom, countries.geom);
        ''')
        points.extend(cursor.fetchall())
    else:
        for country in countries:
            cursor.execute('''SELECT
                ST_AsGeoJSON(points.geom),
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
        loc = ast.literal_eval(point[0])['coordinates']
        point_dict = {
            'location': loc,
            'bright_ti4': point[1],
            'scan': point[2],
            'track': point[3],
            'acq_date': point[4],
            'acq_time': point[5],
            'satellite': point[6],
            'instrument': point[7],
            'confidence': point[8],
            'version': point[9],
            'bright_ti5': point[10],
            'frp': point[11],
            'daynight': point[12],
        }
        ret.append(point_dict)

    return ret


if __name__ == '__main__':
    args = parse_args()
    if args.d:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.DEBUG)

    countries = ', '.join(map(lambda x: f"'{x.upper()}'", args.countries))

    conn = db_connect()
    cursor = conn.cursor()
    ret = db_points_within(countries, cursor)
    conn.close

    print(ret)

