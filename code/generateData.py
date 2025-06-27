from faker import Faker
import numpy as np
import os
import pandas as pd
import random
import uuid

# Set constants
num_rows = 10_000  # 100M rows
batch_size = 10_000  # Process 1M rows at a time
datadir = "data"
if not os.path.exists(datadir):
    os.makedirs(datadir)

# Define possible pages and their transition probabilities
pages = ['/home', '/products', '/about', '/contact', '/signup', '/login', '/checkout']

# Page transition matrix (rows=from, columns=to)
transition_matrix = {
    '/home': {'self': 0.1, '/products': 0.5, '/about': 0.05, '/contact': 0.35, '/signup': 0.25, '/login': 0.65, '/checkout': 0, 'exit': 0.1},
    '/products': {'self': 0.1, '/home': 0.5, '/about':0.05, '/contact': 0.35, '/signup': 0.55, '/login': 0.75, '/checkout': 0.45, 'exit': 0.15},
    '/about': {'self': 0.05, '/home': 0.25, '/products': 0.1, '/contact': 0.75, '/signup': 0.15, '/login': 0.15, '/checkout': 0, 'exit': 0.25},
    '/contact': {'self': 0.05, '/home': 0.15, '/products': 0.05, '/about': 0.05, '/signup': 0.05, '/login': 0.05, '/checkout': 0, 'exit': 0.65},
    '/signup': {'self': 0.05, '/home': 0.5, '/products': 0.5, '/about': 0.05, '/contact': 0.05, '/login': 0.05, '/checkout': 0.3, 'exit': 0.4},
    '/login': {'self': 0.05, '/home': 0.1, '/products': 0.5, '/about': 0.05, '/contact': 0.35, '/signup': 0.01, '/checkout': 0.45, 'exit': 0.2},
    '/checkout': {'self': 0.05, '/home': 0.3, '/products': 0.25, '/about': 0.05, '/contact': 0.45, '/signup': 0.35, '/login': 0.05, 'exit': 0.65}
}

# Define page-specific events and their probabilities
page_events = {
    '/products': {
        'product_click': 0.7,
        'add_to_cart': 0.4,
        'remove_from_cart': 0.15,
        'begin_checkout': 0.2,
        'complete_purchase': 0.1,
        'view_cart': 0.3,
        'apply_coupon': 0.15,
        'search_performed': 0.5,
        'logout': 0.05
    },
    '/home': {
        'signup_initiated': 0.25,
        'login_successful': 0.4
    },
    '/signup': {
        'signup_complete': 0.6
    },
    '/contact': {
        'form_submitted': 0.5,
        'contact_inquiry': 0.7
    }
}

# Function to generate events for a specific page
def generate_page_events(page):
    events = []
    if page in page_events:
        for event, probability in page_events[page].items():
            if random.random() < probability:
                events.append(event)
    return events

# Function to generate a sequence of pages for a session based on transition probabilities
def generate_page_sequence(max_pages=10, min_pages=1):
    landing_weights = [0.4, 0.45, 0.15, 0.25, 0.35, 0.5, 0]
    current_page = random.choices(pages, weights=landing_weights)[0]
    
    page_sequence = [current_page]
    
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

def random_probabilities(n):
    probabilities = [random.random() for _ in range(n)]
    total = sum(probabilities)
    return [p / total for p in probabilities]

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
        referrer = np.random.choice(['google.com', 'duckduckgo.com', 'bing.com', 'yahoo.com', 
                                     'brave', 'instagram.com', 'youtube.com', 'facebook.com',
                                     'reddit.com', 'linkedin.com', 'snapchat', 'direct'], p=[0.15, 0.075, 0.075, 0.05, 0.05, 
                                                                                             0.1, 0.05, 0.1, 0.05, 
                                                                                             0.05, 0.1, 0.15])
        campaign = np.random.choice(['spring_sale', 'newsletter', 'retargeting', 'social_media', ''], p=[0.2, 0.2, 0.15, 0.25, 0.2])
        device_type = np.random.choice(['mobile', 'desktop', 'tablet'], p=[0.55, 0.35, 0.1])
        browser = np.random.choice(['Chrome', 'Firefox', 'Safari', 'Edge', 'Opera'], p=[0.6, 0.15, 0.2, 0.04, 0.01])

        states = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", 
                  "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", 
                  "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", 
                  "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", 
                  "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", 
                  "New Hampshire", "New Jersey", "New Mexico", "New York", 
                  "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", 
                  "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", 
                  "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", 
                  "West Virginia", "Wisconsin", "Wyoming"]
        state_rand_p = random_probabilities(len(states))
        state = np.random.choice(states, p=state_rand_p)

        is_new_user = np.random.choice([0, 1], p=[0.7, 0.3])
        
        # Generate reasonable number of pages per session (most sessions are short)
        pages_per_session_weights = [0.3, 0.25, 0.15, 0.1, 0.05, 0.05, 0.03, 0.03, 0.02, 0.02]
        max_pages = np.random.choice(range(1, 11), p=pages_per_session_weights)
        
        # Generate sequence of page views for this session
        page_sequence = generate_page_sequence(max_pages=max_pages)
        
        # Basic session start time
        session_start = pd.to_datetime(np.random.randint(
            pd.Timestamp('2025-05-14').value // 10**9,
            pd.Timestamp('2025-05-15').value // 10**9
        ), unit='s')
        
        # Create page view records
        for i, page in enumerate(page_sequence):
            # Calculate timestamp for this page view
            page_time = session_start + pd.Timedelta(seconds=int(np.random.exponential(30) * (i+1)))
            
            # Determine if this is landing or exit page
            is_landing_page = (i == 0)
            is_exit_page = (i == len(page_sequence) - 1)
            
            # Generate events for this page
            events = generate_page_events(page)
            
            # Create the base page view record
            base_page_view = {
                'session_id': session_id,
                'user_id': user_id,
                'timestamp': page_time,
                'page_url': page,
                'is_landing_page': int(is_landing_page),
                'is_exit_page': int(is_exit_page),
                'referrer': referrer if is_landing_page else '',
                'campaign': campaign if is_landing_page else '',
                'device_type': device_type,
                'browser': browser,
                'state': state,
                'is_new_user': is_new_user,
                'event': ''  # Empty event for the page view itself
            }
            
            # Add the base page view first
            all_page_views.append(base_page_view.copy())
            
            # Create separate records for each event
            for event in events:
                event_view = base_page_view.copy()
                event_view['event'] = event
                # Add a small time increment for each event (1-5 seconds after page view)
                event_view['timestamp'] = page_time + pd.Timedelta(seconds=random.randint(1, 5))
                all_page_views.append(event_view)
            
            # Stop if we've reached the target batch size
            if len(all_page_views) >= pages_to_generate:
                break
    
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