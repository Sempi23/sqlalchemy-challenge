# Import the dependencies.

import warnings
warnings.filterwarnings('ignore')

import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement 
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(bind=engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def Welcome():
    """List all available api routes"""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Retrieve the last 12 months of precipitation data and convert it to a JSON response."""
    # Calculate the date 1 year ago from the last data point in the database.
    recent_data_point = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Extract the date from the Row object 
    recent_date = recent_data_point[0]  

    # Calculate the date one year ago
    year_ago = dt.datetime.strptime(recent_date, "%Y-%m-%d") - dt.timedelta(days=365)

    # Perform a query to retrieve precipitation data for the last year
    date_precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago)

    session.close()

    precipitation = {date: prcp for date, prcp in date_precipitation}

    return jsonify(precipitation)


@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    stations = session.query(Station.station).all()
    station_names = [station[0] for station in stations]
    return jsonify(station_names)


@app.route("/api/v1.0/tobs")
def tobs():

# Calculate date one year ago from the latest measurement
  recent_data_point = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
  recent_date = recent_data_point[0]
  year_ago = dt.datetime.strptime(recent_date, "%Y-%m-%d") - dt.timedelta(days=365)

  # Find the most active station (assuming 'station' is the column name)
  most_active_station = (
      session.query(Measurement.station, func.count(Measurement.id))
      .group_by(Measurement.station)
      .order_by(func.count(Measurement.id).desc())
      .first()
  )
  station_id = most_active_station[0]

  # Query temperatures from the most active station for the last year
  station_data = (
      session.query(Measurement.date, Measurement.tobs)
      .filter(Measurement.station == station_id)
      .filter(Measurement.date >= year_ago)
      .all()
  )

  # Convert the query result to a list of dictionaries
  temps = [{"date": date, "tobs": temp} for date, temp in station_data]
  return jsonify(temps)



@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def statend(start, end=None):
    """Retrieve a JSON list of the minimum, average, and maximum temperature for a specified start-end range."""
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    end_date = dt.datetime.strptime(end, "%Y-%m-%d")

    # Query for temperature statistics
    temperatures = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs),
    ).filter(Measurement.date>=start_date).filter(Measurement.date<=end_date).all()
  
    startend_temp_list = list(np.ravel(temperatures))
    
    return jsonify(startend_temp_list)

    

if __name__ == "__main__":
    app.run(debug=True)

    session.close()




