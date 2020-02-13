import pandas as pd 
import numpy as np
from statistics import mean

penticton_data = pd.read_csv('Penticton RS Jan1 2009-Feb 7-2020.csv')
mccuddy_data = pd.read_csv('McCuddy Jan1 2009-Feb 7-2020.csv')
ashnola_data = pd.read_csv('Ashnola Jan1 2009-Feb 7-2020.csv')

dataframes = [penticton_data, mccuddy_data, ashnola_data]
dropColumns=['temperature', 'relative_humidity', 'wind_direction', 'wind_speed', 'precipitation', 'status', 'temp_valid', 'rh_valid', 'wdir_valid', 'wspeed_valid', 'precip_valid', 'gc', 'danger_rating']

for col in dropColumns:
    penticton_data = penticton_data.drop(columns=[col])
    mccuddy_data = mccuddy_data.drop(columns=[col])
    ashnola_data = ashnola_data.drop(columns=[col])

ffmc_percentiles = []
bui_percentiles = []
isi_percentiles = []

# parse weather_date string into 3 columns: yyyy - mm - dd
for df in dataframes:
    station_name = str(df['display_name'].iloc[0])

    # sanity check - report if any indexes or code values are negative (they shouldn't be)
    negative_values = df[['ffmc', 'bui', 'isi']] < 0

    df['year'] = df['weather_date'].apply(lambda x: int(np.trunc(x/10000)))
    df['month'] = df['weather_date'].apply(lambda x: int(np.trunc((x % 1000) / 100)))
    df['day'] = df['weather_date'].apply(lambda x: int(np.trunc((x % 100))))
    df = df.drop(columns=['weather_date'])

    # remove data recorded > 10 years ago
    indexNames = df[df['year'] < 2009].index
    df.drop(indexNames, inplace=True)

    # remove data recorded outside of fire season
    # assume fire season for Penticton is May 1 - August 31. I don't actually know, it's just a guess
    indexNames = df[df['month'] > 8].index
    df.drop(indexNames, inplace=True)
    indexNames = df[df['month'] < 5].index
    df.drop(indexNames, inplace=True)

    # calculate 90th percentile
    ninetieth_percentile = df.quantile(.9)
    ffmc_percentiles.append(ninetieth_percentile['ffmc'])
    isi_percentiles.append(ninetieth_percentile['isi'])
    bui_percentiles.append(ninetieth_percentile['bui'])


    print('\n----- ' + station_name + ' -------\n')
    if (negative_values[negative_values==True].count().sum() > 0):
        print('Number of invalid values found: ' + str(negative_values[negative_values==True].count().sum()))
    print('FFMC: ' + str(ninetieth_percentile['ffmc']))
    print('ISI: ' + str(ninetieth_percentile['isi']))
    print('BUI: ' + str(ninetieth_percentile['bui']))
    print('\n--------------\n')


# data completeness check - report if FFMC, BUI, or ISI data is missing for any day

# data completeness check - report if any days within fire season in 2009 - 2019 are missing

# report mean values for each of FFMC, BUI, & ISI
print('Mean FFMC: ' + str(mean(ffmc_percentiles)))
print('Mean ISI: ' + str(mean(isi_percentiles)))
print('Mean BUI: ' + str(mean(bui_percentiles)))
print('\n\n')