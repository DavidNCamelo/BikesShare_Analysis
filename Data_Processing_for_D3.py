import pandas as pd
import json
from CleaningTrips import CleanData

def process_data():
    # Load data
    trips = pd.read_csv('trip_data.csv', parse_dates=['Start Date', 'End Date'])
    stations = pd.read_csv('station_data.csv')

    # Clean and transform data
    trips = CleanData(trips).clean_data().replace_station().get_data()

    # Merge station names
    trips = trips.merge(stations[['Id', 'Name']], left_on='Start Station', right_on='Id', how='left')
    trips.rename(columns={'Name': 'start_station_name'}, inplace=True)
    
    trips = trips.merge(stations[['Id', 'Name']], left_on='End Station', right_on='Id', how='left')
    trips.rename(columns={'Name': 'end_station_name'}, inplace=True)

    # Extract year-month for filtering
    trips['Year-Month'] = trips['Start Date'].dt.to_period('M').astype(str)
    trips['Start Hour'] = trips['Start Date'].dt.hour
    trips['End Hour'] = trips['End Date'].dt.hour

    # Select relevant columns
    trips = trips[['Year-Month', 'start_station_name', 'end_station_name', 'Start Hour', 'End Hour']]
    
    # Save as JSON
    trips.to_json('trips_data2.json', orient='records', indent=2)
    print("Data processed and saved as trips_data.json")

if __name__ == "__main__":
    process_data()
