import streamlit as st
import pandas as pd
import json
import os
from stats_engine import calculate_stats
import plotly.express as px

MATCH_FILE = "data/matches.json"


def export_ui():
    st.header("Export & Analytics Dashboard")

    if "match" not in st.session_state or not st.session_state.match.get("ball_log"):
        st.warning("No match data available")
        return

    match = st.session_state.match
    batting_df, bowling_df, ball_df = calculate_stats(match["ball_log"])

    # Export to Excel
    if st.button("Export Match to Excel"):
        with pd.ExcelWriter("match.xlsx") as writer:
            batting_df.to_excel(writer, sheet_name="Batting", index=False)
            bowling_df.to_excel(writer, sheet_name="Bowling", index=False)
            ball_df.to_excel(writer, sheet_name="BallByBall", index=False)
        st.success("Exported match.xlsx")

    # Dashboard
    st.subheader("Analytics Dashboard")

    # Runs per over
    over_runs = ball_df.groupby('over')['runs'].sum().reset_index()
    fig = px.bar(over_runs, x='over', y='runs', title="Runs per Over")
    st.plotly_chart(fig)

    # Player Leaderboard
    st.subheader("Batting Leaderboard")
    st.dataframe(batting_df.sort_values('Runs', ascending=False))

    st.subheader("Bowling Leaderboard")
    st.dataframe(bowling_df.sort_values('Wickets', ascending=False))

    # Search player stats
    player_search = st.text_input("Search Player Stats")
    if player_search:
        player_batting = batting_df[batting_df['Batsman'].str.contains(player_search, case=False)]
        player_bowling = bowling_df[bowling_df['Bowler'].str.contains(player_search, case=False)]
        if not player_batting.empty:
            st.write("Batting Stats:", player_batting)
        if not player_bowling.empty:
            st.write("Bowling Stats:", player_bowling)

    # Beautiful UI with cards
    st.markdown("""
    <style>
    .card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.metric("Total Score", match["score"])
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.metric("Wickets", match["wickets"])
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.metric("Overs", f"{match['overs']}.{match['balls']}")
        st.markdown('</div>', unsafe_allow_html=True)

    # Mobile-first design note: Streamlit is responsive, but for umpire friendly, perhaps larger buttons, but for now, assume ok.
