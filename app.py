import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import plotly.express as px
import time

# 1. Setup Page Configuration
st.set_page_config(page_title="Live Sheet Dashboard", layout="wide")
st.title("📊 Real-Time Operations Dashboard")

# Refresh interval (updates every 10 seconds)
REFRESH_INTERVAL = 10 

# 2. Authenticate and Connect to Google Sheets
scope = ["https://google.com", "https://googleapis.com"]

try:
    # Looks for your credentials.json file in the repository
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    # Connected directly to your specific sheet ID
    SHEET_ID = "1kMgv08R3Hmd0f_IV3H-T-jtjQRmcTRdDF8DkpgSTyb8"
    sheet = client.open_by_key(SHEET_ID).sheet1

except Exception as e:
    st.error("Authentication Error: Please check your credentials.json file or Google Sheet access.")
    st.stop()

# 3. Continuous Dashboard Refresh Loop
placeholder = st.empty()

while True:
    with placeholder.container():
        # Fetch fresh data from the Google Sheet rows
        raw_data = sheet.get_all_records()
        df = pd.DataFrame(raw_data)
        
        # Ensure data is present before calculating metrics
        if not df.empty:
            # Layout: Top Row Summary Cards (KPI Metrics)
            kpi1, kpi2, kpi3 = st.columns(3)
            
            with kpi1:
                st.metric(label="📈 Total Logs", value=len(df))
            with kpi2:
                # Assumes you have a 'status' column in your sheet
                active_count = len(df[df['status'].astype(str).str.lower() == 'active']) if 'status' in df.columns else 0
                st.metric(label="🟢 Active Sessions", value=active_count)
            with kpi3:
                st.metric(label="🔄 System Sync Status", value="Healthy")
                
            # Layout: Middle Row Visual Analytics Charts
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                st.subheader("Live Log Feed Activity")
                st.dataframe(df.tail(10), use_container_width=True) # Shows the latest 10 rows
                
            with chart_col2:
                st.subheader("Status Distribution Profile")
                if 'status' in df.columns and not df['status'].empty:
                    fig = px.pie(df, names='status', hole=0.4)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Add a 'status' column to generate visual charts.")
        else:
            st.info("Awaiting live input stream data from Google Sheets source...")
            
    # Pause execution before fetching the next live interval update
    time.sleep(REFRESH_INTERVAL)
