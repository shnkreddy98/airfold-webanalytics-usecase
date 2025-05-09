from ingest import ingest_data
from logging_utils import setup_logging

import logging
import os
import time

data_dir = '/app/data/parquet_data'

if __name__ == "__main__":
    log_file = setup_logging()
    
    files = [file for file in os.listdir(data_dir) if file.endswith('parquet')]
    for file in files:
        try:
            ingest_data(file)
        except Exception as e:
            logging.error(e)
            logging.info("Restarting after 5 seconds")
            time.sleep(5)
            ingest_data(file)
