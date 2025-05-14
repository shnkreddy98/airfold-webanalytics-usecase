import streamlit as st
import requests
from io import StringIO
import os
from dotenv import load_dotenv
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

load_dotenv()

auth_code = os.getenv('auth_code')

def get_data(endpoint, params=''):
    endpoint = endpoint+'.csv'
    full_auth_code = 'Bearer {}'.format(auth_code)

    if params:
        url = 'https://api.us.airfold.co/v1/pipes/{}?inp_date={}'
        url = url.format(endpoint, str(params))
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
        return [response.status_code, response.text]

def grouped_bar_plot(data, x_cols, y_cols):
    data = [go.Bar(name=y_col, x=data[x_cols], y=data[y_col]) for y_col in y_cols]
    fig = go.Figure(
        data=data) 
    # Change the bar mode
    fig.update_layout(
        barmode='group',
        title='Conversions by Device Type',
        xaxis_title=x_cols,
        yaxis_title=y_cols[0]+'Vs'+y_cols[1]
    )

    return fig

def sankey_diag(data):
    all_pages = list(pd.unique(data[['landing_page', 'exit_page']].values.ravel()))
    page_idx = {page: i for i, page in enumerate(all_pages)}

    source = data['landing_page'].map(page_idx).tolist()
    target = data['exit_page'].map(page_idx).tolist()
    value = data['sessions'].tolist()

    colors = px.colors.qualitative.Set3 * 5
    node_colors = [colors[i] for i in range(len(all_pages))]
    link_colors = [colors[source[i] % len(colors)] for i in range(len(source))]

    node_x = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    node_y = [0.5] * 10

    fig = go.Figure(data=[go.Sankey(
        arrangement="snap",
        node=dict(
            pad=20,
            thickness=20,
            label=all_pages,
            color=node_colors[:len(all_pages)],
            x=node_x,
            y=node_y
        )
,
        link=dict(
            source=source,
            target=target,
            value=value,
            color=link_colors[:len(source)]
        )
    )])

    fig.update_layout(
        title_text="User Flow: Landing → Exit Pages",
        font=dict(size=12, color="white")
    )

    return fig

def donut_bar(data):
    fig = go.Figure(data=[go.Pie(labels=data['exit_page'], 
                                 values=data['sessions'], 
                                 hole=.3,
                                 textinfo='label+percent')])
    return fig
    
if __name__=="__main__":
    st.set_page_config(layout="wide")
    date_param = st.date_input("Date Input",
                           value = "2023-01-01",
                           min_value="2023-01-01",
                           max_value="2023-12-31",
                           format='YYYY/MM/DD')

    col1, col2 = st.columns(2)

    # daily_city_summary
    with col1:
        raw_data = get_data('daily_city_summary', date_param)
        df = pd.read_csv(StringIO(raw_data))
        fig = grouped_bar_plot(df,
                            x_cols='city',
                            y_cols=['no_of_users', 'total_views', 'total_conversions'])
        st.plotly_chart(fig)
    
    # daily_conversion_rate
    with col2:
        raw_data = get_data('daily_metrics', date_param)
        df = pd.read_csv(StringIO(raw_data))
        df = df[['total_users', 'total_new_users']]

        # Title
        st.markdown("<h2 style='color:white;'>Daily Metrics</h2>", unsafe_allow_html=True)

        # Use the first (and only) row
        row = df.iloc[0]

        # Optional: Define friendly names for display
        label_map = {
            'no_users': 'Total Users',
            'no_new_users': 'New Users'
        }

        for col_name, value in row.items():
            display_name = label_map.get(col_name, col_name)
            st.markdown(
                f"""
                <div style="background-color:#333333; padding:20px; border-radius:8px; margin-bottom:10px;">
                    <h4 style="color:white; text-align:center;">{display_name}</h4>
                    <h1 style="color:white; text-align:center; margin:10px 0;">{value}</h1>
                </div>
                """,
                unsafe_allow_html=True
            )


    col3, col4 = st.columns(2)

    # top_converting_campaigns
    with col3:
        raw_data = get_data('top_converting_campaigns')
        df = pd.read_csv(StringIO(raw_data))
        fig = grouped_bar_plot(df, 
                               x_cols='campaign', 
                               y_cols=['conversions', 'users'])
        st.plotly_chart(fig)

    # conversion_by_device
    with col4:
        raw_data = get_data('conversion_by_device')
        df = pd.read_csv(StringIO(raw_data))
        fig = grouped_bar_plot(df, 
                               x_cols='device_type', 
                               y_cols=['views', 'total_conversions'])
        st.plotly_chart(fig)

    # funnel_landing_exit
    raw_data = get_data('funnel_landing_exit')
    df = pd.read_csv(StringIO(raw_data))
    fig = sankey_diag(df)
    st.plotly_chart(fig, use_container_width=True)
    
    col5, col6 = st.columns(2)
    
    # top_exit_pages
    with col5:
        raw_data = get_data('top_exit_pages')
        df = pd.read_csv(StringIO(raw_data))
        fig = donut_bar(df)
        st.plotly_chart(fig)

    # new_vs_returning_users
    with col6:
        raw_data = get_data('new_vs_returning_users')
        df = pd.read_csv(StringIO(raw_data))
        fig = grouped_bar_plot(df,
                               x_cols='is_new',
                               y_cols=['sessions', 'conversions'])
        st.plotly_chart(fig)
    
