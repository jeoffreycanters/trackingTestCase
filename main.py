import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import mplsoccer

#pitch 105m by 68m

def createHeateMap(playerNumber, matchPeriod, matchNumber, team, fileFormat):

    if(fileFormat == 'xlsx'):
        df = pd.read_excel('match_' + str(matchNumber) + '/' + team + '.' + fileFormat)
    elif(fileFormat == 'csv'):
        df = pd.read_csv('match_' + str(matchNumber) + '/' + team + '.' + fileFormat)

    df = df[df['IdPeriod'] == matchPeriod]

    customcmap = matplotlib.colors.LinearSegmentedColormap.from_list('custom cmap', ['black', 'red'])

    pitch = mplsoccer.Pitch(pitch_type='impect', pitch_color='black', line_color='white', pitch_length=105, pitch_width=68, axis=True, line_zorder=2)

    fig_width = 10
    fig_height = fig_width*(68/105)

    fig, ax = pitch.draw(figsize=(fig_width, fig_height))
    pitch.kdeplot(df[team.lower() + '_' + str(playerNumber) + '_x']/100, df[team.lower() + '_' + str(playerNumber) + '_y']/100, ax=ax, cmap=customcmap, fill=True, n_levels=100, zorder=1)
    fig.set_facecolor('black')

    plt.show()


createHeateMap(120, 1, 1, 'Home', 'csv')