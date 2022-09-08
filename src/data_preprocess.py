import pickle
import logging
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

log_format = "%(asctime)s %(levelname)-8s %(message)s"
logging.basicConfig(
    format=log_format,
    filename="../logs/log_preprocess.log",
    level=logging.DEBUG,
)
logger = logging.getLogger()


def read_parquet_files(filename):
    """
    Read parquet file format for given filename and returns the contents
    """
    logger.info("Reading Parquet files...")
    df = pd.read_parquet(filename, engine="pyarrow")
    # df_stores = pd.read_parquet('../input/stores.parquet',engine='pyarrow')
    return df


def save_to_pkl(df, filename):
    """
    Pickles/Saves content into a file
    """
    logger.info(f"Saving {filename}")
    with open(f"../output/{filename}", "wb") as f_in:
        pickle.dump(df, f_in)


def feature_engg_1(df2016_train, df_test, df_items):
    """
    Takes pandas dataframes as inputs and add new features
    """
    logger.info("Feature engineering...")
    le = LabelEncoder()

    df_items["family"] = le.fit_transform(df_items["family"].to_numpy())
    # df_stores['city'] = le.fit_transform(df_stores['city'].to_numpy())
    # df_stores['state'] = le.fit_transform(df_stores['state'].to_numpy())
    # df_stores['type'] = le.fit_transform(df_stores['type'].to_numpy())

    logger.info("Creating df_2017...")
    df_2017 = df2016_train.loc[df2016_train["date"] >= datetime(2017, 1, 1)]
    del df2016_train

    logger.info("Creating promo_2017_train df...")
    promo_2017_train = (
        df_2017.set_index(["store_nbr", "item_nbr", "date"])[["onpromotion"]]
        .unstack(level=-1)
        .fillna(False)
    )
    promo_2017_train.columns = promo_2017_train.columns.get_level_values(1)
    promo_2017_test = df_test[["onpromotion"]].unstack(level=-1).fillna(False)
    promo_2017_test.columns = promo_2017_test.columns.get_level_values(1)
    promo_2017_test = promo_2017_test.reindex(promo_2017_train.index).fillna(
        False
    )
    promo_2017 = pd.concat([promo_2017_train, promo_2017_test], axis=1)
    del promo_2017_test, promo_2017_train

    df_2017 = (
        df_2017.set_index(["store_nbr", "item_nbr", "date"])[["unit_sales"]]
        .unstack(level=-1)
        .fillna(0)
    )
    df_2017.columns = df_2017.columns.get_level_values(1)

    df_2017_item = df_2017.groupby("item_nbr")[df_2017.columns].sum()
    promo_2017_item = promo_2017.groupby("item_nbr")[promo_2017.columns].sum()

    df_items = df_items.reindex(df_2017.index.get_level_values(1))
    # df_stores = df_stores.reindex(df_2017.index.get_level_values(0))

    # df_2017_store_class = df_2017.reset_index()
    # df_2017_store_class['class'] = df_items['class'].values
    # df_2017_store_class_index = df_2017_store_class[['class', 'store_nbr']]
    # df_2017_store_class = df_2017_store_class.groupby(['class', 'store_nbr'])
    # [df_2017.columns].sum()

    # df_2017_promo_store_class = promo_2017.reset_index()
    # df_2017_promo_store_class['class'] = df_items['class'].values
    # df_2017_promo_store_class_index = df_2017_promo_store_class[['class', 'store_nbr']]
    # df_2017_promo_store_class = df_2017_promo_store_class.groupby
    # (['class', 'store_nbr'])[promo_2017.columns].sum()

    save_to_pkl(df=df_2017, filename="df_2017.pkl")
    save_to_pkl(df=df_items, filename="df_items.pkl")
    return (
        df_2017,
        promo_2017,
        df_2017_item,
        promo_2017_item,
    )  # , df_2017_store_class, df_2017_store_class_index,df_2017_promo_store_class


def get_timespan(df, dt, minus, periods, freq="D"):
    """
    Taking start date, period and freq as input, returns datetimeindex based on their combination
    """
    return df[
        pd.date_range(dt - timedelta(days=minus), periods=periods, freq=freq)
    ]


def prepare_dataset(df, promo_df, t2017, is_train=True, name_prefix=None):
    """
    Takes pandas dataframes as inputs and add new features
    """
    X = {
        "promo_14_2017": get_timespan(promo_df, t2017, 14, 14)
        .sum(axis=1)
        .values,
        "promo_60_2017": get_timespan(promo_df, t2017, 60, 60)
        .sum(axis=1)
        .values,
        # "promo_140_2017": get_timespan(promo_df, t2017, 140, 140).sum(axis=1).values,
        "promo_3_2017_aft": get_timespan(
            promo_df, t2017 + timedelta(days=16), 15, 3
        )
        .sum(axis=1)
        .values,
        "promo_7_2017_aft": get_timespan(
            promo_df, t2017 + timedelta(days=16), 15, 7
        )
        .sum(axis=1)
        .values,
        #   "promo_14_2017_aft": get_timespan(promo_df, t2017 + timedelta(days=16), 15, 14).sum(axis=1).values,
    }

    for i in [3, 7, 14]:
        tmp1 = get_timespan(df, t2017, i, i)
        tmp2 = (get_timespan(promo_df, t2017, i, i) > 0) * 1

        X["has_promo_mean_%s" % i] = (
            (tmp1 * tmp2.replace(0, np.nan)).mean(axis=1).values
        )
        X["has_promo_mean_%s_decay" % i] = (
            (tmp1 * tmp2.replace(0, np.nan) * np.power(0.9, np.arange(i)[::-1]))
            .sum(axis=1)
            .values
        )

        X["no_promo_mean_%s" % i] = (
            (tmp1 * (1 - tmp2).replace(0, np.nan)).mean(axis=1).values
        )
        X["no_promo_mean_%s_decay" % i] = (
            (
                tmp1
                * (1 - tmp2).replace(0, np.nan)
                * np.power(0.9, np.arange(i)[::-1])
            )
            .sum(axis=1)
            .values
        )

    for i in [3, 7, 14]:
        tmp = get_timespan(df, t2017, i, i)
        X["diff_%s_mean" % i] = tmp.diff(axis=1).mean(axis=1).values
        X["mean_%s_decay" % i] = (
            (tmp * np.power(0.9, np.arange(i)[::-1])).sum(axis=1).values
        )
        X["mean_%s" % i] = tmp.mean(axis=1).values
        X["median_%s" % i] = tmp.median(axis=1).values
        X["min_%s" % i] = tmp.min(axis=1).values
        X["max_%s" % i] = tmp.max(axis=1).values
        X["std_%s" % i] = tmp.std(axis=1).values

    for i in [3, 7, 14]:
        tmp = get_timespan(df, t2017 + timedelta(days=-7), i, i)
        X["diff_%s_mean_2" % i] = tmp.diff(axis=1).mean(axis=1).values
        X["mean_%s_decay_2" % i] = (
            (tmp * np.power(0.9, np.arange(i)[::-1])).sum(axis=1).values
        )
        X["mean_%s_2" % i] = tmp.mean(axis=1).values
        X["median_%s_2" % i] = tmp.median(axis=1).values
        X["min_%s_2" % i] = tmp.min(axis=1).values
        X["max_%s_2" % i] = tmp.max(axis=1).values
        X["std_%s_2" % i] = tmp.std(axis=1).values

    # for i in [7, 14]:
    #     tmp = get_timespan(df, t2017, i, i)
    #     X['has_sales_days_in_last_%s' % i] = (tmp > 0).sum(axis=1).values
    #     X['last_has_sales_day_in_last_%s' % i] = i - ((tmp > 0) * np.arange(i)).max(axis=1).values
    #     X['first_has_sales_day_in_last_%s' % i] = ((tmp > 0) * np.arange(i, 0, -1)).max(axis=1).values

    #     tmp = get_timespan(promo_df, t2017, i, i)
    #     X['has_promo_days_in_last_%s' % i] = (tmp > 0).sum(axis=1).values
    #     X['last_has_promo_day_in_last_%s' % i] = i - ((tmp > 0) * np.arange(i)).max(axis=1).values
    #     X['first_has_promo_day_in_last_%s' % i] = ((tmp > 0) * np.arange(i, 0, -1)).max(axis=1).values

    # tmp = get_timespan(promo_df, t2017 + timedelta(days=16), 15, 15)
    # X['has_promo_days_in_after_15_days'] = (tmp > 0).sum(axis=1).values
    # X['last_has_promo_day_in_after_15_days'] = 15 - ((tmp > 0) * np.arange(15)).max(axis=1).values
    # X['first_has_promo_day_in_after_15_days'] = ((tmp > 0) * np.arange(15, 0, -1)).max(axis=1).values

    # for i in range(1, 16):
    #     X['day_%s_2017' % i] = get_timespan(df, t2017, i, 1).values.ravel()

    for i in range(7):
        X[f"mean_4_dow{i}_2017"] = (
            get_timespan(df, t2017, 28 - i, 4, freq="7D").mean(axis=1).values
        )
        X[f"mean_20_dow{i}_2017"] = (
            get_timespan(df, t2017, 140 - i, 20, freq="7D").mean(axis=1).values
        )

    # for i in range(16):
    #     X[f"promo_{i}"] = promo_df[t2017 + timedelta(days=i)].values#.astype(np.uint8)

    X = pd.DataFrame(X)

    if is_train:
        y = df[pd.date_range(t2017, periods=16)].to_numpy()
        return X, y
    if name_prefix is not None:
        X.columns = ["%s_%s" % (name_prefix, c) for c in X.columns]
    return X


def feature_engg_2(df_2017, promo_2017, df_2017_item, promo_2017_item):
    """
    Takes pandas dataframes as inputs and add new features.
    Finally collates all the dataframes into X_train, y_train, X_val, y_val and X_test
    """
    t2017 = date(2017, 6, 14)
    num_days = 6
    X_l, y_l = [], []
    for i in range(num_days):
        delta = timedelta(days=7 * i)
        X_tmp, y_tmp = prepare_dataset(df_2017, promo_2017, t2017 + delta)

        X_tmp2 = prepare_dataset(
            df_2017_item,
            promo_2017_item,
            t2017 + delta,
            is_train=False,
            name_prefix="item",
        )
        X_tmp2.index = df_2017_item.index
        X_tmp2 = X_tmp2.reindex(df_2017.index.get_level_values(1)).reset_index(
            drop=True
        )

        # X_tmp3 = prepare_dataset(df_2017_store_class, df_2017_promo_store_class, t2017 + delta, is_train=False, name_prefix='store_class')
        # X_tmp3.index = df_2017_store_class.index
        # X_tmp3 = X_tmp3.reindex(df_2017_store_class_index).reset_index(drop=True)

        X_tmp = pd.concat([X_tmp, X_tmp2, df_items.reset_index()], axis=1)
        X_l.append(X_tmp)
        y_l.append(y_tmp)

        del X_tmp, X_tmp2, y_tmp

    logger.info("Creating X_train, y_train...")
    X_train = pd.concat(X_l, axis=0)
    y_train = np.concatenate(y_l, axis=0)
    del X_l, y_l

    save_to_pkl(df=X_train, filename="X_train.pkl")
    del X_train
    save_to_pkl(df=y_train, filename="y_train.pkl")
    del y_train

    logger.info("Creating X_val, y_val...")
    X_val, y_val = prepare_dataset(df_2017, promo_2017, date(2017, 7, 26))
    X_val2 = prepare_dataset(
        df_2017_item,
        promo_2017_item,
        date(2017, 7, 26),
        is_train=False,
        name_prefix="item",
    )
    X_val2.index = df_2017_item.index
    X_val2 = X_val2.reindex(df_2017.index.get_level_values(1)).reset_index(
        drop=True
    )

    # X_val3 = prepare_dataset(df_2017_store_class,
    #   df_2017_promo_store_class, date(2017, 7, 26), is_train=False, name_prefix='store_class')
    # X_val3.index = df_2017_store_class.index
    # X_val3 = X_val3.reindex(df_2017_store_class_index).reset_index(drop=True)

    X_val = pd.concat([X_val, X_val2, df_items.reset_index()], axis=1)
    del X_val2
    save_to_pkl(df=X_val, filename="X_val.pkl")
    del X_val
    save_to_pkl(df=y_val, filename="y_val.pkl")
    del y_val

    logger.info("Creating X_test...")
    X_test = prepare_dataset(
        df_2017, promo_2017, date(2017, 8, 16), is_train=False
    )

    X_test2 = prepare_dataset(
        df_2017_item,
        promo_2017_item,
        date(2017, 8, 16),
        is_train=False,
        name_prefix="item",
    )
    X_test2.index = df_2017_item.index
    X_test2 = X_test2.reindex(df_2017.index.get_level_values(1)).reset_index(
        drop=True
    )

    # X_test3 = prepare_dataset(df_2017_store_class, df_2017_promo_store_class, date(2017, 8, 16), is_train=False, name_prefix='store_class')
    # X_test3.index = df_2017_store_class.index
    # X_test3 = X_test3.reindex(df_2017_store_class_index).reset_index(drop=True)

    X_test = pd.concat([X_test, X_test2, df_items.reset_index()], axis=1)

    del X_test2, df_2017_item, promo_2017_item
    save_to_pkl(df=X_test, filename="X_test.pkl")


if __name__ == "__main__":
    df2016_train = read_parquet_files(filename="../input/df2016_train.parquet")
    df_test = read_parquet_files(filename="../input/df_test.parquet")
    df_items = read_parquet_files(filename="../input/df_items.parquet")
    df_2017, promo_2017, df_2017_item, promo_2017_item = feature_engg_1(
        df2016_train, df_test, df_items
    )
    feature_engg_2(df_2017, promo_2017, df_2017_item, promo_2017_item)
    logger.info("All done...")
