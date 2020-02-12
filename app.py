import numpy as np
import datetime as dt
from datetime import timedelta

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, and_

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################


@app.route("/")
def welcome():
    """List all available api routes."""
		
    return(
		f"Available Routes:<br/>"
		f"/api/v1.0/precipitation<br/>"
		f"/api/v1.0/stations<br/>"
		f"/api/v1.0/tobs<br/>"
		f"/api/v1.0/temp/start/end"
	)
	
	
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    prev_year = dt.date(2017,8,23) - dt.timedelta(365)
	   
    #Query database to get precipitation data by date
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()
	

    # Create a dictionary from the row data and append to precipitation data
    precip = {date:prcp for date, prcp in results}
    
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
	
	#Query db to get a list of stations
    results=session.query(Station.station).all()
    
	
	#Transform query results into list
    station_list = list(np.ravel(results))
	
    #Output list
    return jsonify(station_list)	

@app.route("/api/v1.0/tobs")
def temperatures():
    
    #Determine latest date
    latest_date = session.query(Measurement).order_by(Measurement.date.desc()).limit(1)
    
    for date in latest_date:
        latest_date = date.date
    
    latest_date = dt.datetime.strptime(latest_date, "%Y-%m-%d")
        
    one_year_before = latest_date - timedelta(days=365)
    
    #Query DB to get dates and temperatures 1 year before 
    #Join Station and Measurement table
    results = session.query(Station.date, Measurement.tobs).\
    join(Measurement.station).filter(and_(Station.date <= latest_date, Station.date >= one_year_before)).all()
    
     

    #list
    temps_list = []
    
    for result in results:
        temps_list.append(result[0][1])

            
    #Jsonify
    return jsonify(temps_list)

@app.route("/api/v1.0/temp/<start>")
        
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:

        results = session.query(*sel).\
        filter(Measurement.date >= start).all()
        temps = list(np.ravel(results)) 
        return jsonify(temps) 
	   
	   
    results = session.query(*sel).\
    filter(Measurement.date >= start).\
    filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps)
	
		
	
if __name__ == '__main__':
    app.run(debug=True)

