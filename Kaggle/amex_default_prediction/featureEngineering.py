import pandas as pd
import numpy as np
from greedyFindBin import GreedyFindBin

one_hot_prefix = "one_hot"


def one_hot_encoding(df, cols, is_drop=True):
    """ function for one hot encoding
    """
    for col in cols:
        print("one hot encoding:", col)
        dummies = pd.get_dummies(pd.Series(df[col]), prefix=f"{one_hot_prefix}_{col}")
        df = pd.concat([df, dummies], axis=1)
    if is_drop:
        df.drop(cols, axis=1, inplace=True)
    return df


def category_feature_statistic(df, categorical_features, calc_last=True):
    """ calc statistic for categorical features
    """
    one_hot_features = [col for col in df.columns if one_hot_prefix in col]
    print(f"one hot cols:{one_hot_features}")
    # calc one hot statistics
    one_hot_statistic = (
        ["mean", "std", "sum", "last"] if calc_last else ["mean", "std", "sum"]
    )
    one_hot_statistic_df = df.groupby("customer_ID", sort=False)[one_hot_features].agg(
        one_hot_statistic
    )
    one_hot_statistic_df.columns = ["_".join(x) for x in one_hot_statistic_df.columns]
    # calc original categorical feature statistic
    categorical_statistic = ["last", "nunique"] if calc_last else ["nunique"]
    categorical_statistic_df = df.groupby("customer_ID", sort=False)[
        categorical_features
    ].agg(categorical_statistic)
    categorical_statistic_df.columns = [
        "_".join(x) for x in categorical_statistic_df.columns
    ]
    # calc number of transactions per customer
    count_df = df.groupby("customer_ID", sort=False)[["S_2"]].agg(["count"])
    count_df.columns = ["_".join(x) for x in count_df.columns]
    # concat dataframe
    df = pd.concat(
        [one_hot_statistic_df, categorical_statistic_df, count_df], axis=1
    ).reset_index()

    return df


def numerical_feature_statistic(
    df, numerical_features, calc_normal_statis=True, calc_last=True
):
    """ calc statistic for numerical features
    """
    numerical_statistic = []
    # decide statistic need to be calculated
    if calc_normal_statis:
        numerical_statistic += ["mean", "std", "min", "max", "sum"]
    if calc_last:
        numerical_statistic += ["last"]
    # calc statistic
    num_agg_df = df.groupby("customer_ID", sort=False)[numerical_features].agg(
        numerical_statistic
    )
    # rename columns
    num_agg_df.columns = ["_".join(x) for x in num_agg_df.columns]
    return num_agg_df.reset_index()


def diff_features(df, numerical_features, calc_last=True):
    """ 1 - calc differ between numerical features (T vs T-1)
        2 - calc differ statistic
    """
    # calc differ
    diff_numerical_features = [f"diff_{col}" for col in numerical_features]
    cids = df["customer_ID"].values
    df = df.groupby("customer_ID")[numerical_features].diff().add_prefix("diff_")
    df.insert(0, "customer_ID", cids)
    # calc differ statisc
    diff_statistic = (
        ["mean", "std", "min", "max", "sum"]
        if calc_last
        else ["mean", "std", "min", "max", "sum", "last"]
    )
    diff_statistic_df = df.groupby("customer_ID", sort=False)[
        diff_numerical_features
    ].agg(diff_statistic)
    # rename columns
    diff_statistic_df.columns = ["_".join(x) for x in diff_statistic_df.columns]
    return diff_statistic_df.reset_index()


def customer_rankings_features(df, numerical_features):
    """ rank customer features compared with his/her own features and only keep the latest record ranking
    """
    cids = df["customer_ID"].values
    df = (
        df.groupby("customer_ID")[numerical_features].rank(pct=True).add_prefix("rank_")
    )
    df.insert(0, "customer_ID", cids)
    df.drop_duplicates(subset=["customer_ID"], keep="last", inplace=True)
    return df


def year_month_ranking_features(df, numerical_features):
    """ rank customer features and compare with other customer and only keep the latest record ranking
    """
    cids = df["customer_ID"].values
    df["ym"] = df["S_2"].apply(lambda x: x[:7])
    df = df.groupby("ym")[numerical_features].rank(pct=True).add_prefix("ym_rank_")
    df.insert(0, "customer_ID", cids)
    df.drop_duplicates(subset=["customer_ID"], keep="last", inplace=True)
    return df


def retrieve_last_n_transactions_per_customer(df, n):
    """ retrieve customer latest n transactions according to S_2(datetime column)
    """
    # prefix = f"last{n}_"
    df["rank"] = df.groupby("customer_ID")["S_2"].rank(ascending=False)
    df = df.loc[df["rank"] <= n].reset_index(drop=True)
    df = df.drop(["rank"], axis=1)
    return df


def discretize_numerical_features(df, col):
    """ discretize numerical features into bins
    """
    # sort by values
    vc = df[col].value_counts().sort_index()
    # generate bins
    bins = GreedyFindBin(vc.index.values, vc.values, len(vc), 255, vc.sum())
    # assign bin index to column
    df[col] = np.digitize(df[col], [-np.inf] + bins)
    # set outlier to 0
    df.loc[df[col] == len(bins) + 1, col] = 0
    # normalization
    df[col] = df[col] / df[col].max()
    return df
