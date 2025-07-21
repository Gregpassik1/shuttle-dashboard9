
import streamlit as st
import pandas as pd
import numpy as np

st.title("Shuttle Route Optimizer (Normalized Input Format)")

uploaded_file = st.file_uploader("Upload shuttle trip data (normalized format)", type=["csv", "xlsx"])

if uploaded_file:
    # Load based on file extension
    if uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)

    # Basic format check
    required_columns = {'date', 'time_block', 'pickup_location', 'passenger_count'}
    if not required_columns.issubset(df.columns):
        st.error(f"Uploaded file must contain columns: {required_columns}")
    else:
        df['date'] = pd.to_datetime(df['date'])
        df['day_of_week'] = df['date'].dt.day_name()
        df['month'] = df['date'].dt.strftime('%B')

        selected_month = st.selectbox("Select Month", sorted(df['month'].unique()))
        month_df = df[df['month'] == selected_month]

        # Traffic adjustment
        traffic_level = st.selectbox("Traffic Conditions", ["Average", "Moderate", "High"])
        traffic_multiplier = {"Average": 1.0, "Moderate": 1.2, "High": 1.4}[traffic_level]

        # Monthly Avg Passenger Volume by Time Block and Day of Week (Heatmap Format)
        st.subheader("Monthly Avg Passenger Volume by Time Block and Day of Week")
        grouped1 = (month_df.groupby(['time_block', 'day_of_week'])['passenger_count']
                    .mean().unstack(fill_value=0).reindex(columns=[
                        'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'
                    ]))
        st.dataframe(grouped1.style.background_gradient(axis=0))

        # Monthly Avg Passenger Volume by Time Block and Pickup Location
        st.subheader("Monthly Avg Passenger Volume by Time Block and Pickup Location")
        grouped2 = (month_df.groupby(['time_block', 'day_of_week', 'pickup_location'])['passenger_count']
                    .mean().reset_index())
        pivot2 = grouped2.pivot_table(index='time_block',
                                      columns=['day_of_week', 'pickup_location'],
                                      values='passenger_count',
                                      fill_value=0)
        st.dataframe(pivot2)

        # Optimized Shuttle Count
        st.subheader("Optimized Shuttle Count by Time Block and Day of Week")
        capacity = 14
        grouped3 = (month_df.groupby(['time_block', 'day_of_week'])['passenger_count']
                    .sum().unstack(fill_value=0).reindex(columns=[
                        'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'
                    ]))
        shuttles_needed = np.ceil((grouped3 * traffic_multiplier) / capacity).astype(int)
        st.dataframe(shuttles_needed)
else:
    st.info("Awaiting file upload...")
