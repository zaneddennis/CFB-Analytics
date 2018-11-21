
schoolNames = {
        "Brigham Young": "BYU",
        "Central Florida": "UCF",
        "Florida Intl.": "Florida International",
        "Hawaii": "Hawai'i",
        "Louisiana-Monroe": "Louisiana Monroe",
        "Louisiana-Lafayette": "Louisiana",
        "Massachusetts": "UMass",
        "Miami (FL)": "Miami",
        "Miami-FL": "Miami",
        "Miami-OH": "Miami (OH)",
        "North Carolina State": "NC State",
        "San Jose State": "San José State",
        "Southern Methodist": "SMU",
        "Southern Miss": "Southern Mississippi",
        "UL-Lafayette": "Louisiana",
        "UL-Monroe": "Louisiana Monroe",
        "UTSA": "UT San Antonio",
    }

# translates school names from various other formats into the one used in the CFB API
def translateName(school):
    if school in schoolNames:
        return schoolNames[school]
    else:
        return school

# like translateName, but for a pd Series
def translateNames(schools):
    result = []
    for s in schools:
        if s in schoolNames:
            result.append(schoolNames[s])
        else:
            result.append(s)
    return result


# assumes 1.00 unit stake
# american odds format
# pct should be 0 <= x <= 1
def expectedValue(odds, pct):
    odds = int(odds)
    winProfit = ""

    if odds > 0:
        winProfit = odds * 0.01

    elif odds < 0:
        winProfit = 100 / abs(odds)

    else:
        assert False

    return (winProfit * pct) - (1 - pct)
