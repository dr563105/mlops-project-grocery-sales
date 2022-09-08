import pandas as pd
import numpy as np
import pickle
import lightgbm as lgb
from sklearn.metrics import mean_squared_error
import logging

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',filename="../logs/log_model_train.log", level=logging.DEBUG)
logger = logging.getLogger()

def save_to_pkl(input, filename):
    logger.info(f"Saving {filename}...")
    with open(f'../models/{filename}','wb') as f_in:
        pickle.dump(input, f_in)

def load_pkl(filename):
    logger.info(f"Reading {filename}...")
    with open(f'../output/{filename}','rb') as f_out:
        df = pickle.load(f_out)
    return df

def model_training(X_train, y_train, X_val, y_val, X_test, df_items, num_days):
    logger.info("Training models...")
    logger.info("Setting Params")
    params = {
        'num_leaves': 80,
        'objective': 'regression',
        'min_data_in_leaf': 200,
        'learning_rate': 0.02,
        'feature_fraction': 0.8,
        'bagging_fraction': 0.7,
        'bagging_freq': 1,
        'metric': 'l2',
        'num_threads': 16
    }
    
    MAX_ROUNDS = 1
    val_pred = []
    test_pred = []
    cate_vars = []
    for i in range(16):
        logger.info("=" * 50)
        logger.info("Step %d" % (i+1))
        logger.info("=" * 50)
        dtrain = lgb.Dataset(
            X_train, label=y_train[:, i],
            categorical_feature=cate_vars,
            weight=pd.concat([df_items["perishable"]] * num_days) * 0.25 + 1)
        dval = lgb.Dataset(
            X_val, label=y_val[:, i], reference=dtrain,
            weight=df_items["perishable"] * 0.25 + 1,
            categorical_feature=cate_vars)
        bst = lgb.train(
            params, dtrain, num_boost_round=MAX_ROUNDS,
            valid_sets=[dtrain, dval], early_stopping_rounds=125, verbose_eval=50)
        logger.info("\n".join(("%s: %.2f" % x) for x in sorted(
            zip(X_train.columns, bst.feature_importance("gain")),
            key=lambda x: x[1], reverse=True)))

        val_pred.append(bst.predict(
            X_val, num_iteration=bst.best_iteration or MAX_ROUNDS))
        test_pred.append(bst.predict(
            X_test, num_iteration=bst.best_iteration or MAX_ROUNDS))
    
    save_to_pkl(input=bst,filename='model_lgbm.bin')

    return val_pred, test_pred

def validation_and_prediction(val_pred, y_val, df_2017):
    logger.info("Validation mse:", mean_squared_error(
    y_val, np.array(val_pred).transpose()))

    weight = items["perishable"] * 0.25 + 1
    err = (y_val - np.array(val_pred).transpose())**2
    err = err.sum(axis=1) * weight
    err = np.sqrt(err.sum() / weight.sum() / 16)
    logger.info(f'nwrmsle = {err}')

    y_val = np.array(val_pred).transpose()
    df_preds = pd.DataFrame(
        y_val, index=df_2017.index,
        columns=pd.date_range("2017-07-26", periods=16)).stack().to_frame("unit_sales")

    df_preds.index.set_names(["store_nbr", "item_nbr", "date"], inplace=True)
    df_preds["unit_sales"] = np.clip(np.expm1(df_preds["unit_sales"]), 0, 1000)
    df_preds.reset_index().to_parquet('../output/lgb_cv.parquet', index=False, engine='pyarrow')

def make_submission(df_test, test_pred):
    print("Making submission...")
    y_test = np.array(test_pred).transpose()
    df_preds = pd.DataFrame(
        y_test, index=df_2017.index,
        columns=pd.date_range("2017-08-16", periods=16)).stack().to_frame("unit_sales")
    df_preds.index.set_names(["store_nbr", "item_nbr", "date"], inplace=True)

    submission = df_test[["id"]].join(df_preds, how="left").fillna(0)
    submission["unit_sales"] = np.clip(np.expm1(submission["unit_sales"]), 0, 1000)
    submission.to_parquet('../output/lgb_sub.parquet', float_format='%.4f', index=None, engine='pyarrow')

if __name__ == '__main__':
    X_train = load_pkl('X_train.pkl') 
    y_train = load_pkl('y_train.pkl')
    X_val = load_pkl('X_val.pkl')
    y_val = load_pkl('y_val.pkl')
    X_test = load_pkl('X_test.pkl')
    items = load_pkl('df_items.pkl')
    df_2017 = load_pkl('df_2017.pkl')
    df_test = pd.read_parquet(
                '../input/dftest.parquet',  engine='pyarrow')
    num_days = 6

    val_pred, test_pred = model_training(X_train=X_train, y_train=y_train, X_val=X_val, y_val=y_val, X_test=X_test, df_items=items, num_days=num_days)
    validation_and_prediction(val_pred=val_pred,y_val=y_val, df_2017=df_2017)
    make_submission(df_test, test_pred)
    logger.info("All done...")
