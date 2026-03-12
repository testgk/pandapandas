"""
Continent to countries mapping — single source of truth for country classification.
Each key is a continent name, each value is the list of known country name variants.
"""
from typing import Dict, List

CONTINENT_COUNTRIES: Dict[ str, List[ str ] ] = {
    "North America": [
        "United States of America", "United States", "USA", "US",
        "Canada",
        "Mexico",
        "Guatemala", "Belize", "Honduras", "El Salvador",
        "Nicaragua", "Costa Rica", "Panama",
        "Cuba", "Jamaica", "Haiti", "Dominican Republic", "Bahamas",
    ],
    "South America": [
        "Brazil", "Argentina", "Chile", "Peru", "Colombia",
        "Venezuela", "Bolivia", "Ecuador", "Uruguay", "Paraguay",
        "Guyana", "Suriname", "French Guiana",
    ],
    "Europe": [
        "Germany", "France", "United Kingdom", "Italy", "Spain",
        "Poland", "Romania", "Netherlands", "Belgium", "Greece",
        "Portugal", "Czech Republic", "Hungary", "Sweden", "Belarus",
        "Austria", "Serbia", "Switzerland", "Bulgaria", "Slovakia",
        "Denmark", "Finland", "Norway", "Ireland",
        "Bosnia and Herzegovina", "Croatia", "Albania",
        "Lithuania", "Slovenia", "Latvia", "Estonia",
        "North Macedonia", "Moldova", "Luxembourg", "Malta",
        "Iceland", "Montenegro", "Cyprus", "Ukraine",
    ],
    "Asia": [
        "China", "India", "Russia", "Russian Federation",
        "Indonesia", "Pakistan", "Bangladesh", "Japan",
        "Philippines", "Vietnam", "Turkey", "Iran",
        "Thailand", "Myanmar", "South Korea", "Iraq",
        "Afghanistan", "Saudi Arabia", "Uzbekistan", "Malaysia",
        "Nepal", "Yemen", "North Korea", "Sri Lanka",
        "Kazakhstan", "Syria", "Cambodia", "Jordan",
        "Azerbaijan", "United Arab Emirates", "Tajikistan",
        "Israel", "Laos", "Singapore", "Oman",
        "Kuwait", "Georgia", "Mongolia", "Armenia",
        "Qatar", "Bahrain", "East Timor", "Maldives",
        "Brunei", "Kyrgyzstan", "Turkmenistan",
    ],
    "Africa": [
        "Nigeria", "Ethiopia", "Egypt", "South Africa",
        "Kenya", "Uganda", "Algeria", "Sudan",
        "Morocco", "Angola", "Ghana", "Mozambique",
        "Madagascar", "Cameroon", "Ivory Coast", "Niger",
        "Burkina Faso", "Mali", "Malawi", "Zambia",
        "Senegal", "Somalia", "Chad", "Zimbabwe",
        "Guinea", "Rwanda", "Benin", "Tunisia",
        "Burundi", "Togo", "Sierra Leone", "Libya",
        "Liberia", "Central African Republic", "Mauritania",
        "Eritrea", "Gambia", "Botswana", "Namibia",
        "Gabon", "Lesotho", "Guinea-Bissau",
        "Equatorial Guinea", "Mauritius", "Eswatini",
        "Djibouti", "Comoros", "Cape Verde",
        "São Tomé and Príncipe", "Seychelles", "Tanzania",
        "Democratic Republic of the Congo", "Republic of the Congo",
    ],
    "Oceania": [
        "Australia", "Papua New Guinea", "New Zealand",
        "Fiji", "Solomon Islands", "Vanuatu",
        "Samoa", "Micronesia", "Tonga",
        "Kiribati", "Palau", "Marshall Islands",
        "Tuvalu", "Nauru",
    ],
}


def buildCountryLookup() -> Dict[ str, str ]:
    """Build a flat country-name → continent lookup from CONTINENT_COUNTRIES."""
    lookup: Dict[ str, str ] = {}
    for continent, countries in CONTINENT_COUNTRIES.items():
        for country in countries:
            lookup[ country ] = continent
    return lookup


# Pre-built lookup for fast O(1) access
COUNTRY_TO_CONTINENT: Dict[ str, str ] = buildCountryLookup()

