import os
import pandas as pd
import numpy as np

DATA_PATH = '~/GitHub/la_mayors_office/data'
INPUT_WARNING_FILE = os.path.join(DATA_PATH, "LA_Downsample_Gradient_Boosted_Trees_Classifier_with_Early_Stopp_52_19.13_no_tot_account_no_work_description_RC_10_lt_0.098_gt_0.100.csv")
INPUT_PROPERTIES_FILE = os.path.join(DATA_PATH, "la_housing_dataset_no_geo_property_id_cleanzip2.csv")

OUTPUT_FILE = os.path.join(DATA_PATH, "Early_Warning_List.csv")

# read in the file
df_housing = pd.read_csv(INPUT_PROPERTIES_FILE, encoding='latin-1')
df_warning = pd.read_csv(INPUT_WARNING_FILE, encoding='latin-1', dtype=str)

# Set dtypes for index variable
df_warning['Property ID'] = df_warning['Property ID'].astype(str)
df_housing['Property ID'] = df_housing['Property ID'].astype(str)

# merge address data with prediction data
df_housing_prediction = (
    df_housing[['Property ID', 'APN', 'Address Full', 'Zip Code']].
    set_index('Property ID').
    join(
        df_warning.set_index('Property ID')[['num_demo_permits', 'Total Actions Before Ellis', 'Cross-Validation Prediction']],
        how='inner'
    )
)

# Turn prediction into a 0-100 threat level
df_housing_prediction['Withdrawal Threat Level'] = np.round(100 * df_housing_prediction['Cross-Validation Prediction'].astype(float)).astype(int)
df_housing_prediction = df_housing_prediction.drop('Cross-Validation Prediction', 1)

# Outputting format
df_housing_prediction = (
    df_housing_prediction.
    reset_index('Property ID').
    sort_values(['Withdrawal Threat Level', 'Property ID', 'APN'], ascending=[False, True, True]).
    fillna('').
    drop_duplicates()
)

df_housing_prediction.to_csv(OUTPUT_FILE, index=False)
