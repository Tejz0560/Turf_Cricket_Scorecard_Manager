import streamlit as st
from stats_engine import calculate_stats


def display_scorecard(match):
    """Display a professional cricket scorecard with team navigation"""
    st.markdown("---")
    st.markdown("<h1 style='text-align: center; color: #1f77b4;'>🏏 Match Scorecard</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Initialize team navigation state
    if "scorecard_team_index" not in st.session_state:
        st.session_state.scorecard_team_index = 0
    
    # Team navigation
    teams = [match["team1"], match["team2"]]
    current_team = teams[st.session_state.scorecard_team_index]
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("⬅️ Previous", disabled=st.session_state.scorecard_team_index == 0):
            st.session_state.scorecard_team_index -= 1
            st.rerun()
    
    with col2:
        st.markdown(f"<h2 style='text-align: center; color: #2e7d32;'>{current_team}</h2>", unsafe_allow_html=True)
    
    with col3:
        if st.button("Next ➡️", disabled=st.session_state.scorecard_team_index == 1):
            st.session_state.scorecard_team_index += 1
            st.rerun()
    
    st.markdown("---")
    
    # Determine if this is first or second innings for the current team
    is_first_innings = (current_team == match["team1"] and match["innings"] >= 1) or (current_team == match["team2"] and match["innings"] == 2)
    is_second_innings = (current_team == match["team2"] and match["innings"] == 2)
    
    if is_first_innings:
        display_team_batting(match, current_team, 1)
        display_team_bowling(match, current_team, 1)
    elif is_second_innings:
        display_team_batting(match, current_team, 2)
        display_team_bowling(match, current_team, 2)
    else:
        st.info(f"{current_team} yet to bat")
    
    st.markdown("---")


def display_team_batting(match, team_name, innings):
    """Display batting scorecard for a specific team and innings"""
    st.markdown(f"<h3 style='color: #2e7d32;'>🏏 {team_name} - {'1st' if innings == 1 else '2nd'} Innings Batting</h3>", unsafe_allow_html=True)
    
    # Get players for this team
    players = match["players1"] if team_name == match["team1"] else match["players2"]
    
    batting_data = []
    
    for player in players:
        # Get stats based on innings
        if innings == 1:
            # First innings stats from batsman_runs
            if player in match["batsman_runs"]:
                bats = match["batsman_runs"][player]
                runs = bats.get("runs", 0)
                balls = bats.get("balls", 0)
                fours = bats.get("fours", 0)
                sixes = bats.get("sixes", 0)
            else:
                runs = balls = fours = sixes = 0
        else:
            # Second innings stats from ball_log
            runs = balls = fours = sixes = 0
            for ball in match["ball_log"]:
                if ball["batsman"] == player and ball.get("innings") == 2:
                    runs += ball["runs"]
                    if not ball.get("extras"):
                        balls += 1
                    if ball["runs"] == 4:
                        fours += 1
                    elif ball["runs"] == 6:
                        sixes += 1
        
        # Only show players who have batted (runs > 0 or balls > 0)
        if runs > 0 or balls > 0:
            # Find dismissal
            dismissal = ""
            is_out = False
            
            for d in match.get("dismissals", []):
                if d["batsman"] == player and d.get("innings") == innings:
                    is_out = True
                    if d["dismissal_type"] == "Caught":
                        dismissal = f"c {d['fielder']} b {d['bowler']}"
                    elif d["dismissal_type"] == "Run Out":
                        dismissal = f"run out ({d['fielder']})"
                    elif d["dismissal_type"] == "Stumped":
                        dismissal = f"st {d['fielder']} b {d['bowler']}"
                    elif d["dismissal_type"] == "Bowled":
                        dismissal = f"b {d['bowler']}"
                    elif d["dismissal_type"] == "LBW":
                        dismissal = f"lbw b {d['bowler']}"
                    else:
                        dismissal = d['dismissal_type'].lower()
                    break
            
            if not is_out:
                dismissal = "not out"
            
            batting_data.append({
                "Batsman": player,
                "Score": f"{runs}({balls})",
                "4s": fours,
                "6s": sixes,
                "Dismissal": dismissal,
                "is_out": is_out
            })
    
    if batting_data:
        # Create DataFrame
        import pandas as pd
        df_batting = pd.DataFrame(batting_data)
        
        # Create display dataframe without is_out column
        df_display = df_batting.drop('is_out', axis=1).reset_index(drop=True)
        
        # Custom styling for not out batsmen (green highlight)
        def highlight_not_out(row):
            idx = row.name
            if idx < len(df_batting) and not df_batting.iloc[idx]['is_out']:
                return ['background-color: #e8f5e8'] * len(row)
            return [''] * len(row)
        
        # Display table with styling
        st.dataframe(
            df_display.style.apply(highlight_not_out, axis=1),
            width='stretch'
        )
    else:
        st.info("No batting data available")


def display_team_bowling(match, team_name, innings):
    """Display bowling scorecard for a specific team and innings"""
    st.markdown(f"<h4 style='color: #f57c00;'>🎳 Bowling Figures</h4>", unsafe_allow_html=True)
    
    # Get bowling team (opposite of batting team)
    bowling_team = match["team2"] if team_name == match["team1"] else match["team1"]
    bowlers = match["players2"] if team_name == match["team1"] else match["players1"]
    
    # Get bowler stats based on innings
    bowler_stats = match.get("bowler_stats_first", match["bowler_stats"]) if innings == 1 else match["bowler_stats"]
    
    bowling_data = []
    for bowler in bowlers:
        if bowler in bowler_stats:
            bowl = bowler_stats[bowler]
            
            # Calculate overs and balls for this bowler
            if innings == 1:
                # For first innings, use match overs/balls as approximation
                overs = match.get("first_innings_overs", match["overs"])
                balls = match.get("first_innings_balls", match["balls"])
            else:
                # For second innings, count from ball_log
                overs = balls = 0
                for ball in match["ball_log"]:
                    if ball["bowler"] == bowler and ball.get("innings") == 2:
                        if not ball.get("extras") or ball.get("extras") not in ["wide", "no_ball"]:
                            balls += 1
                overs = balls // 6
                balls = balls % 6
            
            bowling_data.append({
                "Bowler": bowler,
                "O": f"{overs}.{balls}",
                "M": 0,  # Maidens not tracked
                "R": bowl.get("runs", 0),
                "W": bowl.get("wickets", 0),
                "Econ": f"{bowl.get('runs', 0)/(overs + balls/6):.1f}" if (overs + balls/6) > 0 else "0.0"
            })
    
    if bowling_data:
        import pandas as pd
        df_bowling = pd.DataFrame(bowling_data)
        st.dataframe(df_bowling, width='stretch')
    else:
        st.info("No bowling data available")


def scoring_ui():

    if "match" not in st.session_state:
        st.warning("Start a match first")
        return

    match = st.session_state.match

    if match.get("winner"):
        st.success(f"🏆 {match['winner']} Wins! 🏆")
        st.balloons()
        
        display_scorecard(match)
        
        return  # Stop the match

    # Toggle for extra runs on wide/no ball
    extra_runs_toggle = st.sidebar.checkbox("Extra runs on Wide/No Ball", value=True)

    # Option to increase overs
    if st.sidebar.button("Increase Overs by 1"):
        match["total_overs"] += 1
        st.sidebar.success("Overs increased")

    # Show bar graph button
    if st.sidebar.button("📊 Show Over-by-Over Stats"):
        st.session_state.show_graph = not st.session_state.get("show_graph", False)

    # Show scorecard button
    if st.sidebar.button("📋 Show Scorecard"):
        st.session_state.show_scorecard = not st.session_state.get("show_scorecard", False)

    # Initialize over_runs if not present
    if "over_runs" not in match:
        match["over_runs"] = {}

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Score", match["score"])
    col2.metric("Wickets", match["wickets"])
    col3.metric("Overs", f"{match['overs']}.{match['balls']}")
    col4.metric("Innings", match["innings"])

    st.write(f"Batting: {match['current_batting']} | Bowling: {match['current_bowling']}")
    st.write(f"Striker: {match['striker']} | Non-Striker: {match['non_striker']} | Bowler: {match['bowler']}")

    st.divider()

    # Second Innings Selection Interface
    if match["innings"] == 2 and match["balls"] == 0 and match["overs"] == 0:
        st.markdown("---")
        st.info(f"🎯 **Target: {match['first_innings_score'] + 1} runs**")
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Select Striker")
            striker_options = match["batting_team"]
            new_striker = st.selectbox("Choose Striker", striker_options, key="innings2_striker")
        
        with col2:
            st.subheader("Select Non-Striker")
            non_striker_options = [p for p in match["batting_team"] if p != new_striker]
            new_non_striker = st.selectbox("Choose Non-Striker", non_striker_options, key="innings2_non_striker") if non_striker_options else None
        
        st.subheader("Select Opening Bowler")
        bowler_options = match["bowling_team"]
        new_bowler = st.selectbox("Choose Bowler", bowler_options, key="innings2_bowler")
        
        if st.button("Start Second Innings", key="start_innings2"):
            match["striker"] = new_striker
            match["non_striker"] = new_non_striker
            match["bowler"] = new_bowler
            st.success(f"Second Innings Started! {match['striker']} and {match['non_striker']} to bat. {match['bowler']} to bowl.")
            st.rerun()

    # Wicket pending
    if "wicket_pending" not in st.session_state:
        st.session_state.wicket_pending = False
    if "dismissal_details" not in st.session_state:
        st.session_state.dismissal_details = {}

    def add_ball(run=0, extra=None, wicket=False, new_batsman=None, dismissal_type=None, fielder=None):
        if wicket and new_batsman:
            # Record dismissal details before changing striker
            if dismissal_type:
                dismissal_record = {
                    "batsman": match["striker"],  # The striker got out
                    "bowler": match["bowler"],
                    "dismissal_type": dismissal_type,
                    "fielder": fielder,
                    "innings": match["innings"]
                }
                if "dismissals" not in match:
                    match["dismissals"] = []
                match["dismissals"].append(dismissal_record)
            
            match["striker"] = new_batsman
            st.session_state.wicket_pending = False
            st.session_state.dismissal_details = {}

        ball_no = match["overs"] * 6 + match["balls"] + 1
        over = match["overs"] + 1

        if extra in ["wide", "no_ball"]:
            if extra_runs_toggle:
                match["score"] += 1
            if extra == "wide":
                # Wide doesn't count as a ball even if extra runs enabled
                pass
            else:
                # No ball doesn't count as a ball either
                pass
        else:
            match["score"] += run
            match["balls"] += 1

        if match["balls"] == 6:
            match["overs"] += 1
            match["balls"] = 0
            match["over_details"].append([])

        if wicket:
            match["wickets"] += 1

        # Strike rotation
        if run in [1, 3, 5] or wicket:
            match["striker"], match["non_striker"] = match["non_striker"], match["striker"]

        # Update over details
        if extra:
            if extra == "wide":
                match["over_details"][-1].append("WD")  # WD for wide
            else:
                match["over_details"][-1].append("NB")  # NB for no ball
        elif wicket:
            match["over_details"][-1].append("W")  # W for wicket
        else:
            match["over_details"][-1].append(str(run))

        # Track runs per over
        over_num = match["overs"] + 1
        if over_num not in match["over_runs"]:
            match["over_runs"][over_num] = 0
        if extra:
            if extra_runs_toggle:
                match["over_runs"][over_num] += 1
        else:
            match["over_runs"][over_num] += run

        match["ball_log"].append({
            "batsman": match["striker"],  # Always the striker faced the ball
            "bowler": match["bowler"],
            "runs": run,
            "extras": extra,
            "wicket": wicket,
            "ball_no": ball_no,
            "over": over,
            "innings": match["innings"],
            "dismissal_type": dismissal_type,
            "fielder": fielder
        })

        # Update batsman runs with sixes and fours tracking
        batsman = match["ball_log"][-1]["batsman"]  # Always the striker
        if batsman not in match["batsman_runs"]:
            match["batsman_runs"][batsman] = {"runs": 0, "sixes": 0, "fours": 0, "balls": 0}
        match["batsman_runs"][batsman]["runs"] += run
        if not extra:  # Only count balls faced for non-extras
            match["batsman_runs"][batsman]["balls"] += 1
        if run == 6:
            match["batsman_runs"][batsman]["sixes"] += 1
        elif run == 4:
            match["batsman_runs"][batsman]["fours"] += 1
        
        # Update bowler stats
        bowler = match["bowler"]
        if bowler not in match["bowler_stats"]:
            match["bowler_stats"][bowler] = {"runs": 0, "wickets": 0}
        match["bowler_stats"][bowler]["runs"] += run
        if wicket:
            match["bowler_stats"][bowler]["wickets"] += 1

        # Check if innings over
        if match["overs"] >= match["total_overs"] or match["wickets"] >= 10:
            if match["innings"] == 1:
                match["first_innings_score"] = match["score"]
                match["first_innings_overs"] = match["overs"]
                match["first_innings_balls"] = match["balls"]
                match["wickets_at_end_first"] = match["wickets"]
                match["bowler_stats_first"] = match["bowler_stats"].copy()  # Save first innings bowling
                match["innings"] = 2
                match["current_batting"] = match["team2"]
                match["current_bowling"] = match["team1"]
                match["batting_team"] = match["players2"]
                match["bowling_team"] = match["players1"]
                match["striker"] = match["players2"][0] if match["players2"] else None
                match["non_striker"] = match["players2"][1] if len(match["players2"]) > 1 else None
                match["bowler"] = match["players1"][0] if match["players1"] else None
                match["score"] = 0
                match["wickets"] = 0
                match["overs"] = 0
                match["balls"] = 0
                match["over_details"] = [[]]
                match["batsman_runs"] = {}
                match["bowler_stats"] = {}
                match["over_runs"] = {}
                match["dismissals"] = []
                st.success("Second Innings Started")
            else:
                # Match end
                if match["score"] > match["first_innings_score"]:
                    match["winner"] = match["current_batting"]
                elif match["score"] < match["first_innings_score"]:
                    match["winner"] = match["current_bowling"]
                else:
                    match["winner"] = "Draw"
                st.rerun()  # To show winner

    # Bowler selection per over
    if match["balls"] == 0:
        bowler_options = [p for p in match["bowling_team"]]
        selected_bowler = st.selectbox("Select Bowler for this Over", bowler_options, key=f"bowler_{match['overs']}")
        match["bowler"] = selected_bowler

    # BUTTON GRID
    cols = st.columns(6)
    runs = [0,1,2,3,4,6]
    button_clicked = False
    for i, r in enumerate(runs):
        if cols[i].button(str(r), key=f"run_{r}_{match['ball_no']}" if 'ball_no' in match else f"run_{r}"):
            add_ball(run=r)
            button_clicked = True
    
    if button_clicked:
        st.rerun()

    st.divider()

    col1, col2, col3 = st.columns(3)
    if col1.button("Wicket 🔴", key="wicket_btn"):
        st.session_state.wicket_pending = True
        st.rerun()
    if col2.button("Wide 🔵", key="wide_btn"):
        add_ball(extra="wide")
        st.rerun()
    if col3.button("No Ball 🔵", key="noball_btn"):
        add_ball(extra="no_ball")
        st.rerun()

    # Wicket selection
    if st.session_state.wicket_pending:
        st.markdown("### Wicket Details")
        
        # Dismissal type selection
        dismissal_types = ["Bowled", "Caught", "LBW", "Run Out", "Stumped", "Hit Wicket", "Handled Ball", "Obstructing Field", "Double Hit", "Retired Out"]
        dismissal_type = st.selectbox("How did the batsman get out?", dismissal_types, key="dismissal_type")
        
        # Fielder selection (for catches, run outs, stumpings)
        fielder = None
        if dismissal_type in ["Caught", "Run Out", "Stumped"]:
            all_players = match["players1"] + match["players2"]
            fielder_options = [p for p in all_players if p != match["striker"]]  # Can't catch/run out themselves
            fielder = st.selectbox("Select Fielder", fielder_options, key="fielder")
        
        # New batsman selection
        remaining_players = [p for p in match["batting_team"] if p not in [match["striker"], match["non_striker"]] and p not in [b["batsman"] for b in match["ball_log"] if b.get("wicket")]]
        
        if remaining_players:
            new_batsman = st.selectbox("Select New Batsman", remaining_players, key="new_batsman")
            
            if st.button("Confirm Wicket", key="confirm_wicket"):
                add_ball(wicket=True, new_batsman=new_batsman, dismissal_type=dismissal_type, fielder=fielder)
                st.rerun()
        else:
            st.warning("No more batsmen available")
            if st.button("Confirm Wicket (All Out)", key="confirm_wicket_last"):
                add_ball(wicket=True, dismissal_type=dismissal_type, fielder=fielder)
                st.rerun()

    # Over details in single line
    current_over_balls = " ".join(match["over_details"][-1]) if match["over_details"] else ""
    st.write(f"Current Over: {current_over_balls}")

    st.divider()

    # Display bar graph if toggle is on
    if st.session_state.get("show_graph", False) and match["over_runs"]:
        import plotly.express as px
        import pandas as pd
        
        over_data = pd.DataFrame([
            {"Over": f"Over {over}", "Runs": runs}
            for over, runs in sorted(match["over_runs"].items())
        ])
        
        fig = px.bar(
            over_data, 
            x="Over", 
            y="Runs", 
            title="Runs Scored per Over",
            labels={"Runs": "Runs Scored"},
            color="Runs",
            color_continuous_scale="Viridis"
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.info(f"Total Runs: {sum(match['over_runs'].values())} | Overs Played: {len(match['over_runs'])}")

    st.divider()

    # Batsman and Bowler Cards - Horizontal Layout with real-time updates
    st.markdown("""
    <style>
    .card-container {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
    }
    .card {
        background-color: #f0f2f6;
        padding: 12px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        min-width: 140px;
        font-size: 12px;
        flex: 1;
    }
    .striker-card {
        background-color: #e8f5e8;
        border-left: 4px solid #4caf50;
    }
    .non-striker-card {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
    }
    .bowler-card {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .card-title {
        font-weight: bold;
        margin-bottom: 4px;
        font-size: 11px;
        color: #555;
    }
    .card-text {
        font-size: 11px;
        margin: 2px 0;
    }
    .card-name {
        font-weight: bold;
        font-size: 12px;
        margin: 3px 0;
    }
    </style>
    <div class="card-container">
    """, unsafe_allow_html=True)

    # Get current batsman and bowler stats for display
    striker_data = match["batsman_runs"].get(match["striker"], {"runs": 0, "sixes": 0, "fours": 0, "balls": 0}) if match["striker"] else {}
    non_striker_data = match["batsman_runs"].get(match["non_striker"], {"runs": 0, "sixes": 0, "fours": 0, "balls": 0}) if match["non_striker"] else {}
    bowler_data = match["bowler_stats"].get(match["bowler"], {"runs": 0, "wickets": 0}) if match["bowler"] else {}

    if match["striker"]:
        st.markdown(f'''<div class="card striker-card">
        <div class="card-title">🏏 STRIKER</div>
        <div class="card-name">{match["striker"]}</div>
        <div class="card-text">Runs: <b>{striker_data.get("runs", 0)}</b> ({striker_data.get("balls", 0)} balls)</div>
        <div class="card-text">4s: {striker_data.get("fours", 0)} | 6s: {striker_data.get("sixes", 0)}</div>
        </div>''', unsafe_allow_html=True)

    if match["non_striker"]:
        st.markdown(f'''<div class="card non-striker-card">
        <div class="card-title">⚾ NON-STRIKER</div>
        <div class="card-name">{match["non_striker"]}</div>
        <div class="card-text">Runs: <b>{non_striker_data.get("runs", 0)}</b> ({non_striker_data.get("balls", 0)} balls)</div>
        <div class="card-text">4s: {non_striker_data.get("fours", 0)} | 6s: {non_striker_data.get("sixes", 0)}</div>
        </div>''', unsafe_allow_html=True)

    if match["bowler"]:
        st.markdown(f'''<div class="card bowler-card">
        <div class="card-title">🎳 BOWLER</div>
        <div class="card-name">{match["bowler"]}</div>
        <div class="card-text">Runs: <b>{bowler_data.get("runs", 0)}</b></div>
        <div class="card-text">Wickets: <b>{bowler_data.get("wickets", 0)}</b></div>
        </div>''', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # Display scorecard if toggle is on
    if st.session_state.get("show_scorecard", False):
        display_scorecard(match)

    if st.button("Undo Last Ball"):
        if match["ball_log"]:
            last = match["ball_log"].pop()
            match["score"] -= last["runs"]
            if last["extras"] in ["wide", "no_ball"] and extra_runs_toggle:
                match["score"] -= 1
            if last["wicket"]:
                match["wickets"] -= 1
                # Remove dismissal record
                if "dismissals" in match:
                    match["dismissals"] = [d for d in match["dismissals"] if not (d["batsman"] == last["batsman"] and d["bowler"] == last["bowler"] and d.get("innings") == last.get("innings"))]
                # Restore striker (the batsman who got out becomes striker again)
                match["striker"] = last["batsman"]
            # Revert balls only if it wasn't an extra
            if not last.get("extras"):
                match["balls"] -= 1
                if match["balls"] < 0:
                    match["overs"] -= 1
                    match["balls"] = 5
            # Revert over details
            if match["over_details"] and match["over_details"][-1]:
                match["over_details"][-1].pop()
            # Revert batsman runs
            if last["batsman"] in match["batsman_runs"]:
                match["batsman_runs"][last["batsman"]]["runs"] -= last["runs"]
                if not last.get("extras"):  # Only decrement balls if it wasn't an extra
                    match["batsman_runs"][last["batsman"]]["balls"] -= 1
                if last["runs"] == 6:
                    match["batsman_runs"][last["batsman"]]["sixes"] -= 1
                elif last["runs"] == 4:
                    match["batsman_runs"][last["batsman"]]["fours"] -= 1
            # Revert bowler stats
            if match["bowler"] in match["bowler_stats"]:
                match["bowler_stats"][match["bowler"]]["runs"] -= last["runs"]
                if last["wicket"]:
                    match["bowler_stats"][match["bowler"]]["wickets"] -= 1

    st.divider()
    st.write("Ball Log")
    st.dataframe(match["ball_log"])
