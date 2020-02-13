import pandas as pd 
import numpy as np
from statistics import mean

penticton_data = pd.read_csv('Penticton RS Jan1 2009-Feb 7-2020.csv')
mccuddy_data = pd.read_csv('McCuddy Jan1 2009-Feb 7-2020.csv')
ashnola_data = pd.read_csv('Ashnola Jan1 2009-Feb 7-2020.csv')

dataframes = [penticton_data, mccuddy_data, ashnola_data]
dropColumns=['temperature', 'relative_humidity', 'wind_direction', 'wind_speed', 'precipitation', 'status', 'temp_valid', 'rh_valid', 'wdir_valid', 'wspeed_valid', 'precip_valid', 'gc', 'danger_rating']

# fire season start and end dates (month and day in numeric format) for location
# May 1 - Sept 15 used for these stations
FIRE_SEASON_START_MONTH = 5
FIRE_SEASON_START_DATE = 1
FIRE_SEASON_END_MONTH = 9
FIRE_SEASON_END_DATE = 15

# time range start and end years
START_YEAR = 2009
END_YEAR = 2019

# percentile to report out (in decimal format)
PERCENTILE = 0.9

for col in dropColumns:
    penticton_data = penticton_data.drop(columns=[col])
    mccuddy_data = mccuddy_data.drop(columns=[col])
    ashnola_data = ashnola_data.drop(columns=[col])

ffmc_percentiles = []
bui_percentiles = []
isi_percentiles = []

print('\n\n *------ PERCENTILE FIRE WEATHER CALCULATOR -------*\n\n')
print('Percentile calculated: ' + str(PERCENTILE * 100))
print('Fire season start month/date: ' + str(FIRE_SEASON_START_MONTH) + '/' + str(FIRE_SEASON_START_DATE))
print('Fire season end month/date: ' + str(FIRE_SEASON_END_MONTH) + '/' + str(FIRE_SEASON_END_DATE))
print('Years included in time range: ' + str(START_YEAR) + ' - ' + str(END_YEAR))

# parse weather_date string into 3 columns: yyyy - mm - dd
for df in dataframes:
    station_name = str(df['display_name'].iloc[0])

    # sanity check - report if any indexes or code values are negative (they shouldn't be)
    negative_values = df[['ffmc', 'bui', 'isi']] < 0

    df['year'] = df['weather_date'].apply(lambda x: int(np.trunc(x/10000)))
    df['month'] = df['weather_date'].apply(lambda x: int(np.trunc((x % 1000) / 100)))
    df['day'] = df['weather_date'].apply(lambda x: int(np.trunc((x % 100))))
    df = df.drop(columns=['weather_date'])

    # remove data recorded before START_YEAR
    indexNames = df[df['year'] < START_YEAR].index
    df.drop(indexNames, inplace=True)
    # remove data recorded after END_YEAR
    indexNames = df[df['year'] > END_YEAR].index
    df.drop(indexNames, inplace=True)

    # remove data recorded outside of fire season
    indexNames = df[df['month'] < FIRE_SEASON_START_MONTH].index
    df.drop(indexNames, inplace=True)
    indexNames = df[df['month'] > FIRE_SEASON_END_MONTH].index
    df.drop(indexNames, inplace=True)
    indexNames = df[(df['month'] == FIRE_SEASON_START_MONTH) & (df['day'] < FIRE_SEASON_START_DATE)].index
    df.drop(indexNames, inplace=True)
    indexNames = df[(df['month'] == FIRE_SEASON_END_MONTH) & (df['day'] > FIRE_SEASON_END_DATE)].index
    df.drop(indexNames, inplace=True)


    # calculate 90th percentile
    calculated_percentile = df.quantile(PERCENTILE)
    ffmc_percentiles.append(calculated_percentile['ffmc'])
    isi_percentiles.append(calculated_percentile['isi'])
    bui_percentiles.append(calculated_percentile['bui'])


    print('\n----- ' + station_name + ' -------\n')
    if (negative_values[negative_values==True].count().sum() > 0):
        print('Number of invalid values found: ' + str(negative_values[negative_values==True].count().sum()))
    print('Values at ' + str(PERCENTILE * 100) + 'th percentile:')
    print('FFMC: ' + str(calculated_percentile['ffmc']))
    print('ISI: ' + str(calculated_percentile['isi']))
    print('BUI: ' + str(calculated_percentile['bui']))
    print('\n--------------\n')


# data completeness check - report if FFMC, BUI, or ISI data is missing for any day

# data completeness check - report if any days within fire season in 2009 - 2019 are missing

# report mean values for each of FFMC, BUI, & ISI
print('Mean FFMC: ' + str(mean(ffmc_percentiles)))
print('Mean ISI: ' + str(mean(isi_percentiles)))
print('Mean BUI: ' + str(mean(bui_percentiles)))
print('\n\n')