import polars as pl
from polars import col
from datetime import date
import streamlit as st
import pandas as pd

# Set the plotting backend to Plotly
pd.options.plotting.backend = "plotly"

def main():
    st.title("PortAventura World - Predicting Ride Wait Times")

    # Load data and process it as before
    attendance = (
        pl.read_csv('data/attendance.csv').filter(col('FACILITY_NAME') == 'PortAventura World')
        .with_columns(col('USAGE_DATE').str.to_datetime("%Y-%m-%d"))
        .select('USAGE_DATE', 'attendance')
    )

    st.header("Attendance Over Time")
    
    # Create interactive plot using Plotly via Pandas with title
    st.plotly_chart(attendance.to_pandas().plot(x='USAGE_DATE', y='attendance'))
    
    # Filter and group data
    filtered_data = attendance.filter(
        (col('USAGE_DATE') <= date(2020, 3, 13)).or_(col('USAGE_DATE') >= date(2021, 6, 19))
    ).groupby(col('USAGE_DATE').dt.weekday()).mean().sort('USAGE_DATE', descending=False)

    st.header("Filtered and Grouped Data")
    
    # Display the grouped data as a DataFrame with title
    st.write("Filtered and Grouped Data:")
    st.write(filtered_data.to_pandas())
    
    # Create a plot for the grouped data with title
    st.plotly_chart(filtered_data.to_pandas().plot(x='USAGE_DATE', y='attendance'))

    # Define the 'link' DataFrame
    link = pl.read_csv('data/link_attraction_park.csv', separator=';')

    # Rest of your code here

if __name__ == "__main__":
    main()
