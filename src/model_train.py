import pickle

import numpy as np
import mlflow
import pandas as pd
import prefect
import lightgbm as lgb
from prefect import flow, task
from sklearn.metrics import mean_squared_error

TRACKING_SERVER_HOST = ""
mlflow.set_tracking_uri(f"http://{TRACKING_SERVER_HOST}:5000")
# mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("LGBM-Mlflow-experiment")

logger = prefect.get_run_logger()

@task(name="Pickle output")
def save_to_pkl(input, filename):
    """
    Pickles/Saves content into a file
    """
    logger.info(f"Saving {filename}")
    with open(f"../output/{filename}", "wb") as f_in:
        pickle.dump(input, f_in)


@task(name="Pickle Model")
def savemodel_to_pkl(input, filename):
    """
    Pickles/Saves model into models directory
    """
    logger.info(f"Saving {filename}")
    with open(f"../models/{filename}", "wb") as f_in:
        pickle.dump(input, f_in)


@task(name="Unpickling")
def load_pkl(filename):
    """
    Unpickles/loads file and returns the contents
    """
    logger.info(f"Reading {filename}...")
    with open(f"../output/{filename}", "rb") as f_out:
        df = pickle.load(f_out)
    return df


@task(name="Model Training")
def model_training(X_train, y_train, X_val, y_val, df_items, X_test, num_days):
    """
    Model parameters are set and model is trained
    """
    
    logger.info("Setting Params")
    mlflow.lightgbm.autolog(disable=True)
    with mlflow.start_run(nested=True):
        param = {
            "objective": "regression",
            "metric": "l2",
            "verbosity": 1,
            "boosting_type": "gbdt",
            "n_estimators": 500,
            "early_stopping_round": 50,
            "num_threads": -1,
        }
        param2 = {
            "num_leaves": 200,  #
            "feature_fraction": 0.7386878356648194,
            "bagging_fraction": 0.8459744550725283,
            "bagging_freq": 1,
            "max_depth": 4,
            "max_bin": 200,  # 249
            "learning_rate": 0.02,
            "min_data_in_leaf": 100,  # 200
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
        save_to_pkl(input=val_pred, filename="val_pred.pkl")
        save_to_pkl(input=test_pred, filename="test_pred.pkl")
    
    return val_pred, test_pred


@task(name="validation and prediction module")
def validation_and_prediction(val_pred, y_val, df_2017, items):
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
    df_val_preds.to_parquet(
        "../output/lgb_cv.parquet", index=False, engine="pyarrow"
    )
    logger.info("Storing cross validation results as artifact")
    mlflow.log_artifact(
        local_path="../output/lgb_cv.parquet", artifact_path="output"
    )


@task(name="Generate Future Sales")
def generate_future_sales(test_pred, df_2017, df_test):
    """
    A function to generate future sales
    """
    y_test = np.array(test_pred).transpose()
    df_preds = pd.DataFrame(
    y_test, index=df_2017.index,
    columns=pd.date_range("2017-08-16", periods=16)).stack().to_frame("unit_sales")
    df_preds.index.set_names(["store_nbr", "item_nbr", "date"], inplace=True)

    future_df = df_test[["id"]].join(df_preds, how="left").fillna(0)
    future_df["unit_sales"] = np.clip(np.expm1(future_df["unit_sales"]), 0, 1000)
    logger.info("Storing the predicted set as artifact")
    future_df.to_parquet("../predictions/lgb_preds_sep26.parquet", engine="pyarrow", index=False)


@flow(name="Sales-Model-Training-Validation-Forecasting")
def main():
    """
    Main function
    """
    X_train = load_pkl("X_train.pkl")
    y_train = load_pkl("y_train.pkl")
    X_val = load_pkl("X_val.pkl")
    y_val = load_pkl("y_val.pkl")
    df_items = load_pkl("df_items.pkl")
    df_2017 = load_pkl("df_2017.pkl")
    X_test = load_pkl("../input/grocerysalespickled/X_test.pkl")
    df_test = pd.read_parquet("../input/grocery-sales-forecasting-parquet/df_test.parquet", engine="pyarrow")
    num_days = 6

    val_pred, test_pred = model_training(X_train, y_train, X_val, y_val, df_items, X_test, num_days)
    validation_and_prediction(
            val_pred=val_pred, y_val=y_val, df_2017=df_2017, items=df_items
    )
    generate_future_sales(test_pred, df_2017, df_test)
    logger.info("All done")


if __name__ == "__main__":
    model_training()
