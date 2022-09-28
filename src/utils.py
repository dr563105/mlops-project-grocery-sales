import pickle

import pandas as pd
import prefect


def read_parquet_files(filename: str):
    """
    Read parquet file format for given filename and returns the contents
    """
    # logger = prefect.get_run_logger()
    # logger.info(f"Reading {filename}")
    df = pd.read_parquet(filename, engine="pyarrow")
    return df


def save_as_parquet(df: pd.DataFrame, filename: str):
    """
    Saves contents in parquet file format using Apache pyarrow engine
    """
    df.to_parquet(path=f"../{filename}", engine="pyarrow")


def save_to_pkl(input, filename: str):
    """
    Pickles/Saves content into a file
    """
    logger = prefect.get_run_logger()
    logger.info(f"Saving {filename}")
    with open(f"../output/{filename}", "wb") as f_in:
        pickle.dump(input, f_in)


def savemodel_to_pkl(input, filename: str):
    """
    Pickles/Saves model into models directory
    """
    logger = prefect.get_run_logger()
    logger.info(f"Saving {filename}")
    with open(f"../models/{filename}", "wb") as f_in:
        pickle.dump(input, f_in)


def load_pkl(filename: str) -> pd.DataFrame:
    """
    Unpickles/loads file and returns the contents
    """
    logger = prefect.get_run_logger()
    logger.info(f"Reading {filename}...")
    with open(f"../output/{filename}", "rb") as f_out:
        df = pickle.load(f_out)
    return df
