import os
import pandas as pd

def dump_counts(df, idx, col):
    dump_grouped = df.groupby([idx, col]).size()\
      .unstack().fillna(0)\
      .reset_index()\
      #.to_csv(os.path.join(filepath, '{}.csv'.format(col).replace(" ", "_")), index=False)
    return dump_grouped

def agg_work_description(df, idx, text_col, category, sep=" ",):
    df[text_col] = df[text_col].fillna("")
    agg_work_description = df[df['General Category'] == category].groupby([idx])[text_col]\
                             .apply(list)\
                             .apply(lambda x: sep.join(x))
    return agg_work_description

def agg_address_description(df, idx, text_col, sep=","):
    df[text_col] = df[text_col] .fillna(" ")
    agg_address_description = df.groupby([idx])[text_col]\
                             .apply(list)\
                             .apply(lambda x: sep.join(x))
    return agg_address_description
#
# Set the input/output file names to the right targets
#


DATA_PATH = "~/Dropbox/Democratic Freedom DataDive/LA Mayor's Office - Ellis Act/modified datasets"
INPUT_FILE = os.path.join(DATA_PATH, "la_housing_dataset_no_geo_property_id_cleanzip2.csv")
OUTPUT_FILE = os.path.join(DATA_PATH, "test_output.csv")




# read in the file
la_housing = pd.read_csv(INPUT_FILE, encoding='latin-1')
la_housing['Status Date'] = pd.to_datetime(la_housing['Status Date'])

has_ellis_withdrawal = la_housing.loc[la_housing['General Category'] == "Ellis Withdrawal", "Property ID"].unique().tolist()
currently_rso = la_housing.loc[la_housing['General Category'] == 'Is in RSO Inventory', "Property ID"].unique().tolist()
ever_rso_list = list(set(has_ellis_withdrawal + currently_rso))

# Get the date that withdrawal occurred

min_ellis_date = (
    la_housing[la_housing['General Category'] == 'Ellis Withdrawal'].
    groupby(['Property ID'])[['Status Date']].
    min().
    rename(columns={'Status Date':'Withdrawal Date'})
)

# Drop activite that happened after a withdrawal
merged_la_housing = pd.concat([la_housing, min_ellis_date], axis=1)

# Drop stuff that occured after a withdrawal
merged_la_housing = merged_la_housing.loc[
    pd.isnull(merged_la_housing['Withdrawal Date']) |
    (merged_la_housing['Withdrawal Date'] > merged_la_housing['Status Date'])
]

# Ignore stuff that was never RSO
merged_la_housing = merged_la_housing[merged_la_housing['Property ID'].isin(ever_rso_list)]

# Add the outcome variable for 'Was Withdrawn'
merged_la_housing['WasWithdrawn'] = ~pd.isnull(merged_la_housing['Withdrawal Date'])


#
# Add columns here that are 1 for a feature of interest, 0 elsewhere. Then add them to the 'output columns' list.
#

merged_la_housing['num_building_permits'] = (merged_la_housing['General Category'] == 'Building Permits').astype(int)
merged_la_housing['num_demo_permits'] = (merged_la_housing['General Category'] == 'Demolition Permits').astype(int)
merged_la_housing['num_entitlement_changes'] = (merged_la_housing['General Category'] == 'Entitlement Change').astype(int)

output_columns = [
    'num_building_permits',
    'num_demo_permits',
    'num_entitlement_changes',
    'WasWithdrawn'
]


df_output = merged_la_housing.groupby('Property ID')[output_columns].sum()
cat_col = ['Permit Type','Permit Sub-Type']
idx = 'Property ID'
text_col = 'Work Description'

for col in cat_col:
    dump_grouped = dump_counts(merged_la_housing, idx, col)
    df_output = df_output.join(dump_grouped.set_index(idx), how='left').fillna(0)

# concat work description
gc = ['Entitlement Change', 'Building Permits','Demolition Permits']
for cat in gc:
    temp = pd.DataFrame(agg_work_description(merged_la_housing, idx, text_col, cat))
    temp.columns = [cat+ "_"+text_col]
    df_output = df_output.join(temp, how='left').fillna("NAN")
# concat address
df_output = df_output.join(pd.DataFrame(
              agg_address_description(merged_la_housing, idx, 'Address Full', sep=',')), how='left').fillna(0)
# concat work description

df_output = df_output.reset_index()
df_output['WasWithdrawn'] = df_output['WasWithdrawn'] > 0
df_output.to_csv(OUTPUT_FILE, index=False)
