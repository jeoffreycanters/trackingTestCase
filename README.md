# trackingTestCase
This program performs soccer data analysis based on match data files (either .csv or .xlsx). It calculates various metrics related to a player's performance and the team's overall performance, including distance traveled, total touches, shots, ball possession, and passing maps.

# How to use
To use the program, ensure that you have match data in either CSV or Excel format with player and ball position columns. Then, open a terminal and navigate to the folder containing the script. Run the program with the following command:

```python main.py --player <player_number> --period <match_period> --match <match_number> --team <Home/Away> --format <csv/xlsx> --type <passes/blocks>```

Replace the placeholders with the appropriate values for the player number, match period, match number, team (Home or Away), file format (CSV or Excel), and event type (passes or blocks). The program will generate a heatmap of the player's movement, a passing/blocking map, and save a match summary in a JSON file (e.g., match_summary_<match_number>.json). The JSON file contains the total distance traveled, total touches, total shots, and ball possession percentages for both teams.

