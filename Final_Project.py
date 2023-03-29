"""
Name:       Brian Cardarelli
CS230:      Section 004
Data:       College Football Stadiums
URL:        https://share.streamlit.io/bcards19/cs230_final_project/main/Final_Project.py

This program allows the user to filter college stadiums by selected criteria and view them on maps and charts.
"""

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pydeck as pdk


# Read in Data
def read_data():
    return pd.read_csv('stadums.csv')


# Filter Data
def filter_data(sel_conf, max_cap, yr_built):
    df = read_data()
    df = df.loc[df['conference'].isin(sel_conf)]
    df = df.loc[df['capacity'] > max_cap]
    df = df.loc[df['built'] > yr_built]

    return df


# All Conferences
def all_conferences():
    df = read_data()
    lst = []
    for ind, row in df.iterrows():
        if row['conference'] not in lst:
            lst.append(row['conference'])

    return sorted(lst)


# Count Frequency
def count_conferences(conferences, df):
    return [df.loc[df['conference'].isin([conference])].shape[0] for conference in conferences]


# Pie Chart
def pie_chart(count, sel_conf):
    plt.figure()

    explodes = [0 for i in range(len(count))]
    maximum = count.index(np.max(count))
    explodes[maximum] = 0.05

    plt.pie(count, labels=sel_conf, explode=explodes, autopct="%.2f")
    plt.title(f"Conference Quantity: {', '.join(sel_conf)}")
    return plt


# Stadium Capacities
def stadium_capacity(df):
    capacities = [row['capacity'] for ind, row in df.iterrows()]
    conferences = [row['conference'] for ind, row in df.iterrows()]

    dict = {}
    for conference in conferences:
        dict[conference] = []

    for i in range(len(capacities)):
        dict[conferences[i]].append(capacities[i])

    return dict


# Average Capacity
def capacity_averages(dict_capacities):
    dict = {}
    for key in dict_capacities.keys():
        dict[key] = np.mean(dict_capacities[key])

    return (dict)


# Bar Chart
def bar_chart(dict_avg):
    plt.figure()

    x = dict_avg.keys()
    y = dict_avg.values()
    plt.bar(x, y)
    plt.xticks(rotation=45)
    plt.xlabel("Conference")
    plt.ylabel("Capacity")
    plt.title(f"Average Capacity per Conference: {', '.join(dict_avg.keys())}")

    return plt


# Create a Map
def make_map(df):
    map_df = df.filter(['stadium', 'latitude', 'longitude'])

    view_state = pdk.ViewState(latitude=map_df["latitude"].mean(),
                               longitude=map_df["longitude"].mean(),
                               zoom=3.5)

    layer = pdk.Layer('ScatterplotLayer',
                      data=map_df,
                      get_position='[longitude,latitude]',
                      get_radius=30000,
                      get_color=[100, 200, 500],
                      pickable=True)
    tool_tip = {'html': 'Stadium:<br/> <b>{stadium}</b>', 'style': {'backgroundColor': 'orange', 'color': 'white'}}

    map = pdk.Deck(map_style='mapbox://styles/mapbox/light-v9',
                   initial_view_state=view_state,
                   layers=[layer],
                   tooltip=tool_tip)

    st.pydeck_chart(map)


# Main Function
def main():
    st.title("College Football Stadium Visualization")
    st.write("Welcome to College Football Stadium Database, Open Sidebar to Begin!")
    st.image('ncaa-football-logo.jpg')

    st.sidebar.write("Choose Which Data to Display:")
    conferences = st.sidebar.multiselect("Select a Conference: ", all_conferences())
    min_cap = st.sidebar.slider("Min Capacity: ", 220, 107601)
    year_built = st.sidebar.slider("All Stadiums Built After: ", 1895, 2014)

    data = filter_data(conferences, min_cap, year_built).sort_values(by=['conference'], ascending=True)
    series = count_conferences(conferences, data)

    if data.shape[0] > 1:
        st.write("View a Map of Stadiums")
        make_map(data)

        st.write("Here is a Pie Chart displaying what percentage each selected conference is that meets the criteria: ")
        st.pyplot(pie_chart(series, conferences))

        st.write("Here is a Bar Chart displaying average capacities for each conference: ")
        st.pyplot(bar_chart(capacity_averages(stadium_capacity(data))))


main()
