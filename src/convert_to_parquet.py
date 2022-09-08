from syslog import LOG_WARNING
import numpy as np
import pandas as pd
import gc

def convert_to_parquet():
    df_train_all = pd.read_csv('../input/favoritagrocerysalesforecastingextracted/train.csv',
                    usecols=[1, 2, 3, 4, 5],
                    converters={'unit_sales': lambda u: np.log1p(float(u)) if float(u) > 0 else 0},
                    parse_dates=["date"], low_memory=False)

    save_as_parquet(df=df_train_all,filename='df_train_all.parquet')
    del df_train_all

    df2016_train = pd.read_csv('../input/favoritagrocerysalesforecastingextracted/train.csv',
                    usecols=[1, 2, 3, 4, 5],
                    dtype={'onpromotion': bool},
                    converters={'unit_sales': lambda u: np.log1p(float(u)) if float(u) > 0 else 0},
                    parse_dates=["date"],
                    skiprows=range(1, 66458909), low_memory=False) # from 2016-01-01

    save_as_parquet(df=df2016_train,filename='df2016_train.parquet')
    del df2016_train

    df_test = pd.read_csv("../input/favoritagrocerysalesforecastingextracted/test.csv",
                usecols=[0, 1, 2, 3, 4],
                dtype={'onpromotion': bool},
                parse_dates=["date"], low_memory= False).\
                set_index(['store_nbr', 'item_nbr', 'date'])

    save_as_parquet(df=df_test,filename='dftest.parquet')
    del df_test

    items = pd.read_csv("../input/favoritagrocerysalesforecastingextracted/items.csv").set_index("item_nbr")
    save_as_parquet(df=items,filename='items.parquet')
    stores = pd.read_csv("../input/favoritagrocerysalesforecastingextracted/stores.csv").set_index("store_nbr")
    save_as_parquet(df=stores,filename='stores.parquet')
    holidays = pd.read_csv("../input/favoritagrocerysalesforecastingextracted/holidays_events.csv")
    save_as_parquet(df=holidays,filename='holidays.parquet')
    oil = pd.read_csv( "../input/favoritagrocerysalesforecastingextracted/oil.csv")
    save_as_parquet(df=oil,filename='oil.parquet')
    transactions = pd.read_csv("../input/favoritagrocerysalesforecastingextracted/transactions.csv")
    save_as_parquet(df=transactions,filename='transactions.parquet')
    submissions = pd.read_csv("../input/favoritagrocerysalesforecastingextracted/sample_submission.csv")
    save_as_parquet(df=submissions,filename='submissions.parquet')
    gc.collect()

def save_as_parquet(df, filename):
    df.to_parquet(path=f'../working/{filename}',engine='pyarrow')

if __name__ == '__main__':
    convert_to_parquet()



