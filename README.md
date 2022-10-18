
# FireEye

A near real-time wildfire API written in Python for storing and filtering thermal hotspots detected by the VIIRS sensor aboard the Suomi NPP and NOAA-20 satellites.
The satellites and sensors can be changed by editing the API endpoint [here](https://firms.modaps.eosdis.nasa.gov/api/area).

(readme still in progress)
## Run Locally

Setup Postgres and PostGIS to store the satellite data.

Set update_db.py to run every 3 hours via cron.

Install the requirements and run the Flask API

```bash
  python3 api.py
```

Optionally, host the API with Gunicorn and Nginx with this [guide](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04)


## Configuration

To make this API work, you will need to add the your database configurations and NASA API key  to a config.py file:

### Database:
`host`: database host\
`port`\
`database`: database name\
`user`\
`password`

### NASA API:
`key`: sign up for a key [here](https://firms.modaps.eosdis.nasa.gov/api/area) by clicking "Get MAP_KEY" at the bottom of the page

