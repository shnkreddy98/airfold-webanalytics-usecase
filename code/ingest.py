import logging
from dotenv import load_dotenv
import os
import requests
import json
import time
import pandas as pd

load_dotenv()

data_dir = '/app/data/parquet_data'

transformed_data_dir = 'app/data/json_data'

def check_create_file(filename):
    if not os.path.exists(filename):
        os.makedirs(filename)
        return True
    return False

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
            'Content-Type': 'application/json',
            'Connection': 'keep-alive'
        },
        json=data
    )

def ingest_data(file):
    check_create_file(transformed_data_dir)

    filename = os.path.join(data_dir, file)
    data = pd.read_parquet(filename)

    step = 10000
    total_rows = data.shape[0]

    for idx, i in enumerate(range(0, total_rows, step)):
        filepart = file.split(".")[0]
        end_i = min(i + step, total_rows)
        logging.info(f"Ingesting data part {idx} of {total_rows//step}")
        new_data = data[i:end_i]
        filename = os.path.join(transformed_data_dir, f"{filepart}_{idx+i}_{idx+end_i}.json")
        new_data.to_json(filename, orient='records')
        append_source("web_events", filename)
        time.sleep(1)

    