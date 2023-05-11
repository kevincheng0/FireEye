import psycopg2
import json
import config

if __name__ == '__main__':
    conn = psycopg2.connect(
        host=config.host,
        port=config.port,
        database=config.database,
        user=config.user,
        password=config.password
    )
    cursor = conn.cursor()

    with open('countries.geojson', 'r') as f:
        data = json.load(f)

        values = []

        for feature in data["features"]:
            properties = feature["properties"]
            iso_a3 = properties["ISO_A3"]
            geom = json.dumps(feature["geometry"])
            name =  properties["ADMIN"]

            values.append((iso_a3, geom, name))

        args = ', '.join(cursor.mogrify('(%s, ST_GeomFromGeoJSON(%s), %s)', x).decode('utf-8') for x in values)
        cursor.execute("INSERT INTO countries (iso_a3, geom, name) VALUES " + args)

    conn.commit()
    conn.close()
