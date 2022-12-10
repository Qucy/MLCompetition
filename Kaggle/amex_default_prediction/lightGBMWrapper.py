import warnings

warnings.simplefilter("ignore")

import os
import random
import pandas as pd
import numpy as np
from datetime import datetime
from contextlib import contextmanager
from tqdm import tqdm
from sklearn.metrics import (
    roc_auc_score,
    mean_squared_error,
    average_precision_score,
    log_loss,
)
from sklearn.model_selection import KFold, StratifiedKFold, GroupKFold

import lightgbm as lgb


class LightGBMWrapper:
    """lightGBM training wrapper"""

    def __init__(self, model_config):
        """ init function to construct model
        """
        # retrieve config from model_config
        self.model_config = model_config
        self.name = model_config["name"]
        self.root_path = model_config["root_path"]
        self.epoch = model_config["epoch"]
        self.seed = model_config["seed"]
        self.n_folds = model_config["n_folds"]
        self.early_stopping = model_config["early_stopping"]
        self.lgb_hyper_params = model_config["lgb_hyper_params"]
        self.features = model_config["features"]
        self.lablel = model_config["label"]
        self.id = model_config["id"]
        self.verbose_eval = model_config["verbose_eval"]
        self.remark = model_config["remark"]

        # init experiment id and output folder
        self.experiment_id = self.name + "_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_path = os.path.join(self.root_path, self.experiment_id)

        # create folder if not exist
        if not os.path.isdir(self.output_path):
            os.makedirs(self.output_path)

        # create train log file
        self.train_log = open(
            os.path.join(self.output_path, "train.log"), "w", buffering=1
        )

    def train(self, data):
        # data should not be null
        assert (data is not None, "training data should not be null")

        # init variables
        all_metrics, feature_importance = [], []
        label_name = self.lablel[0]

        # split data by StratifiedKFold
        skf = StratifiedKFold(
            n_splits=self.n_folds, shuffle=True, random_state=self.seed
        )
        X = data[self.features]
        y = data[self.lablel]
        ids = data[self.id]
        split = skf.split(X, y)

        # record configuration at begining
        self._write_train_log_header_or_tail()

        # create dataframe to store prediction
        oof = ids
        oof[label_name] = 0

        # loop split data
        for fold, (train_index, val_index) in enumerate(split):
            # init evaluation result dict
            eval_dict = {}
            # init lgb training and validation dataset
            train_data = lgb.Dataset(X.iloc[train_index], label=y.iloc[train_index])
            val_data = lgb.Dataset(X.iloc[val_index], label=y.iloc[val_index])
            # train model
            model = lgb.train(
                self.lgb_hyper_params,
                train_set=train_data,
                num_boost_round=self.epoch,
                valid_sets=[train_data, val_data],
                evals_result=eval_dict,
                early_stopping_rounds=self.early_stopping,
                verbose_eval=self.verbose_eval,
            )
            # save model
            model.save_model(os.path.join(self.output_path, f"{fold}.ckpt"))
            # make prediction on validation dataset
            valid_preds = model.predict(
                X.iloc[val_index], num_iteration=model.best_iteration
            )
            # save predition
            oof.loc[val_index, label_name] = valid_preds

            # calc amex metric
            amex_metrics = self._amex_metric(
                y.iloc[val_index][label_name].values, valid_preds
            )
            all_metrics.append(amex_metrics)
            # write train log
            self._write_train_log_body(eval_dict, amex_metrics, fold)

            # append feature importance
            feature_importance.append(
                pd.DataFrame(
                    {
                        "feature_name": model.feature_name(),
                        "importance_gain": model.feature_importance(
                            importance_type="gain"
                        ),
                        "importance_split": model.feature_importance(
                            importance_type="split"
                        ),
                    }
                )
            )
        # calc mean amex metric for all the validation dataset
        mean_amex_metric = np.mean(all_metrics)
        # calc global amex metric for all the training dataset
        global_amex_metric = self._amex_metric(
            y[label_name].values, oof[label_name].values
        )
        # output feature importance
        self._write_feature_importance(feature_importance)
        # save tailor for train log
        self._write_train_log_header_or_tail(
            False, mean_amex_metric, global_amex_metric
        )
        # save predictions
        oof.to_csv(os.path.join(self.output_path, "oof.csv"), index=False)
        # output experiment log
        self._write_experiment_log(mean_amex_metric, global_amex_metric)

    def predict(self, data, model_path=None):
        """ predict and generate submission file
        """
        # create submission dataframe
        submission = data[self.id]
        submission["prediction"] = 0
        # looping all the folds
        for fold in range(self.n_folds):
            # generate model file path
            model_path = self.output_path if model_path is None else model_path
            model_file = os.path.join(model_path, f"{fold}.ckpt")
            # loading model
            model = lgb.Booster(model_file=model_file)
            test_preds = model.predict(
                data[self.features], num_iteration=model.best_iteration
            )
            submission["prediction"] += test_preds / self.n_folds
        # save to local disk
        submission.to_csv(
            os.path.join(model_path, "submission.csv.zip"),
            compression="zip",
            index=False,
        )

    def _amex_metric(self, y_true, y_pred):
        """ calc amex metric
        """
        labels = np.transpose(np.array([y_true, y_pred]))
        labels = labels[labels[:, 1].argsort()[::-1]]
        weights = np.where(labels[:, 0] == 0, 20, 1)
        cut_vals = labels[np.cumsum(weights) <= int(0.04 * np.sum(weights))]
        top_four = np.sum(cut_vals[:, 0]) / np.sum(labels[:, 0])

        gini = [0, 0]
        for i in [1, 0]:
            labels = np.transpose(np.array([y_true, y_pred]))
            labels = labels[labels[:, i].argsort()[::-1]]
            weight = np.where(labels[:, 0] == 0, 20, 1)
            weight_random = np.cumsum(weight / np.sum(weight))
            total_pos = np.sum(labels[:, 0] * weight)
            cum_pos_found = np.cumsum(labels[:, 0] * weight)
            lorentz = cum_pos_found / total_pos
            gini[i] = np.sum((lorentz - weight_random) * weight)

        return 0.5 * (gini[1] / gini[0] + top_four)

    def _write_train_log_header_or_tail(
        self, isHeader=True, mean_amex_metric=None, global_amex_metric=None
    ):
        """ write header or tailor for train log
        """
        if isHeader:
            self._write_log(
                self.train_log,
                "================================Model Config Start================================\n",
            )
            self._write_log(self.train_log, str(self.model_config) + "\n")
            self._write_log(
                self.train_log,
                "================================Model Config End================================\n",
            )
        else:
            self._write_log(
                self.train_log,
                f"All mean metric:{mean_amex_metric:.6f}, global metric:{global_amex_metric:.6f}",
            )
            self.train_log.close()
            # rename for better understanding
            os.rename(
                os.path.join(self.output_path, "train.log"),
                os.path.join(self.output_path, f"train_{mean_amex_metric:.6f}.log"),
            )

    def _write_train_log_body(self, eval_dict, amex_metrics, fold):
        """ write training log into train log
        """
        # retrieve validation result for dict
        train_metrics = eval_dict["training"][self.lgb_hyper_params["metric"]]
        validate_metrics = eval_dict["valid_1"][self.lgb_hyper_params["metric"]]
        self._write_log(
            self.train_log,
            f"================================Fold {fold} start================================\n",
        )
        for i in range(len(validate_metrics) // self.verbose_eval):
            self._write_log(
                self.train_log,
                f" - {i * self.verbose_eval} round - train_metric: {train_metrics[i * self.verbose_eval]:.6f} - valid_metric: {validate_metrics[i * self.verbose_eval]:.6f}\n",
            )
        self._write_log(
            self.train_log, f"- {fold} amex metric: {np.mean(amex_metrics):.6f}\n"
        )
        self._write_log(
            self.train_log,
            f"================================Fold {fold} End================================\n",
        )

    def _write_feature_importance(self, feature_importance):
        # calc mean for feature importance -> sort -> save csv to disk
        _ = (
            pd.concat(feature_importance)
            .groupby(["feature_name"])
            .mean()
            .reset_index()
            .sort_values(by=["importance_gain"], ascending=False)
            .to_csv(
                os.path.join(self.output_path, "feature_importance.csv"), index=False
            )
        )

    def _write_experiment_log(self, mean_metric, global_metric):
        """ write experiment log
        """
        log_df = pd.DataFrame(
            {
                "run_id": [self.experiment_id],
                "mean metric": [round(mean_metric, 6)],
                "global metric": [round(global_metric, 6)],
                "remark": [self.remark],
            }
        )
        experiment_file = os.path.join(self.root_path, "experiment_log.csv")
        if not os.path.exists(experiment_file):
            log_df.to_csv(experiment_file, index=False)
        else:
            log_df.to_csv(experiment_file, index=False, header=None, mode="a")

    def _write_log(self, f, log, is_print=True):
        """ print and write log
        """
        if is_print:
            print(log)
        f.write(log)
        return None

