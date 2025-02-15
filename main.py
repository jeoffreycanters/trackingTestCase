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

    customcmap = matplotlib.colors.LinearSegmentedColormap.from_list('custom cmap', ['black', 'red'])

    pitch = mplsoccer.Pitch(pitch_type='impect', pitch_color='black', line_color='white', pitch_length=105, pitch_width=68, axis=True, line_zorder=2)

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


#createHeateMap(120, 1, 1, 'Home', 'csv')
total_distance_km = calcDistanceTraveled(364, 0, 'Away', 'xlsx')
print(f"Total Distance Traveled: {total_distance_km:.2f} km")