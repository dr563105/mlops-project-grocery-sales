import os
import pickle

import numpy as np
import mlflow
import pandas as pd
import prefect
import lightgbm as lgb
from prefect import flow, task
from sklearn.metrics import mean_squared_error

# load_dotenv()

# logging.basicConfig(
#     format="%(asctime)s %(levelname)-8s %(message)s",
#     filename="../logs/log_model_train.log",
#     level=logging.DEBUG,
# )
os.environ["AWS_PROFILE"] = "default"
# DB_USER = os.getenv('DB_USER')
# DB_PASSWORD = os.getenv('DB_PASSWORD')
# DB_ENDPOINT = os.getenv('DB_ENDPOINT')
# DB_NAME = os.getenv('DB_NAME')
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

TRACKING_SERVER_HOST = "ec2-54-226-7-218.compute-1.amazonaws.com"
mlflow.set_tracking_uri(f"http://{TRACKING_SERVER_HOST}:5000")
# postgresql://DB_USER:DB_PASSWORD@DB_ENDPOINT:5432/DB_NAME')
mlflow.set_experiment("LGBM-Mlflow-experiment")
# mlflow.set_tracking_uri('s3://S3_BUCKET_NAME')


def save_to_pkl(input, filename):
    """
    Pickles/Saves content into a file
    """
    logger = prefect.get_run_logger()
    logger.info(f"Saving {filename}")
    with open(f"../output/{filename}", "wb") as f_in:
        pickle.dump(input, f_in)


def savemodel_to_pkl(input, filename):
    """
    Pickles/Saves model into models directory
    """
    logger = prefect.get_run_logger()
    logger.info(f"Saving {filename}")
    with open(f"../models/{filename}", "wb") as f_in:
        pickle.dump(input, f_in)


def load_pkl(filename):
    """
    Unpickles/loads file and returns the contents
    """
    logger = prefect.get_run_logger()
    logger.info(f"Reading {filename}...")
    with open(f"../output/{filename}", "rb") as f_out:
        df = pickle.load(f_out)
    return df

@flow(name="Sales-predictor-modelling-valdition")
def model_training(X_train, y_train, X_val, y_val, X_test, df_items, df_2017, num_days):
    """
    Model parameters are set and model is trained
    """
    logger = prefect.get_run_logger()
    logger.info("Training models...")
    logger.info("Setting Params")
    # mlflow.lightgbm.autolog(disable=True)
    with mlflow.start_run(nested=True):
        param = {
            "objective": "regression",
            "metric": "l2",
            "verbosity": -1,
            "boosting_type": "gbdt",
            "n_estimators": 200,
            "early_stopping_round": 5,
            # "device": "gpu",
            # "gpu_platform_id": 0,
            # "gpu_device_id": 0,
        }
        param2 = {
            "num_leaves": 4,  #
            "feature_fraction": 0.7386878356648194,
            "bagging_fraction": 0.8459744550725283,
            "bagging_freq": 1,
            "max_depth": 2,
            "max_bin": 2,  # 249
            "learning_rate": 0.02,
            "min_data_in_leaf": 2,  # 200
        }
        param.update(param2)

        mlflow.log_params(param)

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
                weight=pd.concat([df_items["perishable"]] * num_days) * 0.25
                + 1,
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
            )
            # logger.info(
            #     "\n".join(
            #         ("%s: %.2f" % x)
            #         for x in sorted(
            #             zip(X_train.columns, bst.feature_importance("gain")),
            #             key=lambda x: x[1],
            #             reverse=True,
            #         )
            #     )
            # )

            val_pred.append(
                bst.predict(
                    X_val, num_iteration=bst.best_iteration or MAX_ROUNDS
                )
            )
            test_pred.append(
                bst.predict(
                    X_test, num_iteration=bst.best_iteration or MAX_ROUNDS
                )
            )

        # savemodel_to_pkl(input=bst, filename="model_lgbm.bin")
        mlflow.lightgbm.log_model(bst, artifact_path="models")
        del X_train
        # save_to_pkl(input=val_pred, filename="val_pred.pkl")
        save_to_pkl(input=test_pred, filename="test_pred.pkl")
        mlflow.log_artifact("../output/test_pred.pkl", artifact_path="output")
        # mlflow.lightgbm.log_model(test_pred, artifact_path="output")
        validation_and_prediction(val_pred=val_pred, y_val=y_val, df_2017=df_2017, items=df_items)

@task(name="validation and prediction module")
def validation_and_prediction(val_pred, y_val, df_2017, items):
    """
    Calculates error for the validation set and stores valadation predictions in a file
    """
    logger = prefect.get_run_logger()
    logger.info(
        "Validation mse: ",
        mean_squared_error(y_val, np.array(val_pred).transpose()),
    )

    weight = items["perishable"] * 0.25 + 1
    err = (y_val - np.array(val_pred).transpose()) ** 2
    err = err.sum(axis=1) * weight
    err = np.sqrt(err.sum() / weight.sum() / 16)
    logger.info(f"nwrmsle = {err}")
    mlflow.log_metric("nwrmsle", err)

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

    df_val_preds.index.set_names(
        ["store_nbr", "item_nbr", "date"], inplace=True
    )
    df_val_preds["unit_sales"] = np.clip(
        np.expm1(df_val_preds["unit_sales"]), 0, 1000
    )
    logger.info("Saving lgb cv predictions...")
    df_val_preds.reset_index().to_parquet(
        "../predictions/lgb_cv.parquet", index=False, engine="pyarrow"
    )

def main():
    """
    main function: loads variables and invokes other functions
    """
    logger = prefect.get_run_logger()
    X_train = load_pkl("X_train.pkl")
    y_train = load_pkl("y_train.pkl")
    X_val = load_pkl("X_val.pkl")
    y_val = load_pkl("y_val.pkl")
    X_test = load_pkl("X_test.pkl")
    items = load_pkl("df_items.pkl")
    df_2017 = load_pkl("df_2017.pkl")
    # df_test = pd.read_parquet("../input/df_test_v1.parquet", engine="pyarrow")
    num_days = 6

    model_training( X_train=X_train, y_train=y_train, X_val=X_val, y_val=y_val, 
                    X_test=X_test,
                    df_items=items,
                    df_2017=df_2017,
                    num_days=num_days,
    )

    logger.info("All done...")

if __name__ == "__main__":
    main()
