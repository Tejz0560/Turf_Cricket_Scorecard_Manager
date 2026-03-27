import pandas as pd


def calculate_stats(ball_log):
    if not ball_log:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    df = pd.DataFrame(ball_log)

    # Ball by ball
    ball_df = df.copy()

    # Batting stats
    batting_df = df.groupby('batsman').agg({
        'runs': 'sum',
        'wicket': 'sum'
    }).reset_index()
    batting_df.columns = ['Batsman', 'Runs', 'Dismissals']

    # Bowling stats
    bowling_df = df.groupby('bowler').agg({
        'runs': 'sum',
        'wicket': 'sum'
    }).reset_index()
    bowling_df.columns = ['Bowler', 'Runs Conceded', 'Wickets']

    return batting_df, bowling_df, ball_df