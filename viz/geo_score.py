"""Munge data for Tableau viz."""

import pandas as pd

# read in raw and geo data
raw = pd.read_csv('cleanzip_2.csv').drop('Unnamed: 0', axis=1)

# geo data came from geohub's geocoding service (http://lahub.maps.arcgis.com/)
# the CSV is in DropBox and Slack!
geo = pd.read_csv('geohub.csv')

# fix the Zip Codes which were lost in geohub
zips = raw.pivot_table(index=['Property ID'], aggfunc='first')['Zip Code'].reset_index()

fix_zip = geo.merge(zips, on='Property ID').rename(
    columns={'Zip Code_y': 'Zip Code'}).drop('Zip Code_x', axis=1)

new_col_order = list(fix_zip.columns[:-5]) + ['Zip Code'] + list(fix_zip.columns[-5:-1])
fix_zip = fix_zip[new_col_order]

# add in potential violations as a new General Category
# this does not actually have scores / ranking
potential_violations = pd.read_csv('potential_violations.csv').rename(
    columns={'Property.ID': 'Property ID'})
withdraw_geo = fix_zip[fix_zip['General Category'] == 'Ellis Withdrawal']
violation_df = withdraw_geo.merge(pd.DataFrame(potential_violations['Property ID']),
                                  on='Property ID')
violation_df['General Category'] = 'Potential Violation'

pd.concat([fix_zip, violation_df]).to_csv('fix_zip_with_violations.csv', index=False)
