

# translates school names from various other formats into the one used in the CFB API
def translateName(school):
    names = {
        "San Jose State": "San José State",
        "Southern Miss": "Southern Mississippi",
        "Louisiana-Monroe": "Louisiana Monroe",
        "Massachusetts": "UMass",
        "Louisiana-Lafayette": "Louisiana",
        "North Carolina State": "NC State",
        "Southern Methodist": "SMU",
        "Miami (FL)": "Miami",
        "UTSA": "UT San Antonio",
        "Florida Intl.": "Florida International",
        "Brigham Young": "BYU",
        "Hawaii": "Hawai'i"
    }

    if school in names:
        return names[school]
    else:
        return school


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
