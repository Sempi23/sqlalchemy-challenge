# Import the dependencies.

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
        f"/api/v1.0/precipitaion<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

@app.route("/api/v1.o/precipitation")
def precipitation():
    """Retrieve the last 12 months of precipitation data and converts it to a JSON response """
   # Calculate the date 1 year ago from last data point in the database.
recent_data_point = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Extract the date from the Row object (ensure 'date' is the correct column name)
recent_date = recent_data_point[0]  # Access the first element (assuming 'date' is at index 0)
    
    # Calculate the date one year ago

year_ago = datetime.strptime(recent_date, "%Y-%m-%d") - dt.timedelta(days=365)

    # Perform a query to retrieve precipitation data for the last year
date_precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago)
    
session.close()

precipitation ={date:prcp for date, prcp in date_precipitation}
return jsonify(precipitation)


@app.route("/api/v1.0/stations")
def stations():
    """Return JSON list of stations from the dataset"""
    Station = base.classes.station

    all_stations = session.query(Station.station).all()
    # create list
    all_stations = {Station:name for station, name in all_stations}

    session.close()

    return jsonify(all_stations)

    
@app.route("/api/v1.o/tobs")
def tobs():
    """Returen a list of observed temperatures for most active station from previous year of data"""
    # Calculate the date 1 year ago from last data point in the database.
recent_data_point = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Extract the date from the Row object (ensure 'date' is the correct column name)
recent_date = recent_data_point[0]

    # Calculate the date one year ago

year_ago = datetime.strptime(recent_date, "%Y-%m-%d") - dt.timedelta(days=365)
 

    # List the stations and their counts in descending order.
most_active_stations = session.query(Station.station, func.count(Measurement.station)) \
                        .join(Measurement, Station.station == Measurement.station) \
                        .group_by(Station.station) \
                        .order_by(func.count(Measurement.station).desc()) \
                        .all()

    #Using the most active station id
    # Query the last 12 months of temperature observation data for this station and plot the results as a histogram
active_station_temp = session.query(Measurement.date, Measurement.tobs).\
                                    filter(Measurement.date >= year_ago).\
                                    filter(Measurement.station == "USC00519281")

active_station_df = pd.DataFrame(active_station_temp, columns=["Date", "Temperature"])

session.close() 
tobs_list = []
for station in active_station_temp:
    

return jsonify(active_station_df)


@app.route()

if __name__ == "__main__":
    app.run(debug=True)




