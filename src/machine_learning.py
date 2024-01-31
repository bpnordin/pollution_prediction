import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import sklearn
from sklearn.pipeline import make_pipeline
from sklearn.compose import make_column_transformer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import root_mean_squared_error
from sklearn.model_selection import cross_val_score
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt
import subprocess
from sklearn.preprocessing import OneHotEncoder

aqs_data = pd.read_csv(
    "data/sample_data/full_df.csv", index_col=0, parse_dates=["datetime"]
)
print(aqs_data.info())
# stratified sampling?
strat_train_set, strat_test_set = train_test_split(
    aqs_data, test_size=0.2, random_state=42, stratify=aqs_data["site_number"]
)

#print(strat_test_set["site_number"].value_counts() / len(strat_test_set))

# site number is no longer useful
# neither is ozone
for set_ in (strat_test_set, strat_train_set):
    #set_.drop("site_number", axis=1, inplace=True)
    set_.drop(["latitude","longitude","site_number"], axis=1, inplace=True)

#print(strat_train_set.info())
#strat_train_set.hist(bins=50, figsize=(36, 24))
#plt.savefig("/tmp/plot.png")
#subprocess.run(["kitty", "icat", "/tmp/plot.png"])
# df.plot(kind="scatter",x="longitude",y="latitude",grid=True,alpha=0.1, figsize=(36,24))

# plt.savefig("/tmp/plot.png")
# subprocess.run(["kitty","icat", "/tmp/plot.png"])

# start transforming data
ozone = strat_train_set.drop("Ozone", axis=1).copy()
ozone_labels = strat_train_set["Ozone"].copy()


def log_plus_one(x):
    return np.log(x + 1)


def inverse_log_plus_one(x):
    return np.exp(x) - 1


log_transformer = sklearn.preprocessing.FunctionTransformer(
    lambda x: np.log(x + 1), inverse_func=lambda x: np.exp(x) - 1
)
log_attributes = [
    "Wind Speed - Scalar",
    "Solar radiation",
    "previous_hour_ozone",
    "Barometric pressure",
]
log_pipeline = make_pipeline(log_transformer, sklearn.preprocessing.StandardScaler())
standard_attributes = [
    "Outdoor Temperature",
    "Relative Humidity ",
    "Wind Direction - Scalar",
]

datetime_attributes = ['Month','Hour','Week Day']
datetime_encoder = make_pipeline(OneHotEncoder())

preprocessing = make_column_transformer(
    (log_pipeline, log_attributes),
    (sklearn.preprocessing.StandardScaler(), standard_attributes),
    (datetime_encoder,datetime_attributes),
    remainder="drop"
    
)

lin_reg = make_pipeline(
    preprocessing,
    sklearn.compose.TransformedTargetRegressor(
        regressor=RandomForestRegressor(random_state=42),
        transformer=log_transformer
    ),
)
scores = -cross_val_score(lin_reg, ozone,ozone_labels,cv=2,scoring="neg_root_mean_squared_error")
print(pd.Series(scores).describe())
lin_reg.fit(ozone, ozone_labels)
ozone_predict = lin_reg.predict(ozone)
print(ozone_predict[:5])
print(ozone_labels.iloc[:5].values)
lin_rmse = root_mean_squared_error(ozone_labels, ozone_predict)
print(lin_rmse)

x_test = strat_test_set.drop("Ozone", axis=1)
y_test = strat_test_set["Ozone"].copy()
test_predict = lin_reg.predict(x_test)
print(root_mean_squared_error(test_predict, y_test))
