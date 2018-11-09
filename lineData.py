import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
import util


# replaces weird 1/2 character with .5
def __cleanLines(s):
    if ord(s[-1]) == 189:
        return s[:-1] + ".5"
    else:
        return s


def __removeRanking(s):
    return re.sub(r"\(\d\d?\) ", r"", s)


def getLines(date):
    gameDivClasses = ["_3A-gC _2DWLf _3zKaX", "_3A-gC _2DWLf _3zKaX _1BrlL", "_3A-gC _2DWLf _3zKaX _1BrlL _1Mxxm", "_3A-gC _2DWLf _3zKaX _1Mxxm"]

    page = requests.get("https://www.sportsbookreview.com/betting-odds/college-football/pointspread/?date=" + str(date))
    soup = BeautifulSoup(page.content, "lxml")

    games = []
    for c in gameDivClasses:
        games.extend(soup.find_all("div", class_=c))

    games_df = pd.DataFrame(columns=["away_team", "home_team", "opening_line"])
    for game in games:
        row = {}

        teams_html = game.find_all("span", class_="_1ekCo")
        row["away_team"] = util.translateName(__removeRanking(teams_html[0].get_text()))
        row["home_team"] = util.translateName(__removeRanking(teams_html[1].get_text()))

        openingLines_html = game.find_all("span", class_="_3Nv_7")
        try:
            row["opening_line"] = openingLines_html[1].get_text()
        except IndexError:
            row["opening_line"] = "N/A"
        else:
            row["opening_line"] = __cleanLines(row["opening_line"])

        games_df = games_df.append(row, ignore_index=True)

    return games_df


def test():
    try:
        x = 1/0
    except:
        print("caught the exception")


pd.set_option('display.max_columns', 500)  # prints the df properly in console instead of splitting up columns
pd.set_option('display.width', 1000)

#test()