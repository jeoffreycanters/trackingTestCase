import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import mplsoccer
import numpy as np

#pitch 105m by 68m

def createHeateMap(playerNumber, matchPeriod, matchNumber, team, fileFormat):
    if(fileFormat == 'xlsx'):
        df = pd.read_excel('match_' + str(matchNumber) + '/' + team + '.' + fileFormat)
    elif(fileFormat == 'csv'):
        df = pd.read_csv('match_' + str(matchNumber) + '/' + team + '.' + fileFormat)
    else:
        raise ValueError("Unsupported file format. Use 'xlsx' or 'csv'.")

    df = df[df['IdPeriod'] == matchPeriod]

    customcmap = matplotlib.colors.LinearSegmentedColormap.from_list('custom cmap', ['#030F37', '#AFF500'])

    pitch = mplsoccer.Pitch(pitch_type='impect', pitch_color='#030F37', line_color='white', pitch_length=105, pitch_width=68, axis=True, line_zorder=2)

    fig_width = 10
    fig_height = fig_width*(68/105)

    fig, ax = pitch.draw(figsize=(fig_width, fig_height))
    pitch.kdeplot(df[team.lower() + '_' + str(playerNumber) + '_x']/100, df[team.lower() + '_' + str(playerNumber) + '_y']/100, ax=ax, cmap=customcmap, fill=True, n_levels=100, zorder=1)
    fig.set_facecolor('black')

    plt.show()

def calcDistanceTraveled(playerNumber, matchNumber, team, fileFormat):
    if (fileFormat == 'xlsx'):
        df = pd.read_excel('match_' + str(matchNumber) + '/' + team + '.' + fileFormat)
    elif (fileFormat == 'csv'):
        df = pd.read_csv('match_' + str(matchNumber) + '/' + team + '.' + fileFormat)
    else:
        raise ValueError("Unsupported file format. Use 'xlsx' or 'csv'.")

    x_col = df[team.lower() + '_' + str(playerNumber) + '_x']/100
    y_col = df[team.lower() + '_' + str(playerNumber) + '_y']/100

    df['dx'] = x_col.diff()
    df['dy'] = y_col.diff()
    df['step_distance'] = np.sqrt(df['dx'] ** 2 + df['dy'] ** 2)
    total_distance = df['step_distance'].sum()
    total_distance_km = round(total_distance/1000)

    return total_distance_km

def calcTotalTouches(playerNumber, matchNumber, team, fileFormat):
    if (fileFormat == 'xlsx'):
        df = pd.read_excel('match_' + str(matchNumber) + '/' + team + '.' + fileFormat)
    elif (fileFormat == 'csv'):
        df = pd.read_csv('match_' + str(matchNumber) + '/' + team + '.' + fileFormat)
    else:
        raise ValueError("Unsupported file format. Use 'xlsx' or 'csv'.")

    x_col = df[team.lower() + '_' + str(playerNumber) + '_x']
    y_col = df[team.lower() + '_' + str(playerNumber) + '_y']
    ball_x_col = df['ball_x']
    ball_y_col = df['ball_y']

    df['player_touched'] = ((x_col - ball_x_col).abs() <= 5) & ((y_col - ball_y_col).abs() <= 5)

    total_touches = df['player_touched'].sum()

    print('Total touches: ' + str(total_touches))

def calcTotalShots(team, matchNumber, fileFormat, matchPeriod):
    if (fileFormat == 'xlsx'):
        df = pd.read_excel('match_' + str(matchNumber) + '/' + team + '.' + fileFormat)
    elif (fileFormat == 'csv'):
        df = pd.read_csv('match_' + str(matchNumber) + '/' + team + '.' + fileFormat)
    else:
        raise ValueError("Unsupported file format. Use 'xlsx' or 'csv'.")

    df = df[df['IdPeriod'] == matchPeriod]

    trackShot_x = 5250 if (matchPeriod == 1 and team == "Home") or (matchPeriod == 2 and team == "Away") else -5250
    trackShot_y_a, trackShot_y_b = -366, 366

    ball_x_col = df['ball_x']
    ball_y_col = df['ball_y']

    if trackShot_x > 0:
        shot_condition = (ball_x_col >= trackShot_x)
    else:
        shot_condition = (ball_x_col <= trackShot_x)

    df['totalShots'] = ((shot_condition) & ((ball_y_col).between(trackShot_y_a, trackShot_y_b)))
    shotTimes = df.loc[df['totalShots'], 'Time'].tolist()
    if shotTimes:
        filteredShotTimes = [shotTimes[0]]
    else:
        filteredShotTimes = []

    for i in range(1, len(shotTimes)):
        if shotTimes[i] != shotTimes[i-1] + 10:
            filteredShotTimes.append(shotTimes[i])

    filteredTotalShots = len(filteredShotTimes)

    print(f"Total shots: {filteredTotalShots}")


#createHeateMap(120, 1, 1, 'Home', 'csv')
#total_distance_km = calcDistanceTraveled(364, 0, 'Away', 'xlsx')
#print(f"Total Distance Traveled: {total_distance_km:.2f} km")
#calcTotalTouches(827, 1, 'Home', 'csv')
#calcTotalShots('Home', 2, 'csv', 1)