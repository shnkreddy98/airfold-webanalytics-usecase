from ingest import ingest_data, write_idx, read_idx
from logging_utils import setup_logging

import logging
import os
import time

last_file = './data/last_file.txt'

if __name__ == "__main__":
    log_file = setup_logging()

    if not os.path.exists(last_file):
        write_idx(last_file, 0)

    start_idx = read_idx(last_file)
    end_idx = 100

    for idx, filepart in enumerate(range(start_idx, end_idx)):
        start_time = time.time()

        file = "web_events_{}.parquet".format(str(filepart))
        logging.info(f"Ingesting {idx+1} of {end_idx} files")
        logging.info(f"Ingesting {file}")
        try:
            ingest_data(file)
        except:
            write_idx(last_file, filepart)
            logging.error(f"Data ingestion stopped at {idx} at {file}")
        end_time = time.time()
        logging.info(f"Data Ingested in {(end_time-start_time)//60} minutes")
