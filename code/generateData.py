from faker import Faker
import numpy as np
import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

num_rows = 100_000_000  # 100M rows
batch_size = 1_000_000
datadir = "data"
if not os.path.exists(datadir):
    os.makedirs(datadir)

def generate_batch(n):
    return pd.DataFrame({
        'user_id': np.random.randint(1, 10_000_000, size=n),
        'session_id': [fake.uuid4() for _ in range(n)],
        'timestamp': pd.to_datetime(np.random.randint(
            pd.Timestamp('2024-01-01').value // 10**9,
            pd.Timestamp('2024-06-01').value // 10**9,
            size=n), unit='s'),
        'page_url': np.random.choice(['/home', '/pricing', '/signup', '/blog', '/contact'], size=n),
        'referrer': np.random.choice(['google.com', 'facebook.com', 'twitter.com', 'direct'], size=n),
        'campaign': np.random.choice(['spring_sale', 'newsletter', 'retargeting', ''], size=n),
        'duration': np.random.exponential(scale=60, size=n).astype(int),
        'conversion_flag': np.random.choice([0, 1], size=n, p=[0.95, 0.05]),
        'device_type': np.random.choice(['mobile', 'desktop', 'tablet'], size=n),
        'browser': np.random.choice(['Chrome', 'Firefox', 'Safari', 'Edge', 'Opera'], size=n),
        'city': np.random.choice(['New York', 'London', 'Toronto', 'Mumbai', 'Berlin'], size=n),
        'landing_page': np.random.choice(['/home', '/pricing', '/signup', '/blog', '/contact'], size=n),
        'exit_page': np.random.choice(['/home', '/pricing', '/signup', '/blog', '/contact'], size=n),
        'session_duration': np.random.exponential(scale=300, size=n).astype(int),
        'is_new_user': np.random.choice([0, 1], size=n, p=[0.7, 0.3])
    })

if __name__ == "__main__":
    fake = Faker()

    # Write in chunks to Parquet
    for i in range(0, num_rows, batch_size):
        batch = generate_batch(batch_size)
        table = pa.Table.from_pandas(batch)

        filename = os.path.join(datadir, f'web_events_{i//batch_size}.parquet')
        pq.write_table(table, filename)
        print(f'Wrote batch {i // batch_size + 1}')
