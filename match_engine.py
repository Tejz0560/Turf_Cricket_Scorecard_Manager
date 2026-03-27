import streamlit as st
from team_management import load_teams


def setup_match_ui():
    st.header("Match Setup")
    teams = load_teams()

    team1 = st.selectbox("Team 1", list(teams.keys()))
    team2 = st.selectbox("Team 2", list(teams.keys()))

    if team1 == team2:
        st.warning("Select different teams")
        return

    players1 = st.multiselect("Playing XI Team 1", teams[team1])
    players2 = st.multiselect("Playing XI Team 2", teams[team2])

    overs = st.number_input("Overs per Innings", 1, 50, 5)

    # Select striker and non-striker
    if players1:
        striker = st.selectbox("Striker", players1, key="striker_select")
        non_striker_options = [p for p in players1 if p != striker]
        non_striker = st.selectbox("Non-Striker", non_striker_options, key="non_striker_select") if non_striker_options else None
    else:
        striker = None
        non_striker = None

    if players2:
        bowler = st.selectbox("Opening Bowler", players2, key="bowler_select")
    else:
        bowler = None

    if st.button("Start Match"):
        st.session_state.match = {
            "team1": team1,
            "team2": team2,
            "players1": players1,
            "players2": players2,
            "current_batting": team1,
            "current_bowling": team2,
            "batting_team": players1,
            "bowling_team": players2,
            "striker": striker,
            "non_striker": non_striker,
            "bowler": bowler,
            "score": 0,
            "wickets": 0,
            "overs": 0,
            "balls": 0,
            "total_overs": overs,
            "innings": 1,
            "log": [],
            "ball_log": [],
            "batting_stats": {},
            "bowling_stats": {},
            "over_details": [[]],
            "first_innings_score": 0,
            "winner": None,
            "batsman_runs": {},
            "bowler_stats": {},
            "over_runs": {},
            "dismissals": []
        }
        st.session_state.menu = "Live Scoring"
        st.rerun()
