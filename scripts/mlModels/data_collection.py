import os
import requests
from datetime import date
from wwo_hist import retrieve_hist_data
from scripts.mlModels.windDir_NN import windDir
from scripts.mlModels.windSpeed_SVR import windSpeed
from scripts.mlModels.data_preprocessing import preprocessing


def collect(location, api_key):

    api_key = api_key
    start_date = '01-JUL-2008'
    end_date = date.today().strftime("%d-%b-%Y").upper()
    frequency = 24

    def getHistoricalData(location):
        retrieve_hist_data(api_key, [location], start_date, end_date,
                           frequency, location_label=False, export_csv=True, store_df=False)

    getHistoricalData(location)

    preprocessing(location)
    print("\n\n\n\nPreprocessing completed!\n\n")

    print("Predicting wind direction...\n\n\n\n")
    windDir(location)
    print("\n\n\n\nWind direction prediction completed!\n\n")

    print("Predicting wind speed...\n\n\n\n")
    windSpeed(location)
    print("\n\n\n\nWind speed prediction completed!\n\n")
