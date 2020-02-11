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
		f"/api/v1.0/<start><br/>"
		"/api/v1.0/<start>/<end><br/>"
	)
	
	
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session from Python to the DB
    session = Session(engine)
    
    #Query database to get precipitation data by date
    results = session.query(Measurement).all()
	
	#Close session
    session.close()
	
    # Create a dictionary from the row data and append to precipitation data
    precipitation_data = []
    for result in results:
        prcp_data = {}
        prcp_data["date"] = result.date
        prcp_data["prcp"] = result.prcp
        precipitation_data.append(prcp_data)
		
    return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session from Python to the DB
    session = Session(engine)
	
	#Query db to get a list of stations
    results=session.query(Station.station).all()
    
    #Close session
    session.close()
	
	#Transform query results into list
    station_list = list(np.ravel(results))
	
    #Output list
    return jsonify(station_list)	

@app.route("/api/v1.0/tobs")
def temperatures():
    #Create our session from Python to the DB
    session = Session(engine)
    
    #Determine latest date
    latest_date = session.query(Measurement).order_by(Measurement.date.desc()).limit(1)
    
    for date in latest_date:
        latest_date = date.date
    
    latest_date = dt.datetime.strptime(latest_date, "%Y-%m-%d")
        
    one_year_before = latest_date - timedelta(days=365)
    
    #Query DB to get dates and temperatures 1 year before 
    #Join Station and Measurement table
    results = session.query(Station.date, Measurement.tobs).\
    .join(Measurement.station).filter(and_(Station.date <= latest_date, Station.date >= one_year_before))
    
     #Close session
    session.close()

    #list
    temps_list = []
    
    for result in results:
        temps_list.append(result[0][1])

            
    #Jsonify
    return jsonify(temps_list)

@app.route("/api/v1.0/start:Y-M-D")
def after_start(start_date):
    
    #Get user input for start date   
    start_date = input("Please enter a date in the following format: YYYY-MM-DD")
    
    #Query DB    
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    join(Station.station).filter(Measurement.date >= start_date).all()
    
    #Close session
    session.close()
    
    #Results to list
    start_list = list(np.ravel(results))
    
    #Return as JSON
    return jsonify(start_list)
        
@app.route("/api/v1.0/start:Y-M-D/end:Y-M-D")
def date_range(start_date, end_date):
    
    start_date = input("Please enter a date in the following format: YYYY-MM-DD")
    end_date = input("Please enter a date in the following format: YYYY-MM-DD")

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    join(Station.station).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
	
    #Close session
    session.close()
	
    #Results to list
    range_list = list(np.ravel(results))
    
    #Return as JSON
    return jsonify(range_list)
	
	
	
if __name__ == '__main__':
    app.run(debug=True)

