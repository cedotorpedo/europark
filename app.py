import polars as pl
from polars import col
from datetime import date
import streamlit as st
import pandas as pd

# Set the plotting backend to Plotly
pd.options.plotting.backend = "plotly"

def main():
    st.title("PortAventura World - Predicting Ride Wait Times")

    # Create a sidebar with tabs
    selected_tab = st.sidebar.selectbox("Select a Tab", ["Attendance", "Average Wait Time"])

    if selected_tab == "Attendance":
        show_attendance()
    elif selected_tab == "Average Wait Time":
        show_wait_time()


def show_attendance():
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


def show_wait_time():
    # Rest of your code for Average Wait Time tab
    # Define the 'link' DataFrame
    link = pl.read_csv('data/link_attraction_park.csv', separator=';')

    wait = (
        pl.read_csv('data/waiting_times.csv')
        .join(link, left_on = 'ENTITY_DESCRIPTION_SHORT', right_on = 'ATTRACTION', how='left')
        .filter(col('PARK') == 'PortAventura World')
    )

    wt = (
        wait
        .with_columns(
            col('DEB_TIME').str.to_datetime(),
            col('FIN_TIME').str.to_datetime(),
    )
    )

    top_6_rides = (
        wt
        .group_by(col('ENTITY_DESCRIPTION_SHORT'))
        .agg(col('WAIT_TIME_MAX').mean().suffix('_mean'))
    ).sort('WAIT_TIME_MAX_mean').tail(6)

    top_6_ride_names = [(row[0], row[1]) for row in reversed(top_6_rides.to_numpy())]

    st.header("🎢 Top 6 Rides 🎢")
    st.write("The top 6 rides based on average wait time are:")
    for i, (ride_name, wait_time_mean) in enumerate(top_6_ride_names, start=1):
        minutes = int(wait_time_mean)
        seconds = int((wait_time_mean - minutes) * 60)
        st.write(f"{i}. {ride_name} ({minutes} minutes {seconds} seconds)")
    st.write("\n\n")

    all_rides = (
        wt
        .group_by(col('ENTITY_DESCRIPTION_SHORT'))
        .agg(col('WAIT_TIME_MAX').mean().suffix('_mean'))
    ).sort('WAIT_TIME_MAX_mean').to_numpy()

    ride_names = [row[0] for row in reversed(all_rides)]  # Reverse the list for descending order

    # selected_ride = st.selectbox("Select Ride", ride_names)
    # Increase the font size of the "Select Ride" text
    st.markdown("<h2>Select Ride</h2>", unsafe_allow_html=True)

    # Create the selectbox
    selected_ride = st.selectbox(" ", ride_names)  # Empty space for better alignment


    wt_filtered = (
        wt
        .filter((col('DEB_TIME') <= date(2020, 3, 13)).or_(col('DEB_TIME') >= date(2021, 6, 19)))   # We take out COVID TIME
        .group_by(col('ENTITY_DESCRIPTION_SHORT').alias('RIDE_NAME'), col('DEB_TIME').dt.weekday().alias('weekday'), (col('DEB_TIME').dt.hour() + col('DEB_TIME').dt.minute() / 60).alias('hour_minute'))
        .agg(col('WAIT_TIME_MAX').mean().suffix('_mean'))
        .filter(col('RIDE_NAME').is_in([selected_ride]))
    ).sort(['weekday', 'hour_minute'], descending=[False, False]).to_pandas()

    st.markdown("<h3>Average Wait Time Throughout the Day</h3>", unsafe_allow_html=True)
    
    # Create a plot for the average wait time throughout the day
    st.plotly_chart(
        wt_filtered.plot(
            x='hour_minute',
            y='WAIT_TIME_MAX_mean',
            color='weekday',
            facet_col="RIDE_NAME",
            facet_col_wrap=3,
            title=f'Average wait time (m) at {selected_ride} throughout the day',
            width=800,
            height=400
        )
    )


if __name__ == "__main__":
    main()
