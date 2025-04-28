# system imports
import os
from datetime import date

# 3rd party imports
import streamlit as st
import pandas as pd
from datetime import datetime
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# user imports
from entities import *

st.title("SongSmith")


st.markdown("Welcome")