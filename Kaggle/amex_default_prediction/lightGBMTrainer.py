import warnings

warnings.simplefilter("ignore")

import pandas as pd
from lightGBMWrapper import LightGBMWrapper

# define columns
customer_id_column = ["customer_ID"]
date_column = ["S_2"]
categorical_features = [
    "B_30",
    "B_38",
    "D_114",
    "D_116",
    "D_117",
    "D_120",
    "D_126",
    "D_63",
    "D_64",
    "D_66",
    "D_68",
]
non_numerical_features = customer_id_column + date_column + categorical_features
label = ["target"]

# label file
train_label_file = "./data/train_labels.csv"
# feature file
feature_file = "./data/all_feature.feather"

# loading features
all_features = pd.read_feather(feature_file)
# loading labels
labels = pd.read_csv(train_label_file)

# merge label with feature file
assert all_features[customer_id_column].equals(labels[customer_id_column]) == True
# combine with label
all_features = pd.concat(
    [all_features, labels.drop(columns=customer_id_column)], axis=1
)

# define model training column with all features
all_feature_column = [
    c
    for c in all_features.columns
    if c not in [customer_id_column[0], date_column[0], label[0]]
]

# define model training features without serise features
all_feature_without_series_feature = [
    c for c in all_feature_column if "target" not in c
]

print(
    f"All feature length {len(all_feature_column)}, feature without series feature {len(all_feature_without_series_feature)}"
)

# define lightGBM config
lgb_config = {
    "name": "lightGBM_without_series_feature",
    "root_path": "/root/amex_prediction/model/",
    "seed": 42,
    "epoch": 4500,
    "early_stopping": 100,
    "verbose_eval": 50,
    "n_folds": 3,
    "features": all_feature_without_series_feature,
    "label": label,
    "id": customer_id_column,
    "verbose_eval": 50,
    "remark": "lgb_with_raw_rank_last36_features",
    "lgb_hyper_params": {
        "objective": "binary",
        "metric": "binary_logloss",
        "boosting": "goss",  # dart
        "max_depth": -1,
        "num_leaves": 64,
        "learning_rate": 0.035,
        #'bagging_freq': 5,
        #'bagging_fraction' : 0.75,
        "feature_fraction": 0.05,
        "min_data_in_leaf": 256,
        "max_bin": 63,
        "min_data_in_bin": 256,
        "tree_learner": "serial",
        "boost_from_average": "false",
        "lambda_l1": 0.1,
        "lambda_l2": 30,
        "num_threads": 12,
        "verbosity": 1,
    },
}
# construct lightGBM model
lightGBMModel_without_series_feature = LightGBMWrapper(lgb_config)
lightGBMModel_without_series_feature.train(all_features)

