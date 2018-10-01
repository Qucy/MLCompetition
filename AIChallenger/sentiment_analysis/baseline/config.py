#!/user/bin/env python
# -*- coding:utf-8 -*-

import os
model_save_path = os.path.abspath('..') + "/data/"
# 训练集文件存放路径
train_data_path = "../data/training/sentiment_analysis_trainingset.csv"
# 验证集文件存放路径
validate_data_path = "../data/validation/sentiment_analysis_validationset.csv"
# 测试集文件存放路径
test_data_path = "../data/test_a/sentiment_analysis_testa.csv"
# 测试集预测结果文件存放路径
test_data_predict_out_path = "../data/test_a/sentiment_analysis_testa_prediction.csv"
