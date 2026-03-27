import json
import os
import streamlit as st

TEAM_FILE = "data/teams.json"

def load_teams():
    if not os.path.exists(TEAM_FILE):
        return {}
    try:
        return json.load(open(TEAM_FILE))
    except json.JSONDecodeError:
        return {}

def save_teams(data):
    json.dump(data, open(TEAM_FILE, "w"), indent=2)

def team_ui():
    st.header("Team Management")
    teams = load_teams()

    new_team = st.text_input("Team Name")
    if st.button("Create Team") and new_team:
        teams[new_team] = []
        save_teams(teams)
        st.success("Team Created")

    team_selected = st.selectbox("Select Team", list(teams.keys()))

    if team_selected:
        player = st.text_input("Add Player")
        if st.button("Add Player"):
            teams[team_selected].append(player)
            save_teams(teams)

        st.write("Players:", teams[team_selected])
