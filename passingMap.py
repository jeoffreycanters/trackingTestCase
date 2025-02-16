import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import mplsoccer
import numpy as np

def createPassingMap(playerNumber, matchNumber, teamA, fileFormat, matchPeriod):
    if(teamA == 'Home'):
        teamB = 'Away'
    elif(teamA == 'Away'):
        teamB = 'Home'
    else:
        raise ValueError("Unsupported team. Use 'Home' or 'Away'.")

    if (fileFormat == 'xlsx'):
        df = pd.read_excel('match_' + str(matchNumber) + '/' + teamA + '.' + fileFormat)
    elif (fileFormat == 'csv'):
        df = pd.read_csv('match_' + str(matchNumber) + '/' + teamA + '.' + fileFormat)
    else:
        raise ValueError("Unsupported file format. Use 'xlsx' or 'csv'.")

    x_col = df[teamA.lower() + '_' + str(playerNumber) + '_x']
    y_col = df[teamA.lower() + '_' + str(playerNumber) + '_y']
    ball_x_col = df['ball_x']
    ball_y_col = df['ball_y']

    df['ball_dx'] = ball_x_col.diff()
    df['ball_dy'] = ball_y_col.diff()

    df['ball_moved'] = np.sqrt(df['ball_dx']**2 + df['ball_dy']**2) < 200
    df['ball_still'] = np.sqrt(df['ball_dx']**2 + df['ball_dy']**2) > 200
    df['player_touched'] = ((x_col - ball_x_col).abs() <= 50) & ((y_col - ball_y_col).abs() <= 50)
    df['player_holds'] = df['player_touched'] & df['ball_still'].shift(1).fillna(False)
    df['player_passes'] = df['player_touched'] & df['ball_moved'].shift(-1).fillna(False)


    teamA_player_columns_x = [col for col in df.columns if col.endswith('_x') and 'ball' not in col and col.startswith(teamA.lower())]
    teamA_player_columns_y = [col for col in df.columns if col.endswith('_y') and 'ball' not in col and col.startswith(teamA.lower())]

    df['completed_pass'] = (
        df[teamA_player_columns_x].sub(df['ball_x'], axis=0).abs() <= 50
    ) & (
        df[teamA_player_columns_y].sub(df['ball_y'], axis=0).abs() <= 50
    ) & (
        df['ball_moved'].shift(1).fillna(False)
    )

    completed_passes = []

    for index, row in df[df['player_passes']].iterrows():
        pass_start_time = row['Time']
        pass_start_x = row['ball_x']
        pass_start_y = row['ball_y']

        receiver_candidates = df[
            (df['Time'] > pass_start_time) &
            (df['Time'] <= pass_start_time + 100)
        ]

        for receiver_index, receiver_row in receiver_candidates.iterrows():
            if receiver_row['completed_pass']:
                pass_end_x = receiver_row['ball_x']
                pass_end_y = receiver_row['ball_y']
                pass_end_time = receiver_row['Time']

                completed_passes.append({
                    'pass_start_time': pass_start_time,
                    'pass_start_x': pass_start_x,
                    'pass_start_y': pass_start_y,
                    'pass_end_time': pass_end_time,
                    'pass_end_x': pass_end_x,
                    'pass_end_y': pass_end_y
                })
