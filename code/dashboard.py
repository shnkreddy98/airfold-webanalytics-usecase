import streamlit as st
from io import StringIO
import os
from dotenv import load_dotenv
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime, date, timedelta

load_dotenv()

auth_code = os.getenv('auth_code')

def get_data(endpoint, params=''):
    endpoint = endpoint+'.csv'
    full_auth_code = 'Bearer {}'.format(auth_code)

    if params:
        url = 'https://api.us.airfold.co/v1/pipes/{}?{}'
        url = url.format(endpoint, params)
    else:
        url = 'https://api.us.airfold.co/v1/pipes/{}'
        url = url.format(endpoint)
    
    response = requests.get(url, 
                            headers={
                                'Authorization': full_auth_code
                            })

    if response.status_code == 200:
        # data = response.json()
        data = response.text
        return data
    else:
        st.write(response.status_code)
        st.write(response.text)
        st.write("Refresh page to try again")

def display_metrics(name, val):

    st.markdown(
        f"""
        <div style="background-color:#333333; padding:20px; border-radius:8px; margin-bottom:10px;">
            <h4 style="color:white; text-align:center;">{name}</h4>
            <h1 style="color:white; text-align:center; margin:10px 0;">{val}</h1>
       </div>
        """,
        unsafe_allow_html=True
    )
            #  <p style="color:{state['change_color']}; text-align:center; font-size:20px; margin:0;">
            #     # tate['change']}
            # </p>

def format_number(num):
    if num >= 1_000_000:
        if num % 1_000_000 == 0:
            return f'{int(num // 1_000_000)} M'
        return f'{round(num / 1_000_000, 3)} M'
    elif num >= 1_000:
        return f'{round(int(num // 1_000), 3)} K'
    return str(num)

def format_number(num):
    if num >= 1_000_000:
        return f'{round(num / 1_000_000, 1)} M'
    elif num >= 1_000:
        return f'{round(num / 1_000, 1)} K'
    return str(num)

def get_state_codes(df):
    state_codes = {
        'District of Columbia' : 'dc','Mississippi': 'MS', 'Oklahoma': 'OK', 
        'Delaware': 'DE', 'Minnesota': 'MN', 'Illinois': 'IL', 'Arkansas': 'AR', 
        'New Mexico': 'NM', 'Indiana': 'IN', 'Maryland': 'MD', 'Louisiana': 'LA', 
        'Idaho': 'ID', 'Wyoming': 'WY', 'Tennessee': 'TN', 'Arizona': 'AZ', 
        'Iowa': 'IA', 'Michigan': 'MI', 'Kansas': 'KS', 'Utah': 'UT', 
        'Virginia': 'VA', 'Oregon': 'OR', 'Connecticut': 'CT', 'Montana': 'MT', 
        'California': 'CA', 'Massachusetts': 'MA', 'West Virginia': 'WV', 
        'South Carolina': 'SC', 'New Hampshire': 'NH', 'Wisconsin': 'WI',
        'Vermont': 'VT', 'Georgia': 'GA', 'North Dakota': 'ND', 
        'Pennsylvania': 'PA', 'Florida': 'FL', 'Alaska': 'AK', 'Kentucky': 'KY', 
        'Hawaii': 'HI', 'Nebraska': 'NE', 'Missouri': 'MO', 'Ohio': 'OH', 
        'Alabama': 'AL', 'Rhode Island': 'RI', 'South Dakota': 'SD', 
        'Colorado': 'CO', 'New Jersey': 'NJ', 'Washington': 'WA', 
        'North Carolina': 'NC', 'New York': 'NY', 'Texas': 'TX', 
        'Nevada': 'NV', 'Maine': 'ME'}

    df['state_code'] = df['state'].apply(lambda x : state_codes[x])
    return df

def make_choropleth(input_df, input_id, input_column, input_color_theme='blues'):
    choropleth = px.choropleth(input_df, locations=input_id, color=input_column, locationmode="USA-states",
                               color_continuous_scale=input_color_theme,
                            #    range_color=(0, max(df_selected_year.population)),
                               scope="usa",
                               labels={'population':'Population'}
                              )
    choropleth.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )
    return choropleth


if __name__=="__main__":
    st.set_page_config(layout="wide")

    interval = st.selectbox(
        "Time Period",
        ("Today", "Yesterday", "Last 7 Days", 
         "This Month", "YearToDate", "CustomDateRange"),
    )
    
    today = date.today()
    yesterday = today - timedelta(days=1)
    last7 = today - timedelta(days=7)
    current_month = datetime.now().month
    current_year = datetime.now().year
    current_day = datetime.now().day

    if interval=="Today":
        start_date = today
        end_date = today

    elif interval=="Yesterday":
        start_date = yesterday
        end_date = yesterday
    
    elif interval=="Last 7 Days":
        start_date = last7
        end_date = today

    elif interval=="This Month":
        start_date = date(current_year, current_month, 1)
        end_date = today
    
    elif interval=="YearToDate":
        start_date = date(current_year, 1, 1)
        end_date = today
    
    elif interval=="CustomDateRange":
        start_date = st.date_input(label="Custom Date Range",
                        value="2024-01-04",
                        format="YYYY/MM/DD",
                        min_value="2024-01-04",
                        max_value="today")

        end_date = st.date_input(label="Custom Date Range",
                        value=start_date,
                        format="YYYY/MM/DD",
                        min_value=start_date,
                        max_value="today")
    
    params = "{}={}&{}={}"
    metric_params = params.format("start_date", str(start_date),
                           "end_date", str(end_date))
    
    curr_params = params.format("start_date", date(current_year-1, current_month, current_day),
                                "end_date", today)
    prev_params = params.format("start_date", date(current_year-2, current_month, current_day),
                                "end_date", date(current_year-1, current_month, current_day-1))

    views_summary = get_data("views_summary",
                             metric_params)
    views_summary = pd.read_csv(StringIO(views_summary))
    page_views = format_number(views_summary['pageview_count'].values[0])

    visitors_summary = get_data("visitors_summary",
                             metric_params)
    visitors_summary = pd.read_csv(StringIO(visitors_summary))
    visitors = format_number(visitors_summary['visitor_count'].values[0])

    sessions_summary = get_data("sessions_summary",
                             metric_params)
    sessions_summary = pd.read_csv(StringIO(sessions_summary))
    sessions = format_number(sessions_summary['session_count'].values[0])

    duration_summary = get_data("avg_duration",
                                metric_params)
    duration_summary = pd.read_csv(StringIO(duration_summary))
    duration = str(round(duration_summary['duration'].values[0], 2))+" S"

    bounce_summary = get_data("bounce_rate",
                              metric_params)
    bounce_summary = pd.read_csv(StringIO(bounce_summary))
    bounce = str(round(bounce_summary['result'].values[0], 2))+" %"

    conversions_summary = get_data("conversion_rate",
                                   metric_params)
    conversions_summary = pd.read_csv(StringIO(conversions_summary))
    conversion = str(round(conversions_summary['result'].values[0], 2))+" %"

    visitors_data = get_data("visitors_chart",
                            curr_params)
    visitors_data = pd.read_csv(StringIO(visitors_data))
    
    views_data = get_data("views_chart",
                            curr_params)
    views_data = pd.read_csv(StringIO(views_data))

    sessions_data = get_data("sessions_chart",
                            curr_params)
    sessions_data = pd.read_csv(StringIO(sessions_data))

    visitors_by_state = get_data("visitors_by_state",
                                 curr_params)
    visitors_by_state = pd.read_csv(StringIO(visitors_by_state))
    sessions_by_state = get_state_codes(visitors_by_state)

    views_by_state = get_data("views_by_state",
                                 curr_params)
    views_by_state = pd.read_csv(StringIO(views_by_state))
    views_by_state = get_state_codes(views_by_state)

    sessions_by_state = get_data("sessions_by_state",
                                 curr_params)
    sessions_by_state = pd.read_csv(StringIO(sessions_by_state))
    sessions_by_state = get_state_codes(sessions_by_state)


    col1, col2, col3, col4, col5, col6 = st.columns(6)
    # try:
    with col1:
        display_metrics("Page Views", page_views)
    with col2:
        display_metrics("Visitors", visitors)
    with col3:
        display_metrics("Sessions", sessions)
    with col4:
        display_metrics("Session Duration", duration)
    with col5:
        display_metrics("Bounce Rate", bounce)
    with col6:
        display_metrics("Conversion Rate", conversion)
    
    visitors_tab, views_tab, sessions_tab = st.tabs(["Visitors", "Views", "Sessions"])
    
    with visitors_tab:
        st.subheader("Visitors Line Chart")
        st.line_chart(visitors_data, x='date', y='visitors')
        visitors_choropleth = make_choropleth(visitors_by_state, 'state_code', 'total_visitors')
        st.plotly_chart(visitors_choropleth, use_container_width=True)

    with views_tab:
        st.subheader("Views Line Chart")
        st.line_chart(views_data, x='date', y='views')
        views_choropleth = make_choropleth(views_by_state, 'state_code', 'total_pageviews')
        st.plotly_chart(views_choropleth, use_container_width=True)

    with sessions_tab:
        st.subheader("Sessions Line Chart")
        st.line_chart(sessions_data, x='date', y='sessions')
        sessions_choropleth = make_choropleth(sessions_by_state, 'state_code', 'total_sessions')
        st.plotly_chart(sessions_choropleth, use_container_width=True)

    
