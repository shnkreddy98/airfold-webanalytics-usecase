from faker import Faker
import numpy as np
import os
import pandas as pd
import random
import uuid

# Set constants
num_rows = 100_000_000  # 100M rows
batch_size = 1_000_000  # Process 1M rows at a time
datadir = "data"
if not os.path.exists(datadir):
    os.makedirs(datadir)

# Define possible pages and their transition probabilities
pages = ['/home', '/products', '/pricing', '/blog', '/about', '/contact', '/signup', '/login', '/checkout']

# Page transition matrix (rows=from, columns=to)
transition_matrix = {
    '/home': {'self': 0.1, '/products': 0.3, '/pricing': 0.2, '/blog': 0.15, '/about': 0.1, '/contact': 0.05, '/signup': 0.05, '/login': 0.05, '/checkout': 0, 'exit': 0.1},
    '/products': {'self': 0.1, '/home': 0.1, '/pricing': 0.3, '/blog': 0.05, '/about': 0.05, '/contact': 0.05, '/signup': 0.05, '/login': 0.05, '/checkout': 0.15, 'exit': 0.15},
    '/pricing': {'self': 0.05, '/home': 0.1, '/products': 0.2, '/blog': 0.05, '/about': 0.05, '/contact': 0.05, '/signup': 0, '/login': 0.15, '/checkout': 0.2, 'exit': 0.15},
    '/blog': {'self': 0.15, '/home': 0.15, '/products': 0.1, '/pricing': 0.05, '/about': 0.2, '/contact': 0.1, '/signup': 0.05, '/login': 0.05, '/checkout': 0, 'exit': 0.15},
    '/about': {'self': 0.05, '/home': 0.15, '/products': 0.1, '/pricing': 0.05, '/blog': 0.1, '/contact': 0.3, '/signup': 0.05, '/login': 0.05, '/checkout': 0, 'exit': 0.15},
    '/contact': {'self': 0.05, '/home': 0.15, '/products': 0.05, '/pricing': 0.05, '/blog': 0.05, '/about': 0.1, '/signup': 0.05, '/login': 0.05, '/checkout': 0, 'exit': 0.45},
    '/signup': {'self': 0.05, '/home': 0.1, '/products': 0.1, '/pricing': 0.05, '/blog': 0.05, '/about': 0.05, '/contact': 0.05, '/login': 0.05, '/checkout': 0.1, 'exit': 0.4},
    '/login': {'self': 0.05, '/home': 0.1, '/products': 0.1, '/pricing': 0.1, '/blog': 0.05, '/about': 0.05, '/contact': 0.05, '/signup': 0.05, '/checkout': 0.25, 'exit': 0.2},
    '/checkout': {'self': 0.05, '/home': 0.1, '/products': 0.1, '/pricing': 0.05, '/blog': 0.05, '/about': 0.05, '/contact': 0.05, '/signup': 0.05, '/login': 0.05, 'exit': 0.45}
}

# Function to generate a sequence of pages for a session based on transition probabilities
def generate_page_sequence(max_pages=10, min_pages=1):
    # Randomly select landing page with custom weights (home is most common landing page)
    landing_weights = [0.4, 0.15, 0.1, 0.15, 0.05, 0.05, 0.05, 0.05, 0]  # No direct landings on checkout
    current_page = random.choices(pages, weights=landing_weights)[0]
    
    page_sequence = [current_page]
    
    # Generate 0 to max_pages-1 additional page views (at least 1 page per session)
    while len(page_sequence) < max_pages:
        # Get transition probabilities for current page
        transitions = transition_matrix[current_page]
        
        # Decide next action based on probabilities
        options = list(transitions.keys())
        probabilities = list(transitions.values())
        next_action = random.choices(options, weights=probabilities)[0]
        
        # If exit, end the sequence
        if next_action == 'exit':
            break
        
        # If self-transition (refreshing the same page), record it
        if next_action == 'self':
            page_sequence.append(current_page)
        else:
            # Otherwise move to the new page
            current_page = next_action
            page_sequence.append(current_page)
    
    # Ensure at least min_pages in sequence
    while len(page_sequence) < min_pages:
        page_sequence.append(random.choice(pages))
    
    return page_sequence

def generate_batch(n):
    """Generate batch of n page views (not n sessions)"""
    
    # This approach creates page views incrementally to match batch_size
    all_page_views = []
    pages_to_generate = n
    
    while len(all_page_views) < pages_to_generate:
        # Create session attributes
        session_id = str(uuid.uuid4())
        user_id = np.random.randint(1, 10_000_000)
        
        # Session-level attributes
        referrer = np.random.choice(['google.com', 'facebook.com', 'twitter.com', 'direct', 'email'], p=[0.4, 0.2, 0.1, 0.2, 0.1])
        campaign = np.random.choice(['spring_sale', 'newsletter', 'retargeting', 'social_media', ''], p=[0.15, 0.15, 0.1, 0.2, 0.4])
        device_type = np.random.choice(['mobile', 'desktop', 'tablet'], p=[0.55, 0.35, 0.1])
        browser = np.random.choice(['Chrome', 'Firefox', 'Safari', 'Edge', 'Opera'], p=[0.6, 0.15, 0.2, 0.04, 0.01])
        city = np.random.choice(['New York', 'London', 'Toronto', 'Mumbai', 'Berlin', 'Tokyo', 'Sydney'])
        is_new_user = np.random.choice([0, 1], p=[0.7, 0.3])
        
        # Add conversion flag at session level
        conversion_potential = np.random.choice([0, 1], p=[0.8, 0.2])
        
        # Generate reasonable number of pages per session (most sessions are short)
        pages_per_session_weights = [0.3, 0.25, 0.15, 0.1, 0.05, 0.05, 0.03, 0.03, 0.02, 0.02]
        max_pages = np.random.choice(range(1, 11), p=pages_per_session_weights)
        
        # Generate sequence of page views for this session
        page_sequence = generate_page_sequence(max_pages=max_pages)
        
        # Basic session start time
        session_start = pd.to_datetime(np.random.randint(
            pd.Timestamp('2023-01-01').value // 10**9,
            pd.Timestamp('2024-12-31').value // 10**9
        ), unit='s')
        
        # Track if checkout page was visited
        checkout_visited = '/checkout' in page_sequence
        
        # Create page view records
        for i, page in enumerate(page_sequence):
            # Calculate timestamp for this page view
            page_time = session_start + pd.Timedelta(seconds=int(np.random.exponential(30) * (i+1)))
            
            # Determine if this is landing or exit page
            is_landing_page = (i == 0)
            is_exit_page = (i == len(page_sequence) - 1)
            
            # Page view duration
            if is_exit_page:
                duration = int(np.random.exponential(30))
            else:
                duration = int(np.random.exponential(60))
            
            # Determine conversion flag
            conversion_flag = 1 if (page == '/checkout' and is_exit_page and conversion_potential) else 0
            
            # Create the page view record
            page_view = {
                'session_id': session_id,
                'user_id': user_id,
                'timestamp': page_time,
                'page_url': page,
                'page_sequence': i + 1,
                'is_landing_page': int(is_landing_page),  # Convert to 0/1 for better compatibility
                'is_exit_page': int(is_exit_page),
                'referrer': referrer if is_landing_page else '',
                'campaign': campaign if is_landing_page else '',
                'duration': duration,
                'conversion_flag': conversion_flag,
                'device_type': device_type,
                'browser': browser,
                'city': city,
                'is_new_user': is_new_user
            }
            
            all_page_views.append(page_view)
            
            # Stop if we've reached the target batch size
            if len(all_page_views) >= pages_to_generate:
                break
    
    # Calculate session durations
    session_durations = {}
    for view in all_page_views:
        sid = view['session_id']
        if sid not in session_durations:
            session_durations[sid] = 0
        session_durations[sid] += view['duration']
    
    # Update all records with session duration
    for view in all_page_views:
        view['session_duration'] = session_durations[view['session_id']]
    
    # Truncate to exactly n records
    final_page_views = all_page_views[:n]
    
    # Create dataframe
    return pd.DataFrame(final_page_views)

if __name__ == "__main__":
    fake = Faker()
    random.seed(42)
    np.random.seed(42)
    
    # Write in chunks
    for i in range(0, num_rows, batch_size):
        batch = generate_batch(batch_size)
        
        # Add option to write to Parquet if needed
        # table = pa.Table.from_pandas(batch)
        filename = os.path.join(datadir, f'web_events_{i//batch_size}.csv')
        # pq.write_table(table, filename)
        batch.to_csv(filename, index=False)
        print(f'Wrote batch {i // batch_size + 1} of {num_rows // batch_size}')