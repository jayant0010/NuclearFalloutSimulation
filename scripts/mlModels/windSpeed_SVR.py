import os
import datetime
import numpy as np
import pandas as pd
from datetime import date
from sklearn.svm import SVR
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split


def windSpeed(location):
    filename = location+"_preprocessed.csv"
    df = pd.read_csv(filename)

    data = pd.DataFrame(
        columns=['day', 'month', 'WindSpeed']
    )

    data['day'] = df['day']
    data['month'] = df['month']

    data['WindSpeed'] = df['WindspeedKmph']
    x = data.iloc[:, :-1]
    y = data['WindSpeed']

    xtrain, xtest, ytrain, ytest = train_test_split(
        x, y, test_size=0.20, random_state=4)

    svr = SVR(kernel='rbf', gamma='auto', C=100.0, epsilon=2.2, verbose=1)
    svr.fit(xtrain, ytrain)

    last_date = df['date'].iloc[-1]
    last_date = datetime.datetime.strptime(last_date, "%Y-%m-%d").date()

    pred_date = []

    for i in range(1, 91):
        pred_date.append(last_date + datetime.timedelta(days=i))

    pred_input = [[] for i in range(90)]

    i = 0

    for j in pred_date:
        pred_input[i].append(j.day)
        pred_input[i].append(j.month)
        i += 1

    sample = pd.DataFrame(
        columns=['day', 'month'],
        data=pred_input
    )

    sample_p = svr.predict(sample)
    sample_p = sample_p.reshape(-1, 1)

    scaler = MinMaxScaler(feature_range=(4, 40))

    sample_p = scaler.fit_transform(sample_p)
    sample_p = sample_p.round()
    sample_p = sample_p.astype('int32')
    sample_p = sample_p.reshape(-1)

    pred_filename = location+".csv"
    filepath = "data/"+pred_filename

    pred_data = pd.read_csv(filepath)
    pred_data['speed'].iloc[-90:] = sample_p

    pred_data.to_csv(filepath, index=False)

    os.remove(filename)
