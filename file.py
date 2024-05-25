import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import pydeck as pdk
from streamlit_option_menu import option_menu

# page configuration
st.set_page_config(
    page_title="NYC Motor Vehicle Collisions",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS styling
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .sidebar .sidebar-content {
        background-color: #ffffff;
    }
    h1, h2, h3 {
        color: #333333;
    }
    </style>
""", unsafe_allow_html=True)

# sidebar for navigation
with st.sidebar:
    selected = option_menu(
        "Navigation",
        ["Overview", "Injuries Map", "Collisions by Time", "Dangerous Streets", "Raw Data"],
        icons=["house", "map", "clock", "exclamation-triangle", "file-text"],
        menu_icon="cast",
        default_index=0,
    )

# title
st.title("Motor Vehicle Collisions in New York City🚗")

# description
st.markdown("""
            This application is a Streamlit dashboard that can be used to analyse motor vehicle collision in NYC.
            Use the sliders and dropdowns to filter data and visuslise the results.
            """)

DATA_URL = 'https://drive.google.com/uc?export=download&id=1EvaV2rm0DC2glPjRz_kA0MXn2eIGm5y5'

@st.cache_data(persist=True)
def load_data(nrows):
  data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[['CRASH_DATE', 'CRASH_TIME']])
  data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True) #computation
  lowercase = lambda x: str(x).lower()
  data.rename(lowercase, axis='columns', inplace=True)
  data.rename(columns={'crash_date_crash_time': 'date/time'}, inplace=True)
  return data

# load data
data = load_data(100000)
original_data = data

if selected == "Overview":
    st.subheader("This application is a Streamlit dashboard that can be used to analyze motor vehicle collisions in NYC. Navigate to the various sections using the sidebar. Use the sliders and dropdowns to filter data and visualise the results.")
    
    # summary statistics
    st.header("Summary Statistics")
    st.write(data.describe())
    
    # sample of the data
    st.header("Sample Data")
    st.write(data.head())
    
    # map of all collisions
    st.header("Map of All Collisions")
    st.map(data[['latitude', 'longitude']].dropna(how='any'))

# Section: Injuries
elif selected == "Injuries Map":
   st.header('Where are the most people injured in New York City?')
   injured_people = st.slider('Number of people injured in vehicle collisions', 0, 19, step=1)
   filtered_data = data.query("injured_persons >= @injured_people")[['latitude', 'longitude']].dropna(how='any')
   
   st.map(filtered_data)


# Section: Collisions by Time of Day
elif selected == "Collisions by Time":
   st.header('How many collisions occur during a given time of the day?')
   hour = st.selectbox('Hour to look at', range(0,24),1)
   hourly_data = data[data['date/time'].dt.hour == hour]
   
   st.markdown('Vehicle collisions between %i:00 and %i:00' % (hour, (hour + 1) % 24))
   
   midpoint = (np.average(hourly_data['latitude']), np.average(hourly_data['longitude']))
   
   st.pydeck_chart(pdk.Deck(
      map_style= "mapbox://styles/mapbox/light-v9",
      initial_view_state={
        'latitude': midpoint[0],
        'longitude': midpoint[1],
        'zoom': 11,
        'pitch':50,
      },
      layers= [
         pdk.Layer(
              "HexagonLayer",
              data = hourly_data[['date/time', 'latitude', 'longitude']],
              get_position=['longitude', 'latitude'],
              radius=100,
              extruded = True,
              pickable = True,
              elevation_scale=4,
              elevation_range=[0,1000]
            ),
      ],
    ))
   
   st.subheader('Breakdown by minutes between %i:00 and %i:00' % (hour, (hour+1) %24))
   filtered = hourly_data [(hourly_data['date/time'].dt.hour == hour) & (data['date/time'].dt.hour < (hour+1))]
   hist = np.histogram(filtered['date/time'].dt.minute, bins=60, range=(0,60))[0]
   chart_data = pd.DataFrame({'minute': range(60), 'crashes': hist})
   
   fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height=400)
   fig.update_layout(
      title='Collisions by Minute',
      xaxis_title='Minute of the Hour',
      yaxis_title='Number of Collisions',
      template='plotly_white'
   )
   st.write(fig)

 # Section: Dangerous Streets
elif selected == "Dangerous Streets":
   st.header('Top 10 Dangerous Streets by Affected Type')
   select = st.selectbox('Affected type of people', ['Pedestrians', 'Cyclists', 'Motorists'])
   if select == "Pedestrians":
      top_streets = original_data.query("injured_pedestrians >= 1")[['on_street_name', 'injured_pedestrians']].sort_values(by=['injured_pedestrians'], ascending=False).dropna(how='any')[:10]
   elif select == 'Cyclists':
      top_streets = original_data.query("injured_cyclists >= 1")[['on_street_name', 'injured_cyclists']].sort_values(by=['injured_cyclists'], ascending=False).dropna(how='any')[:10]
   else:
     top_streets = original_data.query("injured_motorists >= 1")[['on_street_name', 'injured_motorists']].sort_values(by=['injured_motorists'], ascending=False).dropna(how='any')[:10]
    
   st.write(top_streets)

# Section to show the Raw Data
elif selected == "Raw Data":
    st.subheader('Raw Data')
    st.write(data)
