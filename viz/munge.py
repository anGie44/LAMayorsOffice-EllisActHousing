import pandas as pd

# geos came from uploading the addresses to http://lahub.maps.arcgis.com/
# http://lahub.maps.arcgis.com/home/item.html?id=0dac8f8c097b4418bb5b1f81f16e40d6
# use ALL properties to max. likelihood of match, not uniques.
raw = pd.read_csv('cleanzip_2.csv').drop('Unnamed: 0', axis=1)
geo = pd.read_csv('geohub_all.csv')

# get UNIQUE lat-lngs for each property
latlng = geo.pivot_table(index=['Property ID'])[['x', 'y']].reset_index()
print '{} unique geocoordinates for {} property IDs'.format(len(latlng), len(set(raw['Property ID'])))

# output the raw data (fix zip) with lat-lng
with_geo = raw.merge(latlng, on=['Property ID'])
with_geo.to_csv('with_geo.csv')

# add violations
potential_violations = pd.read_csv('potential_violations.csv').rename(columns={'Property.ID': 'Property ID'})
withdraw_geo = with_geo[with_geo['General Category'] == 'Ellis Withdrawal']
violation_df = withdraw_geo.merge(pd.DataFrame(potential_violations['Property ID']), on='Property ID')
violation_df['General Category'] = 'Potential Violation'

with_violation = pd.concat([with_geo, violation_df])
with_violation.to_csv('with_geo_violation.csv', index=False)

# Add RSO as a column
rso = with_geo[with_geo['General Category'] == 'Is in RSO Inventory'].pivot_table(
    index=['Property ID']).reset_index()
rso['RSO'] = True
with_rso = with_violation.merge(rso[['Property ID', 'RSO']], on='Property ID', how='left')
with_rso['RSO'].fillna(False, inplace=True)
with_rso.to_csv('with_geo_violation_rso.csv', index=False)
