import datetime
import numpy as np
import pandas as pd
from datetime import date
from tensorflow.keras.models import Sequential
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.layers import Activation, Dense
from tensorflow_core.python.keras.utils import np_utils


def windDir(location):
    filename = location+"_preprocessed.csv"

    df = pd.read_csv(filename)
    data = pd.DataFrame(
        columns=['day', 'month', 'WindDir']
    )

    data['day'] = df['day']
    data['month'] = df['month']
    data['WindDir'] = df['WindDir']

    le_pred = LabelEncoder()
    y = le_pred.fit_transform(data.WindDir)
    y = np_utils.to_categorical(y)

    y = y.astype('int32')
    out_classes = y.shape[1]

    model = Sequential()

    model.add(Dense(units=16, input_dim=2, activation='relu'))
    model.add(Dense(units=32, activation='relu'))

    model.add(Dense(units=64, activation='relu'))
    model.add(Dense(units=64, activation='relu'))

    model.add(Dense(units=128, activation='relu'))
    model.add(Dense(units=128, activation='relu'))
    model.add(Dense(units=128, activation='relu'))

    model.add(Dense(units=64, activation='relu'))
    model.add(Dense(units=64, activation='relu'))

    model.add(Dense(units=32, activation='relu'))
    model.add(Dense(units=32, activation='relu'))
    model.add(Dense(units=32, activation='relu'))
    model.add(Dense(units=32, activation='relu'))
    model.add(Dense(units=32, activation='relu'))

    model.add(Dense(units=out_classes, activation='softmax'))
    model.compile(loss='categorical_crossentropy',
                  optimizer='adam', metrics=['accuracy'])

    model.fit(data.iloc[:, :-1], y, epochs=200, batch_size=512)

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

    sample_p = model.predict(sample)
    sample_pred = [0 for i in range(len(sample_p))]

    for i in range(len(sample_p)):
        maxm = max(sample_p[i])

        for j in range(len(sample_p[i])):
            if sample_p[i][j] == maxm:
                index = j

        sample_pred[i] = index

    directions = le_pred.inverse_transform(sample_pred)
    directions

    for i in range(len(directions)):
        if directions[i] == 'N':
            c = np.random.randint(0, 1)
            if c == 0:
                directions[i] = np.random.randint(0, 22.5)
            elif c == 1:
                directions[i] = np.random.randint(337.5, 360)

        elif directions[i] == 'NE':
            directions[i] = np.random.randint(22.5, 67.5)

        elif directions[i] == 'E':
            directions[i] = np.random.randint(67.5, 112.5)

        elif directions[i] == 'SE':
            directions[i] = np.random.randint(112.5, 157.5)

        elif directions[i] == 'S':
            directions[i] = np.random.randint(157.5, 202.5)

        elif directions[i] == 'SW':
            directions[i] = np.random.randint(202.5, 247.5)

        elif directions[i] == 'W':
            directions[i] = np.random.randint(247.5, 292.5)

        elif directions[i] == 'NW':
            directions[i] = np.random.randint(292.5, 337.5)

    pred_data = pd.DataFrame(
        columns=['date', 'direction', 'speed']
    )

    pred_data['date'] = pred_date
    pred_data['direction'] = directions

    pred_filename = location+".csv"
    filepath = "data/"+pred_filename

    pred_data.to_csv(filepath, mode='a', header=False, index=False)
