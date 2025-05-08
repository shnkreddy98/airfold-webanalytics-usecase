import logging
from dotenv import load_dotenv
import os
import requests
import json
import time
import numpy as np
import pandas as pd

load_dotenv()

data_dir = './data'

transformed_data_dir = './data/json_data'
internal_idx_file = './data/internal_idx.txt'

def check_create_file(filename):
    if not os.path.exists(filename):
        os.makedirs(filename)
        return True
    return False

def read_idx(filename):
    with open(filename, "r") as f:
        return int(f.read())

def write_idx(filename, idx):
    with open(filename, "w+") as f:
        f.write(str(idx))

def append_source(table, filename):
    logging.info(f"Appending Data {filename} to Airfold")
    auth = os.getenv('auth_code')

    with open(filename, 'r') as f:
        data = json.load(f)
    url = 'https://api.us.airfold.co/v1/events/{}'

    res = requests.post(
        url.format(table),
        headers={
            'Authorization': 'Bearer {}'.format(auth),
            'Content-Type': 'application/json'
        },
        json=data
    )

def ingest_data(file):
    check_create_file(transformed_data_dir)
    if not os.path.exists(internal_idx_file):
        write_idx(internal_idx_file, 0)

    filename = os.path.join(data_dir, file)
    data = pd.read_parquet(filename)

    step = 10000
    total_rows = data.shape[0]

    start_idx = read_idx(internal_idx_file)

    for idx, i in enumerate(range(start_idx, total_rows, step)):
        filepart = file.split(".")[0]
        end_i = min(i + step, total_rows)
        logging.info(f"Ingesting data part {idx} of {total_rows//step}")
        new_data = data[i:end_i]
        filename = os.path.join(transformed_data_dir, f"{filepart}_{start_idx+i}_{start_idx+end_i}.json")
        new_data.to_json(filename, orient='records')
        try:            
            append_source("web_events", filename)
        except:
            write_idx(start_idx+i)
        time.sleep(1)

    