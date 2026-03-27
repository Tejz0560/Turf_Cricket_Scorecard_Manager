import streamlit as st
from team_management import team_ui
from scoring_ui import scoring_ui
from match_engine import setup_match_ui
from export_utils import export_ui

st.set_page_config(layout="wide")

st.title("🏏 Turf Cricket Scorer")

if "menu" not in st.session_state:
    st.session_state.menu = "Teams"

menu = st.sidebar.radio("Menu", ["Teams", "New Match", "Live Scoring", "Export"], index=["Teams", "New Match", "Live Scoring", "Export"].index(st.session_state.menu))

if menu == "Teams":
    team_ui()
elif menu == "New Match":
    setup_match_ui()
elif menu == "Live Scoring":
    scoring_ui()
elif menu == "Export":
    export_ui()
