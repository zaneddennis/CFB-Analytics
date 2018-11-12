import pandas as pd
import numpy as np
from random import randint, choices
from sklearn.linear_model import LinearRegression


def __adjust(df, teams_df):
    for index, row in df.iterrows():
        df.at[index, "off_oppAdj"] = df.at[index, "PRE"] - teams_df.at[row["defense"], "def_aPPD"]
        df.at[index, "def_oppAdj"] = df.at[index, "PRE"] - teams_df.at[row["offense"], "off_aPPD"]

    teams_df["off_Last"] = teams_df["off_aPPD"].copy()
    teams_df["def_Last"] = teams_df["def_aPPD"].copy()
    teams_df[["off_aPPD"]] = df.groupby(by="offense").agg(["mean"])["off_oppAdj"]
    teams_df[["def_aPPD"]] = df.groupby(by="defense").agg(["mean"])["def_oppAdj"]

    return df, teams_df


def __getDirection(df, i, r):
    if (r["start_yardline"] + r["yards"] == r["end_yardline"]) and (r["yards"] != 0):
        return {r["offense"] : "positive", r["defense"] : "negative"}
    elif r["start_yardline"] - r["yards"] == r["end_yardline"] and (r["yards"] != 0):
        return {r["defense"] : "positive", r["offense"] : "negative"}
    else:
        if randint(0,1):
            if df.at[i+1, "game_id"] == r["game_id"]:
                return __getDirection(df, i+1, df.loc[i+1])
            elif df.at[i-1, "game_id"] == r["game_id"]:
                return __getDirection(df, i-1, df.loc[i-1])
        else:
            if df.at[i-1, "game_id"] == r["game_id"]:
                return __getDirection(df, i-1, df.loc[i-1])
            elif df.at[i+1, "game_id"] == r["game_id"]:
                return __getDirection(df, i+1, df.loc[i+1])


def __calcPoints(dr):
    if dr == "TD":
        return 7
    elif dr == "FG":
        return 3
    elif dr == "INT TD":
        return -7
    elif dr == "FUMBLE TD":
        return -7
    elif dr == "PUNT TD":
        return -7
    elif dr == "SF":
        return -2
    elif dr == "FUMBLE RETURN TD":
        return -7
    elif dr == "PUNT RETURN TD":
        return -7
    elif dr == "MISSED FG TD":
        return -7
    else:
        return 0


def __cleanDriveData(dirty, season, weekThrough, includeGarbage=True):
    clean = dirty[(dirty.offense_conference.notnull()) & (dirty.defense_conference.notnull())]

    games = pd.read_json("https://api.collegefootballdata.com/games?year=" + str(season))
    games = games[["id", "week"]]
    games.columns = ["game_id", "week"]

    clean = pd.merge(clean, games, how="left", on="game_id")

    clean = clean.sort_values(by=["game_id", "start_period"])
    clean = clean[["offense", "defense", "week", "game_id", "id", "start_period", "plays", "start_yardline", "yards", "end_yardline", "drive_result"]]

    # fix bad data
    clean = clean[clean.game_id != 401013346]  # Ohio State vs Tulane 2018
    clean = clean[clean.game_id != 400869533]  # Tulsa SMU 2016
    clean = clean[clean.id != 4010128564]  # completely wrong drive in Indiana vs Iowa
    clean = clean[clean.id != 40094526122]  # weirdly catalogued OT drive in Hawaii vs Wyoming
    clean.loc[clean.id == 40093456823, "drive_result"] = "END OF 4TH QUARTER"
    clean.loc[clean.id == 4008696135, "drive_result"] = "INT TD"
    clean.loc[clean.id == 40086912120, "drive_result"] = "FUMBLE TD"

    clean = clean[clean.week <= weekThrough]

    possibleResults = ["TD", "FG", "PUNT", "DOWNS", "INT", "FUMBLE", "END OF HALF", "END OF GAME", "MISSED FG", "INT TD", "FUMBLE TD", "PUNT TD", "SF", "FUMBLE RETURN TD", "PUNT RETURN TD", "MISSED FG TD", "Uncategorized", "KICKOFF",
                       "END OF 4TH QUARTER"]
    # data exploration
    r_df = clean
    for r in possibleResults:
        r_df = r_df[r_df.drive_result != r]
    if len(r_df) != 0:
        print(r_df)
        assert False

    clean = clean[(clean.drive_result != "Uncategorized") & (clean.drive_result != "END OF HALF") & (clean.drive_result != "END OF GAME") & (clean.drive_result != "KICKOFF") & (clean.drive_result != "END of 4TH QUARTER")]
    clean = clean.copy()

    if not includeGarbage:
        clean["isGarbage"] = 0

        plays = {}
        for w in range(1, weekThrough+1):
            plays[w] = pd.read_json("https://api.collegefootballdata.com/plays?year=" + str(season) + "&week=" + str(w))

        for index, row in clean.iterrows():
            if row["start_period"] == 4:
                weekPlays = plays[row["week"]]

                offScore = weekPlays.loc[weekPlays.drive_id == row["id"], "offense_score"].iat[0]
                defScore = weekPlays.loc[weekPlays.drive_id == row["id"], "defense_score"].iat[0]

                if abs(offScore - defScore) >= 21:
                    clean.at[index, "isGarbage"] = 1

        clean = clean[clean.isGarbage != 1]
        clean = clean.drop(columns=["isGarbage"])

    return clean.reset_index(drop=True)


def calculateAll(season, weekThrough, store=False):
    df = pd.read_json("https://api.collegefootballdata.com/drives?year=" + str(season))
    df = __cleanDriveData(df, season, weekThrough, includeGarbage=False)

    df["points"] = 0
    for index, row in df.iterrows():
        df.at[index, "points"] = __calcPoints(row["drive_result"])
    df = df.reset_index(drop=True)

    df["start_distance"] = -1
    for index, row in df.iterrows():
        directions = __getDirection(df, index, row)
        if directions[row["offense"]] == "positive":
            df.at[index, "start_distance"] = 100 - row["start_yardline"]
        elif directions[row["offense"]] == "negative":
            df.at[index, "start_distance"] = row["start_yardline"]
        else:
            print("error in direction finder")
            assert(False)

    df = df[df.plays > 0]
    df = df.reset_index(drop=True)

    grouped_df = df.groupby("start_distance").agg(["count", "mean"])["points"]
    grouped_df = grouped_df.reset_index()
    grouped_df.index = grouped_df.index + 1
    grouped_df.columns = ["start_distance", "driveCount", "meanPPD"]
    grouped_df = grouped_df[grouped_df.driveCount >= 10]

    X = np.array(grouped_df["start_distance"]).reshape(-1, 1)
    y = np.array(grouped_df["meanPPD"]).reshape(-1, 1)
    weights = np.array(grouped_df["driveCount"])

    df = df[["offense", "defense", "game_id", "start_distance", "points"]].copy()
    reg = LinearRegression().fit(X, y, sample_weight=weights)
    df["expectedPoints"] = reg.predict(np.array(df["start_distance"]).reshape(-1, 1))
    df["PRE"] = df["points"] - df["expectedPoints"]

    teams_df = df.groupby(by=["offense"]).agg(["mean"])["PRE"]
    teams_df.columns = ["OPRE"]
    teams_df.index.name = "team"

    defenses = df.groupby(by=["defense"]).agg(["mean"])["PRE"]
    defenses.columns = ["DPRE"]
    defenses.index.name = "team"

    teams_df = pd.merge(teams_df, defenses, how="inner", left_index=True, right_index=True)

    df["off_oppAdj"] = 0.0
    df["def_oppAdj"] = 0.0

    for index, row in df.iterrows():
        df.at[index, "off_oppAdj"] = df.at[index, "PRE"] - teams_df.at[row["defense"], "DPRE"]
        df.at[index, "def_oppAdj"] = df.at[index, "PRE"] - teams_df.at[row["offense"], "OPRE"]

    teams_df[["off_aPPD"]] = df.groupby(by="offense").agg(["mean"])["off_oppAdj"]
    teams_df[["def_aPPD"]] = df.groupby(by="defense").agg(["mean"])["def_oppAdj"]

    teams_df["off_Last"] = 0
    teams_df["def_Last"] = 0

    t1, t2, t3 = choices(teams_df.index, k=3)
    print("\t" + t1 + "\t" + t2 + "\t" + t3)
    for i in range(int(200 / weekThrough)):
        df, teams_df = __adjust(df, teams_df)
        print(i, teams_df.at[t1, "off_aPPD"], teams_df.at[t2, "def_aPPD"], teams_df.at[t3, "off_aPPD"])

    teams_df["off_aPPD"] = (teams_df["off_aPPD"] + teams_df["off_Last"]) / 2
    teams_df["net_aPPD"] = teams_df["off_aPPD"] - teams_df["def_aPPD"]
    teams_df = teams_df[["off_aPPD", "def_aPPD", "net_aPPD"]]
    teams_df = teams_df.round(2)

    if store:
        teams_df.to_csv("Data/teams_aPPD_w" + str(weekThrough) + "_" + str(season) + ".tsv", sep="\t")

    return teams_df.copy()


"""def predictGame(away, home, season, weekThrough, hfa=False):
    drives_df = pd.read_json("https://api.collegefootballdata.com/drives?year=" + str(season))
    drives_df = __cleanDriveData(drives_df, season, weekThrough)

    teams_df = pd.read_csv("Data/teams_aPPD_w" + str(weekThrough) + ".tsv", sep="\t", index_col="team")

    pace = drives_df.groupby(["offense", "game_id"]).count()
    pace = pd.DataFrame(pace.reset_index().groupby("offense").mean()["defense"])
    pace.columns = ["pace"]
    pace.index = pace.index.rename("team")

    teams_df = pd.merge(teams_df, pace, left_index=True, right_index=True)
    gamePace = (teams_df.at[away, "pace"] + teams_df.at[home, "pace"]) / 2.0
    result = (teams_df.at[away, "net_aPPD"] - teams_df.at[home, "net_aPPD"]) * gamePace

    return result"""


# games is a tuple of (away_team, home_team) columns
# returns a column
def predictGames(games, season, weekThrough, hfa=False):
    aways = games[0]
    homes = games[1]
    assert(len(aways) == len(homes))

    drives_df = pd.read_json("https://api.collegefootballdata.com/drives?year=" + str(season))
    drives_df = __cleanDriveData(drives_df, season, weekThrough, includeGarbage=True)

    teams_df = pd.read_csv("Data/teams_aPPD_w" + str(weekThrough) + "_" + str(season) + ".tsv", sep="\t", index_col="team")

    pace = drives_df.groupby(["offense", "game_id"]).count()
    pace = pd.DataFrame(pace.reset_index().groupby("offense").mean()["defense"])
    pace.columns = ["pace"]
    pace.index = pace.index.rename("team")

    teams_df = pd.merge(teams_df, pace, left_index=True, right_index=True)

    predictions = []
    for i in range(len(aways)):
        try:
            gamePace = (teams_df.at[aways.iat[i], "pace"] + teams_df.at[homes.iat[i], "pace"]) / 2.0
            result = (teams_df.at[aways.iat[i], "net_aPPD"] - teams_df.at[homes.iat[i], "net_aPPD"]) * gamePace
            predictions.append(result)
        except KeyError:
            predictions.append(-999)

    return predictions


pd.set_option('display.max_columns', 500)  # prints the df properly in console instead of splitting up columns
pd.set_option('display.width', 1000)

# calculateAll(2016, 7, store=True)
