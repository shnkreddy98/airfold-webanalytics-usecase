from ingest import ingest_data, write_idx, read_idx
from logging_utils import setup_logging

import logging
import os
import sys

csv_files_fmt = 'web_events_{}.csv'
last_file = './data/last_file_{}.txt'
last_idx_file = './data/last_idx_{}.txt'

if __name__ == "__main__":
    log_file = setup_logging()
    part = sys.argv[1]
    last_file = last_file.format(part)
    last_idx_file = last_idx_file.format(part)

    if not os.path.exists(last_file):
        write_idx(last_file, int(part)*25)

    start_idx = read_idx(last_file)

    for idx in range(start_idx, int(part)*25+24):
        file = csv_files_fmt.format(idx)
        logging.info(f"Ingesting {file}")
        ingest_data(file, last_idx_file, part)
        logging.info("Data Ingested")
        write_idx(last_file, idx)
        write_idx(last_idx_file, 0)
