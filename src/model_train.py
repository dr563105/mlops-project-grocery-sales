import os

import numpy as np
import mlflow
import pandas as pd
import prefect
import lightgbm as lgb
from prefect import flow, task
from sklearn.metrics import mean_squared_error

from src.utils import load_pkl, save_to_pkl, savemodel_to_pkl

tracking_server = os.getenv("EC2_IP")
mlflow.set_tracking_uri(f"http://{tracking_server}:5000")
# mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("LGBM-Mlflow-experiment")


@task(name="Model Training")
def model_training(
    X_train: pd.DataFrame,
    y_train: pd.DataFrame,
    X_val: pd.DataFrame,
    y_val: pd.DataFrame,
    df_items: pd.DataFrame,
    X_test: pd.DataFrame,
    num_days: int = 6,
) -> pd.DataFrame:
    """
    Model parameters are set and model is trained
    """
    logger = prefect.get_run_logger()
    logger.info("Setting Params")
    mlflow.lightgbm.autolog(disable=True)
    param = {
        "objective": "regression",
        "metric": "l2",
        "verbosity": 0,
        "boosting_type": "gbdt",
        "n_estimators": 100,  # 130
        "early_stopping_round": 10,
        "num_threads": 6,
    }
    param2 = {
        "num_leaves": 4,  # 50
        "feature_fraction": 0.7386878356648194,
        "bagging_fraction": 0.8459744550725283,
        "bagging_freq": 5,
        "max_depth": 2,  # 10
        "max_bin": 3,  # 50
        "learning_rate": 0.02,
        "min_data_in_leaf": 2,  # 10
    }
    param.update(param2)

    mlflow.log_params(param)

    MAX_ROUNDS = 0.5
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
        )
        # logger.debug(
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
            bst.predict(X_val, num_iteration=bst.best_iteration or MAX_ROUNDS)
        )
        test_pred.append(
            bst.predict(X_test, num_iteration=bst.best_iteration or MAX_ROUNDS)
        )

    savemodel_to_pkl(input=bst, filename="model_lgbm.bin")
    mlflow.lightgbm.log_model(bst, artifact_path="models")
    save_to_pkl(input=val_pred, filename="val_pred.pkl")
    save_to_pkl(input=test_pred, filename="test_pred.pkl")
    return val_pred, test_pred


@task(name="validation and prediction module")
def validation_and_prediction(
    val_pred: pd.DataFrame,
    y_val: pd.DataFrame,
    df_2017: pd.DataFrame,
    items: pd.DataFrame,
):
    """
    Calculates error for the validation set and stores valadation predictions in a file
    """
    logger = prefect.get_run_logger()
    logger.info(
        f"Validation mse: \
                {mean_squared_error(y_val, np.array(val_pred).transpose())}"
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
            columns=pd.date_range("2017-07-26", periods=16),
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
    df_val_preds.to_parquet("../output/lgb_cv.parquet", engine="pyarrow")
    logger.info("Storing cross validation results as artifact")


@task(name="Generate Future Sales")
def generate_future_sales(
    test_pred: pd.DataFrame, df_2017: pd.DataFrame, df_test: pd.DataFrame
):
    """
    A function to generate future sales
    """
    logger = prefect.get_run_logger()
    y_test = np.array(test_pred).transpose()
    df_preds = (
        pd.DataFrame(
            y_test,
            index=df_2017.index,
            columns=pd.date_range("2017-08-16", periods=16),
        )
        .stack()
        .to_frame("unit_sales")
    )
    df_preds.index.set_names(["store_nbr", "item_nbr", "date"], inplace=True)

    future_df = df_test[["id"]].join(df_preds, how="left").fillna(0)
    future_df["unit_sales"] = np.clip(
        np.expm1(future_df["unit_sales"]), 0, 1000
    )
    logger.info("Storing the predicted set as artifact")
    future_df.to_parquet("../predictions/lgb_preds.parquet", engine="pyarrow")
    mlflow.log_artifact(
        "../predictions/lgb_preds.parquet", artifact_path="predictions"
    )


@flow(name="Sales-Model-Training-Validation-Forecasting")
def main():
    """
    Main function
    """
    logger = prefect.get_run_logger()

    X_train = load_pkl("X_train.pkl")
    y_train = load_pkl("y_train.pkl")
    X_val = load_pkl("X_val.pkl")
    y_val = load_pkl("y_val.pkl")
    df_items = load_pkl("df_items.pkl")
    df_2017 = load_pkl("df_2017.pkl")
    X_test = load_pkl("X_test.pkl")
    df_test = pd.read_parquet("../input/df_test.parquet", engine="pyarrow")

    with mlflow.start_run():

        val_pred, test_pred = model_training(
            X_train=X_train,
            y_train=y_train,
            X_val=X_val,
            y_val=y_val,
            df_items=df_items,
            X_test=X_test,
        )

        validation_and_prediction(
            val_pred=val_pred, y_val=y_val, df_2017=df_2017, items=df_items
        )
        generate_future_sales(test_pred, df_2017, df_test)

    logger.info("All done")


if __name__ == "__main__":
    main()
