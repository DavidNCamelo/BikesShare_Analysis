'''
Created by David Camelo on 02/05/2025

Data cleaning for the dataset "trip_data.csv" for web visuals
'''
# Importing reuqired libraries
import pandas as pd


# Create a function to clean the dataset
class CleanData:
    def __init__(self, data):
        self.data = data


    def clean_data(self):
        '''Transforming the columns to datetime'''
        self.data['Start Date'] = pd.to_datetime(self.data['Start Date'])
        self.data['End Date'] = pd.to_datetime(self.data['End Date'])

        '''Create new columns for the hour of the day of the start and end of the trip'''
        self.data['Start Hour'] =self.data['Start Date'].dt.strftime('%H').astype(int) 
        self.data['End Hour'] =self.data['End Date'].dt.strftime('%H').astype(int)
        
        return self


    def replace_station(self):
        '''Replace station values based on new conditions'''
        start_station_replacements = {
            85: 23,
            86: 25,
            87: 49,
            88: 69,
            89: 72,
            90: 72
        }

        end_station_replacements = {
            85: 23,
            86: 25,
            87: 49,
            88: 69,
            89: 72,
            90: 72
        }

        for original, new in start_station_replacements.items():
            modify = (self.data['Start Station'] == original).sum()
            self.data['Start Station'].replace(original, new, inplace=True)
            print(f'{modify} items were modified from {original} to {new} in Start Station.')

        for original, new in end_station_replacements.items():
            modify = (self.data['End Station'] == original).sum()
            self.data['End Station'].replace(original, new, inplace=True)
            print(f'{modify} items were modified from {original} to {new} in End Station.')

        return self


    def get_data(self):
        ''''Return the cleaned dataframe'''
        return self.data