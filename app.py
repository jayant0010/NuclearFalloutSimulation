from flask import Flask, render_template, request
from scripts.main import simulate_plume_model
from os import path
import datetime
import os

# PyFlask instance to render HTML pages and simulation
app = Flask(__name__, static_folder='static')

# Path to the final output video
anim_path = 'static\\videos\simulation.mp4'

# Map used as simulation background
map_path = 'static\images\map.png'

# Rendering index.html on startup
@app.route("/")
def index():
    return render_template('index.html', visibility="hidden")

# Function to accept Form Input
@app.route("/", methods=['POST'])
def disp_output():
    loc = request.form['inputLoc']

    loc_lat = request.form['locLat']
    loc_lng = request.form['locLng']

    date = request.form['dateInput']

    # The coordinates of input location
    latLng = loc_lat + ',' + loc_lng

    # Date entered by user
    month, day, year = [int(i) for i in date.split('/')]

    print("\nLocation:", loc, "\nCoordinates:", latLng)
    print("Day:", day, "\nMonth:", month, "\nYear:", year)

    # Removing existing output, if present.
    if path.exists(anim_path):
        os.remove(anim_path)

    if path.exists(map_path):
        os.remove(map_path)

    # Function to start simulation
    fig, ax, anim = simulate_plume_model(
        latLng=latLng, start_datetimeObject=datetime.datetime(year, month, day))

    # Rendering the output video
    return render_template('index.html', output_path=anim_path, visibility="visible")


if __name__ == "__main__":
    app.run()
