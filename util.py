

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
