import pandas as pd
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import mplsoccer
import numpy as np
from typing import Dict, List, Literal, Tuple
import argparse
import json



# Pitch dimensions: 105m x 68m

def create_heatmap(player_number: int, match_period: int, match_number: int, team: Literal["Home", "Away"], file_format: Literal["csv", "xlsx"]) -> None:
    """Generate and display a heatmap for a player's movement."""
    file_path = f'match_{match_number}/{team}.{file_format}'

    if file_format == 'xlsx':
        df = pd.read_excel(file_path)
    elif file_format == 'csv':
        df = pd.read_csv(file_path)
    else:
        raise ValueError("Unsupported file format. Use 'xlsx' or 'csv'.")

    df = df[df['IdPeriod'] == match_period]

    custom_cmap = matplotlib.colors.LinearSegmentedColormap.from_list('custom_cmap', ['#030F37', '#AFF500'])

    pitch = mplsoccer.Pitch(
        pitch_type='impect', pitch_color='#030F37', line_color='white',
        pitch_length=105, pitch_width=68, axis=True, line_zorder=2
    )

    fig_width = 10
    fig_height = fig_width * (68 / 105)

    fig, ax = pitch.draw(figsize=(fig_width, fig_height))
    pitch.kdeplot(
        df[f'{team.lower()}_{player_number}_x'] / 100,
        df[f'{team.lower()}_{player_number}_y'] / 100,
        ax=ax, cmap=custom_cmap, fill=True, n_levels=100, zorder=1
    )
    fig.set_facecolor('black')

    plt.show()


def calculate_distance_traveled(player_number: int, match_number: int, team: Literal["Home", "Away"], file_format: Literal["csv", "xlsx"]) -> float:
    """Calculate the total distance traveled by a player in kilometers."""
    file_path = f'match_{match_number}/{team}.{file_format}'

    if file_format == 'xlsx':
        df = pd.read_excel(file_path)
    elif file_format == 'csv':
        df = pd.read_csv(file_path)
    else:
        raise ValueError("Unsupported file format. Use 'xlsx' or 'csv'.")

    x_col = df[f'{team.lower()}_{player_number}_x'] / 100
    y_col = df[f'{team.lower()}_{player_number}_y'] / 100

    df['dx'] = x_col.diff()
    df['dy'] = y_col.diff()
    df['step_distance'] = np.sqrt(df['dx'] ** 2 + df['dy'] ** 2)
    total_distance_km = round(df['step_distance'].sum() / 1000, 2)

    return total_distance_km


def calculate_total_touches(player_number: int, match_number: int, team: Literal["Home", "Away"], file_format: Literal["csv", "xlsx"]) -> int:
    """Calculate the total number of touches by a player."""
    file_path = f'match_{match_number}/{team}.{file_format}'

    if file_format == 'xlsx':
        df = pd.read_excel(file_path)
    elif file_format == 'csv':
        df = pd.read_csv(file_path)
    else:
        raise ValueError("Unsupported file format. Use 'xlsx' or 'csv'.")

    df['player_touched'] = (
                                   (df[f'{team.lower()}_{player_number}_x'] - df['ball_x']).abs() <= 5
                           ) & (
                                   (df[f'{team.lower()}_{player_number}_y'] - df['ball_y']).abs() <= 5
                           )

    return int(df['player_touched'].sum())


def calculate_total_shots(team: Literal["Home", "Away"], match_number: int, file_format: Literal["csv", "xlsx"], match_period: int) -> int:
    """Calculate the total number of shots taken by a team."""
    file_path = f'match_{match_number}/{team}.{file_format}'

    if file_format == 'xlsx':
        df = pd.read_excel(file_path)
    elif file_format == 'csv':
        df = pd.read_csv(file_path)
    else:
        raise ValueError("Unsupported file format. Use 'xlsx' or 'csv'.")

    df = df[df['IdPeriod'] == match_period]

    track_shot_x = 5250 if (match_period == 1 and team == "Home") or (match_period == 2 and team == "Away") else -5250
    track_shot_y_range = (-366, 366)

    shot_condition = df['ball_x'] >= track_shot_x if track_shot_x > 0 else df['ball_x'] <= track_shot_x

    df['total_shots'] = shot_condition & df['ball_y'].between(*track_shot_y_range)

    shot_times = df.loc[df['total_shots'], 'Time'].tolist()
    filtered_shot_times = [shot_times[i] for i in range(len(shot_times)) if
                           i == 0 or shot_times[i] != shot_times[i - 1] + 10]

    return len(filtered_shot_times)


def calculate_ball_possession(match_number: int, file_format: Literal["csv", "xlsx"]) -> Dict[str, float]:
    """Calculate ball possession percentage for each team."""
    teams = ['Home', 'Away']
    dfs = {}

    for team in teams:
        file_path = f'match_{match_number}/{team}.{file_format}'
        dfs[team] = pd.read_excel(file_path) if file_format == 'xlsx' else pd.read_csv(file_path)

    df = pd.merge(dfs['Home'], dfs['Away'], on=['Time', 'IdPeriod', 'MatchId', 'ball_x', 'ball_y'])

    player_columns = [col for col in df.columns if '_x' in col and ('home' in col.lower() or 'away' in col.lower())]

    distances = {
        col: np.sqrt((df[col] - df['ball_x']) ** 2 + (df[col.replace('_x', '_y')] - df['ball_y']) ** 2)
        for col in player_columns
    }

    distance_df = pd.DataFrame(distances)

    distance_df.fillna(float("inf"), inplace=True)

    df['closest_player'] = distance_df.idxmin(axis=1)
    df["closest_player"].fillna("", inplace=True)
    df['possession_team'] = df['closest_player'].apply(lambda x: 'Home' if 'home' in x.lower() else 'Away')

    return df['possession_team'].value_counts(normalize=True).mul(100).to_dict()


def create_passing_map(
    player_number: int,
    match_period: int,
    match_number: int,
    team_a: Literal["Home", "Away"],
    file_format: Literal["csv", "xlsx"],
    event_type: Literal["passes", "blocks"]
) -> None:
    """Generates a passing or blocking map for a specific player in a given match."""

    if team_a == "Home":
        team_b = "Away"
    elif team_a == "Away":
        team_b = "Home"
    else:
        raise ValueError("Unsupported team. Use 'Home' or 'Away'.")

    file_path_a = f"match_{match_number}/{team_a}.{file_format}"
    file_path_b = f"match_{match_number}/{team_b}.{file_format}"

    if file_format == "xlsx":
        df_a = pd.read_excel(file_path_a)
        df_b = pd.read_excel(file_path_b)
    elif file_format == "csv":
        df_a = pd.read_csv(file_path_a)
        df_b = pd.read_csv(file_path_b)
    else:
        raise ValueError("Unsupported file format. Use 'xlsx' or 'csv'.")

    df = pd.merge(df_a, df_b, on=["Time", "IdPeriod", "MatchId", "ball_x", "ball_y"])
    df = df[df["IdPeriod"] == match_period]

    player_columns = [
        col for col in df.columns
        if "_x" in col and (team_a.lower() in col.lower() or team_b.lower() in col.lower())
    ]

    team_a_players = list(set(col.split("_")[1] for col in player_columns if team_a.lower() in col.lower()))
    team_b_players = list(set(col.split("_")[1] for col in player_columns if team_b.lower() in col.lower()))

    events: Dict[str, List[Dict[str, Tuple]]] = {"passes": [], "blocks": []}

    distances = {}
    for col in player_columns:
        y_col = col.replace("_x", "_y")
        player_name = col.split("_")[1]
        distance_col = f"distance_{player_name}"
        df[distance_col] = np.sqrt((df[col] - df["ball_x"]) ** 2 + (df[y_col] - df["ball_y"]) ** 2)
        distances[player_name] = distance_col

    df["closest_player"] = df[list(distances.values())].idxmin(axis=1)
    df["closest_player"] = df["closest_player"].str.extract(r"distance_(\d+)")

    df["prev_possessor"] = df["closest_player"].shift(1)

    for idx, row in df.iterrows():
        prev_possessor = row["prev_possessor"]
        current_possessor = row["closest_player"]

        if prev_possessor == str(player_number) and current_possessor != str(player_number):
            event = {
                "time": row["Time"],
                "start_pos": (
                    df.at[idx - 1, f"{team_a.lower()}_{player_number}_x"],
                    df.at[idx - 1, f"{team_a.lower()}_{player_number}_y"],
                ),
                "end_pos": (row["ball_x"], row["ball_y"]),
                "receiver": current_possessor,
            }

            if current_possessor in team_a_players:
                events["passes"].append(event)
            elif current_possessor in team_b_players:
                events["blocks"].append(event)

    # Plot the passing map
    pitch = mplsoccer.Pitch(
        pitch_type="impect",
        pitch_color="#030F37",
        line_color="white",
        pitch_length=105,
        pitch_width=68,
        axis=True
    )

    fig_width = 10
    fig_height = fig_width * (68 / 105)
    fig, ax = pitch.draw(figsize=(fig_width, fig_height))

    arrow_color = "#AFF500" if event_type == "passes" else "red"

    for event in events[event_type]:
        start_x, start_y = event["start_pos"]
        end_x, end_y = event["end_pos"]

        pitch.arrows(
            start_x / 100, start_y / 100, end_x / 100, end_y / 100,
            width=2, headwidth=5, headlength=5, color=arrow_color, ax=ax
        )

    plt.show()


def create_summary_json(player_number, match_period, match_number, team, file_format, event_type):
    summary_data = {}

    summary_data["player_number"] = player_number
    summary_data["match_period"] = match_period
    summary_data["match_number"] = match_number
    summary_data["team"] = team
    summary_data["file_format"] = file_format
    summary_data["event_type"] = event_type

    summary_data["total_distance_km"] = calculate_distance_traveled(player_number, match_number, team, file_format)
    summary_data["total_touches"] = calculate_total_touches(player_number, match_number, team, file_format)
    summary_data["total_shots"] = calculate_total_shots(team, match_number, file_format, match_period)
    summary_data["ball_possession"] = calculate_ball_possession(match_number, file_format)

    with open(f"match_summary_{match_number}.json", "w") as json_file:
        json.dump(summary_data, json_file, indent=4)

    print(f"Summary saved to match_summary_{match_number}.json")

def main(player_number: int, match_period: int, match_number: int, team: Literal["Home", "Away"], file_format: Literal["csv", "xlsx"], event_type: str):
    create_heatmap(player_number, match_period, match_number, team, file_format)
    create_passing_map(player_number, match_period, match_number, team, file_format, event_type)
    create_summary_json(player_number, match_period, match_number, team, file_format, event_type)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze football match data.")
    parser.add_argument("--player", type=int, required=True, help="Player number")
    parser.add_argument("--period", type=int, required=True, help="Match period")
    parser.add_argument("--match", type=int, required=True, help="Match number")
    parser.add_argument("--team", type=str, choices=["Home", "Away"], required=True, help="Team name")
    parser.add_argument("--format", type=str, choices=["csv", "xlsx"], required=True, help="File format")
    parser.add_argument("--type", type=str, choices=["passes", "blocks"], required=True, help="Event type")

    args = parser.parse_args()
    main(args.player, args.period, args.match, args.team, args.format, args.type)
