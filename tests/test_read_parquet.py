import pandas as pd

from src.utils import read_parquet_files


def test_read_parquet():
    """
    Tests whether the read parquet's shape and the one in data_process are same
    """
    input = "./input/oil.parquet"
    df_oil = read_parquet_files(filename=input)
    df2 = pd.read_parquet(input, engine="pyarrow")
    assert df_oil.shape == df2.shape
