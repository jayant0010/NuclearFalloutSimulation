import os
import pandas as pd


def preprocessing(location):
    filename = location+".csv"
    df = pd.read_csv(filename)

    final_df = pd.DataFrame(
        columns=['date', 'direction', 'speed']
    )

    final_df['date'] = df['date_time']
    final_df['direction'] = df['winddirDegree']
    final_df['speed'] = df['windspeedKmph']

    filepath = "data/"+filename
    final_df.to_csv(filepath, index=False)

    for i in range(len(df['winddirDegree'])):
        if df['winddirDegree'][i] >= 337.5 or df['winddirDegree'][i] < 22.5:
            df['winddirDegree'][i] = 'N'

        elif df['winddirDegree'][i] >= 22.5 and df['winddirDegree'][i] < 67.5:
            df['winddirDegree'][i] = 'NE'

        elif df['winddirDegree'][i] >= 67.5 and df['winddirDegree'][i] < 112.5:
            df['winddirDegree'][i] = 'E'

        elif df['winddirDegree'][i] >= 112.5 and df['winddirDegree'][i] < 157.5:
            df['winddirDegree'][i] = 'SE'

        elif df['winddirDegree'][i] >= 157.5 and df['winddirDegree'][i] < 202.5:
            df['winddirDegree'][i] = 'S'

        elif df['winddirDegree'][i] >= 202.5 and df['winddirDegree'][i] < 247.5:
            df['winddirDegree'][i] = 'SW'

        elif df['winddirDegree'][i] >= 247.5 and df['winddirDegree'][i] < 292.5:
            df['winddirDegree'][i] = 'W'

        elif df['winddirDegree'][i] >= 292.5 and df['winddirDegree'][i] < 337.5:
            df['winddirDegree'][i] = 'NW'

    df['month'] = ''
    df['day'] = ''

    for i in range(len(df['date_time'])):
        x = df['date_time'][i].split('-')
        df['day'][i] = x[2]
        df['month'][i] = x[1]

    preprocessed_data = pd.DataFrame(
        columns=['date', 'day', 'month', 'WindDir', 'WindspeedKmph']
    )

    preprocessed_data['date'] = df['date_time']
    preprocessed_data['day'] = df['day']
    preprocessed_data['month'] = df['month']

    preprocessed_data['WindDir'] = df['winddirDegree']
    preprocessed_data['WindspeedKmph'] = df['windspeedKmph']

    prepro_filename = location+"_preprocessed.csv"
    preprocessed_data.to_csv(prepro_filename, index=False)

    os.remove(filename)
