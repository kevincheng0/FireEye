from flask import Flask, jsonify, request
import filter_map
import model
import update_db

app = Flask(__name__)

@app.route("/")
def main():
    return "Main Page"


@app.route("/api/nrt/wildfire", methods=['GET'])
def wildfire():
    countries = request.get_json()["countries"]
    ret = {
        "success": False,
        "points": []
    }

    if countries:
        conn = update_db.db_connect()
        cursor = conn.cursor()

        if countries[0] == "*":
            points = filter_map.db_points_within(countries, cursor, all_countries=True)
        else:
            points = filter_map.db_points_within(countries, cursor)

        ret["points"] = points
        ret["success"] = True
        conn.close()

    return jsonify(ret)

@app.route("/api/model", methods=['GET'])
def model():
    req = request.get_json()
    fwd_rate = model.basic_spread_rate(
        oven_dry_fuel_load=req.oven_dry_fuel_load,
        surface_area_vol_ratio=req.surface_area_vol_ratio,
        packing_ratio=req.packing_ratio,
        dead_fuel_moisture_extinction=req.dead_fuel_moisture_extinction,
        fuel_bed_depth=req.fuel_bed_depth,
        slope=req.slope,
        midflame_wind_speed=req.wind,
        moisture_fraction=req.moisture_fraction
    )
    ret = {
        "success": False,
        "rates": [fwd_rate]
    }
    return ret

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000)
