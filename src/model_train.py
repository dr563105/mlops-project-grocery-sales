import pickle
import logging

import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.metrics import mean_squared_error

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    filename="../logs/log_model_train.log",
    level=logging.DEBUG,
)
logger = logging.getLogger()


def save_to_pkl(input, filename):
    """
    Pickles/Saves content into a file
    """
    logger.info(f"Saving {filename}")
    with open(f"../output/{filename}", "wb") as f_in:
        pickle.dump(input, f_in)

def savemodel_to_pkl(input, filename):
    """
    Pickles/Saves model into models directory
    """
    logger.info(f"Saving {filename}")
    with open(f"../models/{filename}", "wb") as f_in:
        pickle.dump(input, f_in)

def load_pkl(filename):
    """
    Unpickles/loads file and returns the contents
    """
    logger.info(f"Reading {filename}...")
    with open(f"../output/{filename}", "rb") as f_out:
        df = pickle.load(f_out)
    return df


def model_training(X_train, y_train, X_val, y_val, X_test, df_items, num_days):
    """
    Model parameters are set and model is trained
    """
    logger.info("Training models...")
    logger.info("Setting Params")
    param = {
        "objective": "regression",
        "metric": "l2",
        "verbosity": -1,
        "boosting_type": "gbdt",
        "n_estimators": 200,
        "early_stopping_round": 5,
        #"device": "gpu",
        #"gpu_platform_id": 0,
        #"gpu_device_id": 0,
    }
    
    param2 = {
        'num_leaves': 4, #
        'feature_fraction': 0.7386878356648194, 
        'bagging_fraction': 0.8459744550725283, 
        'bagging_freq': 1, 
        'max_depth': 2, 
        'max_bin': 2, #249 
        'learning_rate': 0.02,
        "min_data_in_leaf": 2, #200
    }
    param.update(param2) 

    MAX_ROUNDS = 1
    val_pred = []
    test_pred = []
    cate_vars = []
    for i in range(16):
        logger.info("=" * 50)
        logger.info("Step %d" % (i + 1))
        logger.info("=" * 50)
        dtrain = lgb.Dataset(
            X_train,
            label=y_train[:, i],
            categorical_feature=cate_vars,
            weight=pd.concat([df_items["perishable"]] * num_days) * 0.25 + 1,
        )
        dval = lgb.Dataset(
            X_val,
            label=y_val[:, i],
            reference=dtrain,
            weight=df_items["perishable"] * 0.25 + 1,
            categorical_feature=cate_vars,
        )
        bst = lgb.train(
            param,
            dtrain,
            num_boost_round=MAX_ROUNDS,
            valid_sets=[dtrain, dval],
            early_stopping_rounds=1,
            verbose_eval=50,
        )
        logger.info(
            "\n".join(
                ("%s: %.2f" % x)
                for x in sorted(
                    zip(X_train.columns, bst.feature_importance("gain")),
                    key=lambda x: x[1],
                    reverse=True,
                )
            )
        )

        val_pred.append(
            bst.predict(X_val, num_iteration=bst.best_iteration or MAX_ROUNDS)
        )
        test_pred.append(
            bst.predict(X_test, num_iteration=bst.best_iteration or MAX_ROUNDS)
        )

    savemodel_to_pkl(input=bst, filename="model_lgbm.bin")
    del X_train
    save_to_pkl(input=val_pred, filename="val_pred.pkl")
    save_to_pkl(input=test_pred, filename="test_pred.pkl")
    return val_pred, test_pred


def validation_and_prediction(val_pred, y_val, df_2017):
    """
    Calculates error for the validation set and stores valadation predictions in a file
    """
    logger.info(
        "Validation mse: ",
        mean_squared_error(y_val, np.array(val_pred).transpose()),
    )

    weight = items["perishable"] * 0.25 + 1
    err = (y_val - np.array(val_pred).transpose()) ** 2
    err = err.sum(axis=1) * weight
    err = np.sqrt(err.sum() / weight.sum() / 16)
    logger.info(f"nwrmsle = {err}")

    y_val = np.array(val_pred).transpose()
    df_val_preds = (
        pd.DataFrame(
            y_val,
            index=df_2017.index,
            columns=pd.date_range("2022-09-10", periods=16),
        )
        .stack()
        .to_frame("unit_sales")
    )

    df_val_preds.index.set_names(["store_nbr", "item_nbr", "date"], inplace=True)
    df_val_preds["unit_sales"] = np.clip(np.expm1(df_val_preds["unit_sales"]), 0, 1000)
    logger.info("Saving lgb cv predictions...")
    df_val_preds.reset_index().to_parquet(
        "../output/lgb_cv.parquet", index=False, engine="pyarrow"
    )
   
def make_submission(df_test, test_pred):
    """
    Takes the test set predictions and merges with the provided test dataframe
    """
    y_test = np.array(test_pred).transpose()
    df_test_preds = (
        pd.DataFrame(
            y_test,
            index=df_2017.index,
            columns=pd.date_range("2022-09-10", periods=16),
        )
        .stack()
        .to_frame("unit_sales")
    )
    df_test_preds.index.set_names(["store_nbr", "item_nbr", "date"], inplace=True)

    submission = df_test[["id"]].join(df_test_preds, how="left").fillna(0)
    submission["unit_sales"] = np.clip(
        np.expm1(submission["unit_sales"]), 0, 1000
    )
    submission.to_parquet(
        "../output/lgb_sub.parquet",
        index=None,
        engine="pyarrow",
    )


if __name__ == "__main__":
    X_train = load_pkl("X_train.pkl")
    y_train = load_pkl("y_train.pkl")
    X_val = load_pkl("X_val.pkl")
    y_val = load_pkl("y_val.pkl")
    X_test = load_pkl("X_test.pkl")
    items = load_pkl("df_items.pkl")
    df_2017 = load_pkl("df_2017.pkl")
    df_test = pd.read_parquet("../input/df_test_v1.parquet", engine="pyarrow")
    num_days = 6

    val_pred, test_pred = model_training(
        X_train=X_train,
        y_train=y_train,
        X_val=X_val,
        y_val=y_val,
        X_test=X_test,
        df_items=items,
        num_days=num_days,
    )
    val_pred, test_pred = validation_and_prediction(val_pred=val_pred, y_val=y_val, df_2017=df_2017)
    make_submission(df_test, test_pred)
    logger.info("All done...")
