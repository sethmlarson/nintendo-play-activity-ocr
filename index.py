import json
import re
import subprocess
import sqlite3
from pathlib import Path

curdir = Path(__file__).absolute().parent
proc = subprocess.run(
    [
        "sudo",
        "docker",
        "run",
        "--rm",
        "--net",
        "none",
        "-v",
        f"{curdir / 'images'}:/images",
        "nintendo-play-activity-ocr",
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
if proc.returncode != 0:
    print(proc.stderr.decode())
    exit(proc.returncode)

results = []
for line in proc.stdout.split(b"\n"):
    try:  # Skip invalid JSON lines.
        results.append(json.loads(line.decode().strip()))
    except ValueError:
        print("Bad line: ", line.decode())
        continue

games = {
    # List of potential games in Play Activity.
    "Kirby Air Riders": None,
    "Mario Kart World": None,
    "Mario Kart 8 Deluxe": None,
    "Super Mario Party": None,
    "Mario Party Superstars": None,
    "Super Mario Odyssey": None,
    "Super Mario RPG": None,
    "Paper Mario: The Thousand": "Paper Mario: The Thousand-Year Door",
    "Wonder": "Super Mario Bros. Wonder",
    "Smash Bros. Ultimate": None,
    "Sonic Origins": None,
    "Pikmin 1": None,
    "Pikmin 2": None,
    "Pikmin 3 Deluxe": None,
    "Pikmin 4": None,
    "Overcooked! 2": None,
    "Animal Crossing: New Horizons": None,
}

processed = set()
play_time_durations: dict[tuple[int, int, int, str], int] = {}
for line in results:
    result = line["result"]
    processed.add(line["id"])

    # Split the text into chunks to identify
    # the game name and play times and dates.
    left = result.index("Play Activity")
    result = result[left + 1 :]
    try:
        right_fp = result.index("First played")
    except ValueError:
        right_fp = len(result)
    try:
        right_pa = result.index("Play Activity")
    except ValueError:
        right_pa = len(result)
    if right_pa == right_fp == len(result):
        right_fp = 1
    right = min([right_fp, right_pa])
    name_candidates = " ".join(result[:right]).lower()
    for name, name_alias in games.items():
        if name.lower() in name_candidates:
            game_name = name_alias or name
            break
    else:
        raise RuntimeError(f"Unknown game name: {repr(name_candidates)}")

    play_activity = " ".join(result[right:])
    matches = re.findall(
        r"([1-9][0-9]?/[1-9][0-9]?/2[0-9]{3}) (A few min|(?:([0-9]+)\s*hr[:;,. ]+)?([0-9]+)\s*min)",
        play_activity,
    )
    for date, a_few_min, hours, minutes in matches:
        month, day, year = map(int, date.split("/", 3))
        if "A few min" in a_few_min:
            seconds = 300  # ~5 minutes
        else:
            seconds = (int(hours or 0) * 60 + int(minutes or 0)) * 60
        play_time_durations[(year, month, day, game_name)] = seconds

db_schema = """
CREATE TABLE IF NOT EXISTS sessions (
  id INTEGER PRIMARY KEY,
  game_system STRING,
  game_name STRING,
  date STRING,
  duration INTEGER
);
"""
db = sqlite3.connect("nintendo-play-activity.sqlite")
db.execute(db_schema)
db.commit()

for (year, month, day, game_name), duration in play_time_durations.items():
    db.execute(
        "INSERT INTO sessions (game_system, game_name, date, duration) VALUES (?, ?, ?, ?)",
        ("Switch", game_name, f"{year}-{month:0>2}-{day:0>2}", duration),
    )
db.commit()

# Update the list of processed files.
meta_filepath = curdir / "images/meta.json"
meta = json.loads(meta_filepath.read_text())
meta["processed"] = sorted(set(meta["processed"]) | processed)
meta_filepath.write_text(json.dumps(meta))
