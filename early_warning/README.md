# Early Warning list


This folder takes the output from a datarobot analysis and creates the 'early warning list' that lists rent controlled properties that might undergo an Ellis Withdrawal in the near future.


The script `get_aggregate_per_property.py` provides a template for how to transform the dataset created by `./data/build_Datadive_csv.py` and extract aggregated features for each property. These feature vectors were fed into datarobot, then something mathemagical happened, and they gave us a bunch of predictions about the probability a property would withdraw.

The file `put_datarobot_output_in_csv.py` takes the data robot output, joins it to the original data file, and creates the warning list `Early_Warning_List.csv`