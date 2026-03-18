"""
GeoChallenge Game Module - Interactive Geography Game
Showcases advanced GeoPandas and Pandas capabilities for professional demonstration

Features:
- Geographic location guessing game
- Spatial distance calculations
- Statistical performance analysis
- Dynamic difficulty adjustment
- Real-time scoring system
"""

import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point
from datetime import datetime, timedelta
import random
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class DifficultyLevel(Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"
    EXPERT = "Expert"

@dataclass
class GameChallenge:
    """Represents a single game challenge"""
    location_name: str
    actual_coordinates: Tuple[float, float]  # (lat, lon)
    country: str
    continent: str
    difficulty: DifficultyLevel
    hints: List[str]
    max_distance_km: float  # Maximum reasonable distance for full points

@dataclass
class PlayerAttempt:
    """Represents a player's attempt at a challenge"""
    challenge_id: str
    clicked_coordinates: Tuple[float, float]  # (lat, lon)
    distance_km: float
    accuracy_score: int  # 0-100 percentage score
    response_time_seconds: float
    timestamp: datetime

class GeoChallengeGame:
    """
    Advanced Geography Challenge Game using GeoPandas and Pandas
    
    Demonstrates professional-level usage of:
    - Spatial data analysis with GeoPandas
    - Statistical analysis with Pandas
    - Performance tracking and analytics
    - Dynamic difficulty adjustment
    """
    
    def __init__(self, world_data_manager):
        self.world_data_manager = world_data_manager
        self.challenges_database = self._load_challenges_database()
        self.player_history = pd.DataFrame(columns=[
            'challenge_id', 'location_name', 'difficulty', 'distance_km', 
            'accuracy_score', 'response_time', 'timestamp'
        ])
        self.current_challenge = None
        self.challenge_start_time = None
        self.game_statistics = self._initialize_statistics()
        
    def _load_challenges_database(self) -> pd.DataFrame:
        """Load and create geographic challenges database using GeoPandas"""
        print("🗄️ Loading geographic challenges database...")
        
        # Create comprehensive challenges database
        challenges_data = []
        
        # Major world cities with varying difficulty - EXPANDED DATABASE (100+ cities)
        cities_easy = [
            # Major World Capitals & Famous Cities
            ("New York", (40.7128, -74.0060), "United States", "North America", ["Largest city in USA", "Big Apple", "Statue of Liberty"]),
            ("London", (51.5074, -0.1278), "United Kingdom", "Europe", ["Big Ben", "Thames River", "Capital of UK"]),
            ("Paris", (48.8566, 2.3522), "France", "Europe", ["Eiffel Tower", "City of Light", "Capital of France"]),
            ("Tokyo", (35.6762, 139.6503), "Japan", "Asia", ["Capital of Japan", "Mount Fuji nearby", "Largest metro area"]),
            ("Sydney", (-33.8688, 151.2093), "Australia", "Oceania", ["Opera House", "Harbor Bridge", "Largest city in Australia"]),
            ("Berlin", (52.5200, 13.4050), "Germany", "Europe", ["Brandenburg Gate", "Capital of Germany", "Berlin Wall"]),
            ("Rome", (41.9028, 12.4964), "Italy", "Europe", ["Colosseum", "Vatican", "Eternal City"]),
            ("Madrid", (40.4168, -3.7038), "Spain", "Europe", ["Prado Museum", "Capital of Spain", "Royal Palace"]),
            ("Moscow", (55.7558, 37.6176), "Russia", "Europe", ["Red Square", "Kremlin", "Capital of Russia"]),
            ("Beijing", (39.9042, 116.4074), "China", "Asia", ["Forbidden City", "Great Wall nearby", "Capital of China"]),
            ("Los Angeles", (34.0522, -118.2437), "United States", "North America", ["Hollywood", "Beverly Hills", "City of Angels"]),
            ("Chicago", (41.8781, -87.6298), "United States", "North America", ["Windy City", "Sears Tower", "Great Lakes"]),
            ("Toronto", (43.6532, -79.3832), "Canada", "North America", ["CN Tower", "Largest city in Canada", "Great Lakes"]),
            ("Mexico City", (19.4326, -99.1332), "Mexico", "North America", ["Largest city in Mexico", "Aztec heritage", "High altitude"]),
            ("São Paulo", (-23.5505, -46.6333), "Brazil", "South America", ["Largest city in Brazil", "Economic center", "Carnival"]),
            ("Buenos Aires", (-34.6118, -58.3960), "Argentina", "South America", ["Tango", "Capital of Argentina", "Paris of South America"]),
            ("Cairo", (30.0444, 31.2357), "Egypt", "Africa", ["Pyramids nearby", "Nile River", "Capital of Egypt"]),
            ("Lagos", (6.5244, 3.3792), "Nigeria", "Africa", ["Largest city in Africa", "Economic hub", "Atlantic coast"]),
            ("Mumbai", (19.0760, 72.8777), "India", "Asia", ["Bollywood", "Gateway of India", "Financial capital"]),
            ("Delhi", (28.7041, 77.1025), "India", "Asia", ["Red Fort", "Capital of India", "Ancient and modern"]),
            ("Bangkok", (13.7563, 100.5018), "Thailand", "Asia", ["Capital of Thailand", "Buddhist temples", "Street food"]),
            ("Singapore", (1.3521, 103.8198), "Singapore", "Asia", ["City-state", "Marina Bay", "Garden City"]),
            ("Hong Kong", (22.3193, 114.1694), "Hong Kong", "Asia", ["Victoria Harbor", "Skyscrapers", "Special Administrative Region"]),
            ("Dubai", (25.2048, 55.2708), "UAE", "Asia", ["Burj Khalifa", "Desert city", "Modern architecture"]),
            ("Tel Aviv", (32.0853, 34.7818), "Israel", "Asia", ["Mediterranean coast", "Tech hub", "Modern Israel"]),
        ]
        
        cities_medium = [
            # Regional Capitals & Important Cities
            ("Rio de Janeiro", (-22.9068, -43.1729), "Brazil", "South America", ["Christ the Redeemer", "Copacabana Beach", "Former capital"]),
            ("Istanbul", (41.0082, 28.9784), "Turkey", "Europe/Asia", ["Bosphorus Bridge", "Between two continents", "Former Constantinople"]),
            ("Cape Town", (-33.9249, 18.4241), "South Africa", "Africa", ["Table Mountain", "Cape of Good Hope", "Legislative capital"]),
            ("Barcelona", (41.3851, 2.1734), "Spain", "Europe", ["Sagrada Familia", "Mediterranean coast", "Gaudi architecture"]),
            ("Amsterdam", (52.3676, 4.9041), "Netherlands", "Europe", ["Canals", "Tulips", "Capital of Netherlands"]),
            ("Vienna", (48.2082, 16.3738), "Austria", "Europe", ["Classical music", "Danube River", "Imperial palaces"]),
            ("Prague", (50.0755, 14.4378), "Czech Republic", "Europe", ["Charles Bridge", "Golden City", "Medieval architecture"]),
            ("Budapest", (47.4979, 19.0402), "Hungary", "Europe", ["Danube River", "Thermal baths", "Parliament building"]),
            ("Warsaw", (52.2297, 21.0122), "Poland", "Europe", ["Capital of Poland", "Old Town", "Vistula River"]),
            ("Stockholm", (59.3293, 18.0686), "Sweden", "Europe", ["Capital of Sweden", "14 islands", "Nobel Prize"]),
            ("Helsinki", (60.1699, 24.9384), "Finland", "Europe", ["Capital of Finland", "Baltic Sea", "Northern lights"]),
            ("Oslo", (59.9139, 10.7522), "Norway", "Europe", ["Capital of Norway", "Fjords nearby", "Viking heritage"]),
            ("Copenhagen", (55.6761, 12.5683), "Denmark", "Europe", ["Little Mermaid", "Tivoli Gardens", "Hygge culture"]),
            ("Dublin", (53.3498, -6.2603), "Ireland", "Europe", ["Trinity College", "Guinness", "Emerald Isle"]),
            ("Edinburgh", (55.9533, -3.1883), "Scotland", "Europe", ["Castle", "Royal Mile", "Bagpipes"]),
            ("Zurich", (47.3769, 8.5417), "Switzerland", "Europe", ["Financial center", "Alps nearby", "Lake Zurich"]),
            ("Brussels", (50.8503, 4.3517), "Belgium", "Europe", ["EU headquarters", "Chocolate", "Grand Place"]),
            ("Lisbon", (38.7223, -9.1393), "Portugal", "Europe", ["Atlantic coast", "Age of exploration", "Fado music"]),
            ("Athens", (37.9838, 23.7275), "Greece", "Europe", ["Acropolis", "Parthenon", "Birthplace of democracy"]),
            ("Bucharest", (44.4268, 26.1025), "Romania", "Europe", ["Little Paris", "Dracula country", "Eastern Europe"]),
            ("Kiev", (50.4501, 30.5234), "Ukraine", "Europe", ["Capital of Ukraine", "Golden domes", "Dnieper River"]),
            ("Manila", (14.5995, 120.9842), "Philippines", "Asia", ["Capital of Philippines", "7000 islands", "Jeepneys"]),
            ("Jakarta", (-6.2088, 106.8456), "Indonesia", "Asia", ["Capital of Indonesia", "Largest archipelago", "Spice islands"]),
            ("Kuala Lumpur", (3.1390, 101.6869), "Malaysia", "Asia", ["Petronas Towers", "Twin towers", "Multicultural"]),
            ("Seoul", (37.5665, 126.9780), "South Korea", "Asia", ["K-pop", "Technology hub", "Divided Korea"]),
            ("Pyongyang", (39.0392, 125.7625), "North Korea", "Asia", ["Capital of North Korea", "Hermit kingdom", "Divided Korea"]),
            ("Hanoi", (21.0285, 105.8542), "Vietnam", "Asia", ["Capital of Vietnam", "French colonial", "Motorbikes"]),
            ("Phnom Penh", (11.5564, 104.9282), "Cambodia", "Asia", ["Capital of Cambodia", "Angkor Wat nearby", "Mekong River"]),
            ("Yangon", (16.8661, 96.1951), "Myanmar", "Asia", ["Former capital of Myanmar", "Golden pagodas", "Shwedagon Pagoda"]),
            ("Colombo", (6.9271, 79.8612), "Sri Lanka", "Asia", ["Largest city in Sri Lanka", "Island nation", "Tea plantations"]),
            ("Dhaka", (23.8103, 90.4125), "Bangladesh", "Asia", ["Capital of Bangladesh", "Bengal tigers", "Ganges delta"]),
            ("Kathmandu", (27.7172, 85.3240), "Nepal", "Asia", ["Capital of Nepal", "Himalayas", "Mount Everest base"]),
            ("Thimphu", (27.4728, 89.6390), "Bhutan", "Asia", ["Capital of Bhutan", "Happiness index", "Buddhist kingdom"]),
            ("Kabul", (34.5553, 69.2075), "Afghanistan", "Asia", ["Capital of Afghanistan", "Hindu Kush mountains", "Silk road"]),
            ("Islamabad", (33.6844, 73.0479), "Pakistan", "Asia", ["Capital of Pakistan", "Planned city", "Margalla Hills"]),
            ("Nairobi", (1.2921, 36.8219), "Kenya", "Africa", ["Capital of Kenya", "Safari hub", "Great Rift Valley"]),
            ("Addis Ababa", (9.1450, 40.4897), "Ethiopia", "Africa", ["Capital of Ethiopia", "African Union", "Highland city"]),
            ("Khartoum", (15.5007, 32.5599), "Sudan", "Africa", ["Capital of Sudan", "Blue and White Nile", "Desert city"]),
            ("Accra", (5.6037, -0.1870), "Ghana", "Africa", ["Capital of Ghana", "Gold Coast", "Atlantic Ocean"]),
            ("Dakar", (14.7167, -17.4677), "Senegal", "Africa", ["Capital of Senegal", "Westernmost Africa", "Paris-Dakar rally"]),
            ("Casablanca", (33.5731, -7.5898), "Morocco", "Africa", ["Largest city in Morocco", "Atlantic coast", "Hassan II Mosque"]),
            ("Tunis", (36.8065, 10.1815), "Tunisia", "Africa", ["Capital of Tunisia", "Mediterranean", "Carthage ruins"]),
            ("Algiers", (36.7538, 3.0588), "Algeria", "Africa", ["Capital of Algeria", "Mediterranean", "Casbah"]),
            ("Tripoli", (32.8872, 13.1913), "Libya", "Africa", ["Capital of Libya", "Mediterranean", "Sahara edge"]),
        ]
        
        cities_hard = [
            # Lesser Known Capitals & Regional Cities
            ("Ulaanbaatar", (47.8864, 106.9057), "Mongolia", "Asia", ["Capital of Mongolia", "Coldest capital", "Genghis Khan"]),
            ("Reykjavik", (64.1466, -21.9426), "Iceland", "Europe", ["Northernmost capital", "Geysers", "Northern Lights"]),
            ("Antananarivo", (-18.8792, 47.5079), "Madagascar", "Africa", ["Capital of Madagascar", "Island nation", "Lemurs"]),
            ("Vientiane", (17.9757, 102.6331), "Laos", "Asia", ["Capital of Laos", "Mekong River", "Buddhist temples"]),
            ("Port Vila", (-17.7333, 168.3273), "Vanuatu", "Oceania", ["Capital of Vanuatu", "Pacific islands", "Volcanoes"]),
            ("Tashkent", (41.2995, 69.2401), "Uzbekistan", "Asia", ["Capital of Uzbekistan", "Silk Road", "Central Asia"]),
            ("Almaty", (43.2220, 76.8512), "Kazakhstan", "Asia", ["Former capital of Kazakhstan", "Mountains nearby", "Apples origin"]),
            ("Bishkek", (42.8746, 74.5698), "Kyrgyzstan", "Asia", ["Capital of Kyrgyzstan", "Tien Shan mountains", "Nomadic culture"]),
            ("Dushanbe", (38.5598, 68.7870), "Tajikistan", "Asia", ["Capital of Tajikistan", "Pamir mountains", "Persian culture"]),
            ("Ashgabat", (37.9601, 58.3261), "Turkmenistan", "Asia", ["Capital of Turkmenistan", "Marble city", "Natural gas"]),
            ("Yerevan", (40.1792, 44.4991), "Armenia", "Asia", ["Capital of Armenia", "Mount Ararat view", "Ancient civilization"]),
            ("Tbilisi", (41.7151, 44.8271), "Georgia", "Asia", ["Capital of Georgia", "Caucasus mountains", "Wine country"]),
            ("Baku", (40.4093, 49.8671), "Azerbaijan", "Asia", ["Capital of Azerbaijan", "Caspian Sea", "Oil city"]),
            ("Minsk", (53.9045, 27.5615), "Belarus", "Europe", ["Capital of Belarus", "Last dictatorship", "Soviet architecture"]),
            ("Chisinau", (47.0105, 28.8638), "Moldova", "Europe", ["Capital of Moldova", "Wine cellars", "Eastern Europe"]),
            ("Vilnius", (54.6872, 25.2797), "Lithuania", "Europe", ["Capital of Lithuania", "Baltic state", "Medieval old town"]),
            ("Riga", (56.9496, 24.1052), "Latvia", "Europe", ["Capital of Latvia", "Art nouveau", "Baltic Sea"]),
            ("Tallinn", (59.4370, 24.7536), "Estonia", "Europe", ["Capital of Estonia", "Digital nomads", "Medieval walls"]),
            ("Ljubljana", (46.0569, 14.5058), "Slovenia", "Europe", ["Capital of Slovenia", "Lake Bled nearby", "Green capital"]),
            ("Zagreb", (45.8150, 15.9819), "Croatia", "Europe", ["Capital of Croatia", "Adriatic Sea nearby", "Balkan country"]),
            ("Sarajevo", (43.8486, 18.3564), "Bosnia and Herzegovina", "Europe", ["Capital of Bosnia", "1984 Olympics", "Siege history"]),
            ("Skopje", (41.9973, 21.4280), "North Macedonia", "Europe", ["Capital of North Macedonia", "Alexander the Great", "Balkan crossroads"]),
            ("Podgorica", (42.4304, 19.2594), "Montenegro", "Europe", ["Capital of Montenegro", "Black mountains", "Adriatic coast"]),
            ("Pristina", (42.6629, 21.1655), "Kosovo", "Europe", ["Capital of Kosovo", "Newest European state", "Balkan region"]),
            ("Tirana", (41.3275, 19.8187), "Albania", "Europe", ["Capital of Albania", "Adriatic and Ionian seas", "Mountain country"]),
            ("Windhoek", (-22.5597, 17.0832), "Namibia", "Africa", ["Capital of Namibia", "Kalahari Desert", "German colonial"]),
            ("Gaborone", (-24.6282, 25.9231), "Botswana", "Africa", ["Capital of Botswana", "Okavango Delta", "Diamonds"]),
            ("Maseru", (-29.3167, 27.4833), "Lesotho", "Africa", ["Capital of Lesotho", "Mountain kingdom", "Enclave in South Africa"]),
            ("Mbabane", (-26.3054, 31.1367), "Eswatini", "Africa", ["Capital of Eswatini", "Former Swaziland", "Landlocked kingdom"]),
            ("Maputo", (-25.9692, 32.5732), "Mozambique", "Africa", ["Capital of Mozambique", "Indian Ocean", "Portuguese colonial"]),
            ("Lusaka", (-15.3875, 28.3228), "Zambia", "Africa", ["Capital of Zambia", "Victoria Falls nearby", "Copper mining"]),
            ("Harare", (-17.8252, 31.0335), "Zimbabwe", "Africa", ["Capital of Zimbabwe", "Victoria Falls nearby", "Great Zimbabwe ruins"]),
        ]
        
        cities_expert = [
            # Very Obscure Capitals & Remote Cities
            ("Nuuk", (64.1836, -51.7214), "Greenland", "North America", ["Capital of Greenland", "Arctic Circle", "Icebergs"]),
            ("Funafuti", (-8.5167, 179.2167), "Tuvalu", "Oceania", ["Capital of Tuvalu", "Smallest country", "Rising sea levels"]),
            ("Majuro", (7.1315, 171.1845), "Marshall Islands", "Oceania", ["Capital of Marshall Islands", "Coral atolls", "Pacific"]),
            ("Ngerulmud", (7.5006, 134.6242), "Palau", "Oceania", ["Capital of Palau", "Rock Islands", "Diving paradise"]),
            ("Avarua", (-21.2078, -159.7750), "Cook Islands", "Oceania", ["Capital of Cook Islands", "Polynesia", "Lagoons"]),
            ("Nuku'alofa", (-21.1395, -175.2018), "Tonga", "Oceania", ["Capital of Tonga", "Kingdom in Pacific", "Coral islands"]),
            ("Apia", (-13.8506, -171.7513), "Samoa", "Oceania", ["Capital of Samoa", "Polynesian culture", "Robert Louis Stevenson"]),
            ("Suva", (-18.1248, 178.4501), "Fiji", "Oceania", ["Capital of Fiji", "Coral coast", "Bula"]),
            ("Port Moresby", (-9.4438, 147.1803), "Papua New Guinea", "Oceania", ["Capital of Papua New Guinea", "Bird of paradise", "Tribal cultures"]),
            ("Honiara", (-9.4280, 159.9497), "Solomon Islands", "Oceania", ["Capital of Solomon Islands", "WWII battles", "Coral reefs"]),
            ("Port-au-Prince", (18.5944, -72.3074), "Haiti", "North America", ["Capital of Haiti", "Caribbean", "Earthquake zone"]),
            ("Nassau", (25.0443, -77.3504), "Bahamas", "North America", ["Capital of Bahamas", "Caribbean paradise", "Pink sand beaches"]),
            ("Bridgetown", (13.1939, -59.5432), "Barbados", "North America", ["Capital of Barbados", "Rum birthplace", "Cricket"]),
            ("Port of Spain", (10.6918, -61.2225), "Trinidad and Tobago", "North America", ["Capital of Trinidad", "Carnival", "Oil and gas"]),
            ("Georgetown", (6.8013, -58.1551), "Guyana", "South America", ["Capital of Guyana", "Only English-speaking South American country", "Kaieteur Falls"]),
            ("Paramaribo", (5.8520, -55.2038), "Suriname", "South America", ["Capital of Suriname", "Dutch colonial", "Amazon rainforest"]),
            ("Cayenne", (4.9375, -52.3260), "French Guiana", "South America", ["Capital of French Guiana", "Space center", "French territory"]),
            ("Malé", (4.1755, 73.5093), "Maldives", "Asia", ["Capital of Maldives", "Lowest country", "Coral atolls"]),
            ("Bandar Seri Begawan", (4.9031, 114.9398), "Brunei", "Asia", ["Capital of Brunei", "Oil sultanate", "Southeast Asia"]),
            ("Dili", (-8.5569, 125.5603), "East Timor", "Asia", ["Capital of East Timor", "Newest Asian nation", "Portuguese colonial"]),
            ("Moroni", (-11.7172, 43.2473), "Comoros", "Africa", ["Capital of Comoros", "Volcanic islands", "Ylang-ylang perfume"]),
            ("Victoria", (-4.6199, 55.4513), "Seychelles", "Africa", ["Capital of Seychelles", "Granite islands", "Coco de mer"]),
            ("Port Louis", (-20.1619, 57.5012), "Mauritius", "Africa", ["Capital of Mauritius", "Dodo bird extinct", "Sugar and tourism"]),
            ("Praia", (14.9177, -23.5092), "Cape Verde", "Africa", ["Capital of Cape Verde", "Atlantic islands", "Creole culture"]),
            ("São Tomé", (0.3365, 6.7273), "São Tomé and Príncipe", "Africa", ["Capital of São Tomé", "Equatorial islands", "Cocoa plantations"]),
            ("Malabo", (3.7558, 8.7892), "Equatorial Guinea", "Africa", ["Capital of Equatorial Guinea", "Oil rich", "Spanish speaking Africa"]),
            ("Libreville", (0.4162, 9.4673), "Gabon", "Africa", ["Capital of Gabon", "Equatorial rainforest", "Oil wealth"]),
            ("N'Djamena", (12.1348, 15.0557), "Chad", "Africa", ["Capital of Chad", "Lake Chad", "Sahel region"]),
            ("Bangui", (4.3947, 18.5582), "Central African Republic", "Africa", ["Capital of CAR", "Geographic center of Africa", "Diamonds"]),
            ("Banjul", (13.4549, -16.5790), "Gambia", "Africa", ["Capital of Gambia", "Smallest African mainland country", "River Gambia"]),
            ("Bissau", (11.8811, -15.6178), "Guinea-Bissau", "Africa", ["Capital of Guinea-Bissau", "Portuguese colonial", "Cashew nuts"]),
            ("Conakry", (9.6412, -13.5784), "Guinea", "Africa", ["Capital of Guinea", "Bauxite mining", "West Africa"]),
            ("Freetown", (8.4657, -13.2317), "Sierra Leone", "Africa", ["Capital of Sierra Leone", "Freed slaves", "Blood diamonds"]),
            ("Monrovia", (6.2907, -10.7605), "Liberia", "Africa", ["Capital of Liberia", "American colony", "Never colonized"]),
        ]
        
        cities_expert = [
            # Very Obscure Capitals & Remote Cities
            ("Nuuk", (64.1836, -51.7214), "Greenland", "North America", ["Capital of Greenland", "Arctic Circle", "Icebergs"]),
            ("Funafuti", (-8.5167, 179.2167), "Tuvalu", "Oceania", ["Capital of Tuvalu", "Smallest country", "Rising sea levels"]),
            ("Majuro", (7.1315, 171.1845), "Marshall Islands", "Oceania", ["Capital of Marshall Islands", "Coral atolls", "Pacific"]),
            ("Ngerulmud", (7.5006, 134.6242), "Palau", "Oceania", ["Capital of Palau", "Rock Islands", "Diving paradise"]),
            ("Avarua", (-21.2078, -159.7750), "Cook Islands", "Oceania", ["Capital of Cook Islands", "Polynesia", "Lagoons"]),
            ("Nuku'alofa", (-21.1395, -175.2018), "Tonga", "Oceania", ["Capital of Tonga", "Kingdom in Pacific", "Coral islands"]),
            ("Apia", (-13.8506, -171.7513), "Samoa", "Oceania", ["Capital of Samoa", "Polynesian culture", "Robert Louis Stevenson"]),
            ("Suva", (-18.1248, 178.4501), "Fiji", "Oceania", ["Capital of Fiji", "Coral coast", "Bula"]),
            ("Port Moresby", (-9.4438, 147.1803), "Papua New Guinea", "Oceania", ["Capital of Papua New Guinea", "Bird of paradise", "Tribal cultures"]),
            ("Honiara", (-9.4280, 159.9497), "Solomon Islands", "Oceania", ["Capital of Solomon Islands", "WWII battles", "Coral reefs"]),
            ("Port-au-Prince", (18.5944, -72.3074), "Haiti", "North America", ["Capital of Haiti", "Caribbean", "Earthquake zone"]),
            ("Nassau", (25.0443, -77.3504), "Bahamas", "North America", ["Capital of Bahamas", "Caribbean paradise", "Pink sand beaches"]),
            ("Bridgetown", (13.1939, -59.5432), "Barbados", "North America", ["Capital of Barbados", "Rum birthplace", "Cricket"]),
            ("Port of Spain", (10.6918, -61.2225), "Trinidad and Tobago", "North America", ["Capital of Trinidad", "Carnival", "Oil and gas"]),
            ("Georgetown", (6.8013, -58.1551), "Guyana", "South America", ["Capital of Guyana", "Only English-speaking South American country", "Kaieteur Falls"]),
            ("Paramaribo", (5.8520, -55.2038), "Suriname", "South America", ["Capital of Suriname", "Dutch colonial", "Amazon rainforest"]),
            ("Cayenne", (4.9375, -52.3260), "French Guiana", "South America", ["Capital of French Guiana", "Space center", "French territory"]),
            ("Malé", (4.1755, 73.5093), "Maldives", "Asia", ["Capital of Maldives", "Lowest country", "Coral atolls"]),
            ("Bandar Seri Begawan", (4.9031, 114.9398), "Brunei", "Asia", ["Capital of Brunei", "Oil sultanate", "Southeast Asia"]),
            ("Dili", (-8.5569, 125.5603), "East Timor", "Asia", ["Capital of East Timor", "Newest Asian nation", "Portuguese colonial"]),
            ("Moroni", (-11.7172, 43.2473), "Comoros", "Africa", ["Capital of Comoros", "Volcanic islands", "Ylang-ylang perfume"]),
            ("Victoria", (-4.6199, 55.4513), "Seychelles", "Africa", ["Capital of Seychelles", "Granite islands", "Coco de mer"]),
            ("Port Louis", (-20.1619, 57.5012), "Mauritius", "Africa", ["Capital of Mauritius", "Dodo bird extinct", "Sugar and tourism"]),
            ("Praia", (14.9177, -23.5092), "Cape Verde", "Africa", ["Capital of Cape Verde", "Atlantic islands", "Creole culture"]),
            ("São Tomé", (0.3365, 6.7273), "São Tomé and Príncipe", "Africa", ["Capital of São Tomé", "Equatorial islands", "Cocoa plantations"]),
            ("Malabo", (3.7558, 8.7892), "Equatorial Guinea", "Africa", ["Capital of Equatorial Guinea", "Oil rich", "Spanish speaking Africa"]),
            ("Libreville", (0.4162, 9.4673), "Gabon", "Africa", ["Capital of Gabon", "Equatorial rainforest", "Oil wealth"]),
            ("N'Djamena", (12.1348, 15.0557), "Chad", "Africa", ["Capital of Chad", "Lake Chad", "Sahel region"]),
            ("Bangui", (4.3947, 18.5582), "Central African Republic", "Africa", ["Capital of CAR", "Geographic center of Africa", "Diamonds"]),
            ("Banjul", (13.4549, -16.5790), "Gambia", "Africa", ["Capital of Gambia", "Smallest African mainland country", "River Gambia"]),
            ("Bissau", (11.8811, -15.6178), "Guinea-Bissau", "Africa", ["Capital of Guinea-Bissau", "Portuguese colonial", "Cashew nuts"]),
            ("Conakry", (9.6412, -13.5784), "Guinea", "Africa", ["Capital of Guinea", "Bauxite mining", "West Africa"]),
            ("Freetown", (8.4657, -13.2317), "Sierra Leone", "Africa", ["Capital of Sierra Leone", "Freed slaves", "Blood diamonds"]),
            ("Monrovia", (6.2907, -10.7605), "Liberia", "Africa", ["Capital of Liberia", "American colony", "Never colonized"]),
        ]
        
        # Process cities and create challenges
        for cities, difficulty in [
            (cities_easy, DifficultyLevel.EASY),
            (cities_medium, DifficultyLevel.MEDIUM), 
            (cities_hard, DifficultyLevel.HARD),
            (cities_expert, DifficultyLevel.EXPERT)
        ]:
            for name, coords, country, continent, hints in cities:
                # Calculate max distance based on difficulty (10x more forgiving)
                max_distances = {
                    DifficultyLevel.EASY: 10000,    # 10000km for easy (was 1000km)
                    DifficultyLevel.MEDIUM: 5000,   # 5000km for medium (was 500km)
                    DifficultyLevel.HARD: 2500,     # 2500km for hard (was 250km)
                    DifficultyLevel.EXPERT: 1000    # 1000km for expert (was 100km)
                }
                
                challenge = GameChallenge(
                    location_name=name,
                    actual_coordinates=coords,
                    country=country,
                    continent=continent,
                    difficulty=difficulty,
                    hints=hints,
                    max_distance_km=max_distances[difficulty]
                )
                
                challenges_data.append({
                    'id': f"{name.lower().replace(' ', '_')}_{country.lower().replace(' ', '_')}",
                    'location_name': challenge.location_name,
                    'latitude': challenge.actual_coordinates[0],
                    'longitude': challenge.actual_coordinates[1],
                    'country': challenge.country,
                    'continent': challenge.continent,
                    'difficulty': challenge.difficulty.value,
                    'hints': challenge.hints,
                    'max_distance_km': challenge.max_distance_km
                })
        
        # Convert to GeoDataFrame for spatial operations
        df = pd.DataFrame(challenges_data)
        geometry = [Point(lon, lat) for lat, lon in zip(df['latitude'], df['longitude'])]
        gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
        
        print(f"✅ Loaded {len(gdf)} geographic challenges across {len(gdf['difficulty'].unique())} difficulty levels")
        return gdf
    
    def _initialize_statistics(self) -> Dict:
        """Initialize game statistics tracking (percentage-based scoring)"""
        return {
            'total_games': 0,
            'correct_guesses': 0,
            'total_score': 0,
            'average_distance': 0.0,
            'best_score': 0,
            'worst_score': 100,  # Start at 100% instead of 1000
            'difficulty_stats': {level.value: {'attempts': 0, 'successes': 0} for level in DifficultyLevel}
        }
    
    def get_challenge_by_difficulty(self, difficulty: DifficultyLevel = None) -> GameChallenge:
        """
        Get a random challenge, optionally filtered by difficulty
        Uses Pandas for intelligent selection based on player performance
        """
        available_challenges = self.challenges_database.copy()

        # Filter by difficulty only when explicitly requested
        if difficulty:
            available_challenges = available_challenges[
                available_challenges['difficulty'] == difficulty.value
            ]

        # Avoid repeating recent challenges
        if len( self.player_history ) > 0:
            recentNames = self.player_history.tail( 8 )[ 'location_name' ].tolist()
            filtered = available_challenges[
                ~available_challenges[ 'location_name' ].isin( recentNames )
            ]
            # Only apply filter if enough remain
            if len( filtered ) > 0:
                available_challenges = filtered

        selected_row = available_challenges.sample(n=1).iloc[0]
        
        challenge = GameChallenge(
            location_name=selected_row['location_name'],
            actual_coordinates=(selected_row['latitude'], selected_row['longitude']),
            country=selected_row['country'],
            continent=selected_row['continent'],
            difficulty=DifficultyLevel(selected_row['difficulty']),
            hints=selected_row['hints'],
            max_distance_km=selected_row['max_distance_km']
        )
        
        self.current_challenge = challenge
        self.challenge_start_time = datetime.now()
        
        return challenge
    
    def _calculate_adaptive_difficulty(self) -> DifficultyLevel:
        """
        Calculate appropriate difficulty based on player performance using Pandas analytics
        """
        if len(self.player_history) < 3:
            # Mix difficulties from the start so player sees variety
            import random as _random
            return _random.choice( [ DifficultyLevel.EASY, DifficultyLevel.EASY, DifficultyLevel.MEDIUM ] )

        # Analyze recent performance (last 10 games)
        recent_games = self.player_history.tail(10)
        
        # Calculate performance metrics using Pandas (percentage-based scores)
        avg_score = recent_games['accuracy_score'].mean()
        success_rate = (recent_games['accuracy_score'] > 70).sum() / len(recent_games)  # 70% success threshold
        avg_response_time = recent_games['response_time'].mean()
        
        # Difficulty adjustment logic (percentage-based thresholds)
        if avg_score > 80 and success_rate > 0.7:  # 80% average score
            if avg_response_time < 10:  # Fast and accurate = Expert
                return DifficultyLevel.EXPERT
            else:
                return DifficultyLevel.HARD
        elif avg_score > 60 and success_rate > 0.5:  # 60% average score
            return DifficultyLevel.MEDIUM
        else:
            return DifficultyLevel.EASY
    
    def calculate_distance_km(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """
        Calculate great-circle distance between two points using Haversine formula
        Professional geographic distance calculation
        """
        lat1, lon1 = math.radians(point1[0]), math.radians(point1[1])
        lat2, lon2 = math.radians(point2[0]), math.radians(point2[1])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth's radius in kilometers
        earth_radius_km = 6371.0
        return earth_radius_km * c
    
    def score_attempt(self, clicked_coordinates: Tuple[float, float]) -> PlayerAttempt:
        """Score a player's attempt using advanced spatial analysis with percentage-based scoring."""
        if not self.current_challenge or not self.challenge_start_time:
            raise ValueError("No active challenge")

        distance_km = self.calculate_distance_km(
            clicked_coordinates,
            self.current_challenge.actual_coordinates
        )

        response_time = (datetime.now() - self.challenge_start_time).total_seconds()

        threshold_km = self.getThresholdKm( self.current_challenge )

        if distance_km > threshold_km:
            # Outside threshold - calculate what score would have been, then apply 80% penalty
            max_distance = threshold_km * 2  # Use double threshold for outside scoring
            base_score = max(0, 1000 * (1 - distance_km / max_distance))
            time_bonus = max(0, 100 * (1 - response_time / 60))

            difficulty_multipliers = {
                DifficultyLevel.EASY:   1.0,
                DifficultyLevel.MEDIUM: 1.2,
                DifficultyLevel.HARD:   1.5,
                DifficultyLevel.EXPERT: 2.0,
            }
            multiplier = difficulty_multipliers[ self.current_challenge.difficulty ]
            max_achievable = int( 1000 * multiplier + 100 )
            raw_score = max( 0, min( max_achievable, int( ( base_score + time_bonus ) * multiplier ) ) )
            calculated_score = int( ( raw_score / max_achievable ) * 100 ) if max_achievable > 0 else 0
            # Apply 80% penalty for being outside threshold
            final_score = max( 0, int( calculated_score * 0.20 ) )
        else:
            max_distance = threshold_km
            base_score = max(0, 1000 * (1 - distance_km / max_distance))
            time_bonus = max(0, 100 * (1 - response_time / 60))

            difficulty_multipliers = {
                DifficultyLevel.EASY:   1.0,
                DifficultyLevel.MEDIUM: 1.2,
                DifficultyLevel.HARD:   1.5,
                DifficultyLevel.EXPERT: 2.0,
            }
            multiplier = difficulty_multipliers[ self.current_challenge.difficulty ]
            max_achievable = int( 1000 * multiplier + 100 )
            raw_score = max( 0, min( max_achievable, int( ( base_score + time_bonus ) * multiplier ) ) )
            final_score = int( ( raw_score / max_achievable ) * 100 ) if max_achievable > 0 else 0

        attempt = PlayerAttempt(
            challenge_id = f"{self.current_challenge.location_name}_{datetime.now().timestamp()}",
            clicked_coordinates = clicked_coordinates,
            distance_km = distance_km,
            accuracy_score = final_score,
            response_time_seconds = response_time,
            timestamp = datetime.now()
        )

        new_row = {
            'challenge_id':    attempt.challenge_id,
            'location_name':   self.current_challenge.location_name,
            'difficulty':      self.current_challenge.difficulty.value,
            'distance_km':     attempt.distance_km,
            'accuracy_score':  attempt.accuracy_score,
            'response_time':   attempt.response_time_seconds,
            'timestamp':       attempt.timestamp,
        }
        self.player_history = pd.concat(
            [ self.player_history, pd.DataFrame( [ new_row ] ) ],
            ignore_index = True
        )

        self.current_challenge = None
        self.challenge_start_time = None
        return attempt

    def getThresholdKm( self, challenge ) -> float:
        """
        Compute scoring threshold in km based on country size × difficulty multiplier.
        Large countries (Russia, Canada) get bigger rings; small countries (UK, Singapore) get smaller ones.
        Clamped to [ MIN_THRESHOLD_KM, MAX_THRESHOLD_KM ].
        """
        # Approximate country areas in km² — covers all challenge countries
        COUNTRY_AREA_KM2: Dict[ str, float ] = {
            "Russia":              17_098_242, "Canada":            9_984_670,
            "United States":        9_833_517, "China":             9_596_960,
            "Brazil":               8_515_767, "Australia":         7_692_024,
            "India":                3_287_263, "Argentina":         2_780_400,
            "Kazakhstan":           2_724_900, "Algeria":           2_381_741,
            "Democratic Republic of the Congo": 2_344_858,
            "Saudi Arabia":         2_149_690, "Mexico":            1_964_375,
            "Indonesia":            1_904_569, "Sudan":             1_861_484,
            "Libya":                1_759_540, "Iran":              1_648_195,
            "Mongolia":             1_564_116, "Peru":              1_285_216,
            "Chad":                 1_284_000, "Niger":             1_267_000,
            "Angola":               1_246_700, "Mali":              1_240_192,
            "South Africa":         1_219_090, "Colombia":          1_141_748,
            "Ethiopia":             1_104_300, "Bolivia":           1_098_581,
            "Mauritania":           1_030_700, "Egypt":             1_001_450,
            "Tanzania":               945_087, "Nigeria":             923_768,
            "Venezuela":              916_445, "Namibia":             824_292,
            "Mozambique":             801_590, "Pakistan":            881_913,
            "Turkey":                 783_562, "Chile":               756_102,
            "Zambia":                 752_612, "Myanmar":             676_578,
            "Afghanistan":            652_230, "Somalia":             637_657,
            "Central African Republic": 622_984,
            "Ukraine":                603_550, "Botswana":            581_730,
            "Madagascar":             587_041, "Kenya":               580_367,
            "France":                 643_801, "Thailand":            513_120,
            "Spain":                  505_990, "Turkmenistan":        488_100,
            "Cameroon":               475_442, "Papua New Guinea":    462_840,
            "Sweden":                 450_295, "Uzbekistan":          448_978,
            "Iraq":                   438_317, "Morocco":             446_550,
            "Paraguay":               406_752, "Zimbabwe":            390_757,
            "Japan":                  377_915, "Germany":             357_114,
            "Congo":                  342_000, "Finland":             338_145,
            "Malaysia":               329_847, "Vietnam":             331_212,
            "Norway":                 323_802, "Ivory Coast":         322_463,
            "Poland":                 312_696, "Oman":                309_500,
            "Italy":                  301_340, "Philippines":         300_000,
            "Ecuador":                283_561, "Burkina Faso":        274_200,
            "New Zealand":            268_838, "Gabon":               267_668,
            "Guinea":                 245_857, "United Kingdom":      243_610,
            "Uganda":                 241_038, "Ghana":               238_533,
            "Romania":                238_397, "Laos":                236_800,
            "Guyana":                 214_969, "Belarus":             207_600,
            "Kyrgyzstan":             199_951, "Senegal":             196_722,
            "Syria":                  185_180, "Cambodia":            181_035,
            "Uruguay":                176_215, "Suriname":            163_820,
            "Tunisia":                163_610, "Bangladesh":          147_570,
            "Nepal":                  147_181, "Tajikistan":          143_100,
            "Greece":                 131_957, "Nicaragua":           130_373,
            "North Korea":            120_538, "Malawi":              118_484,
            "Eritrea":                117_600, "Benin":               112_622,
            "Honduras":               112_492, "Liberia":             111_369,
            "Bulgaria":               110_879, "Cuba":                109_884,
            "Guatemala":              108_889, "Iceland":             103_000,
            "South Korea":             99_678, "Hungary":              93_028,
            "Portugal":                92_212, "Jordan":               89_342,
            "Azerbaijan":              86_600, "Austria":              83_871,
            "UAE":                     83_600, "Czech Republic":       78_866,
            "Serbia":                  77_474, "Panama":               75_417,
            "Georgia":                 69_700, "Sri Lanka":            65_610,
            "Lithuania":               65_300, "Latvia":               64_589,
            "Croatia":                 56_594, "Bosnia and Herzegovina": 51_197,
            "Costa Rica":              51_100, "Slovakia":             49_035,
            "Dominican Republic":      48_671, "Estonia":              45_228,
            "Denmark":                 42_924, "Netherlands":          41_543,
            "Switzerland":             41_285, "Bhutan":               38_394,
            "Moldova":                 33_846, "Belgium":              30_528,
            "Armenia":                 29_743, "Albania":              28_748,
            "Solomon Islands":         28_896, "Equatorial Guinea":    28_051,
            "Burundi":                 27_830, "Haiti":                27_750,
            "North Macedonia":         25_713, "Djibouti":             23_200,
            "Belize":                  22_966, "El Salvador":          21_041,
            "Israel":                  20_770, "Slovenia":             20_273,
            "Fiji":                    18_274, "Kosovo":               10_887,
            "Cyprus":                   9_251, "Luxembourg":            2_586,
            "Vanuatu":                 12_189, "Samoa":                 2_842,
            "Montenegro":              13_812, "Eswatini":             17_364,
            "Lesotho":                 30_355, "Timor-Leste":          14_874,
            "Tonga":                      747, "Marshall Islands":        181,
            "Tuvalu":                      26, "Palau":                   459,
            "Cook Islands":               236, "Nauru":                    21,
            "Kiribati":                   811, "Maldives":               298,
            "Bahrain":                    765, "Singapore":              728,
            "Hong Kong":                 1_104, "Greenland":          836_330,
            "Puerto Rico":               9_104, "Macau":                  115,
        }

        # Difficulty multipliers applied to the country-size bonus only
        DIFFICULTY_MULTIPLIER: Dict[ DifficultyLevel, float ] = {
            DifficultyLevel.EASY:   2.0,
            DifficultyLevel.MEDIUM: 1.4,
            DifficultyLevel.HARD:   1.0,
            DifficultyLevel.EXPERT: 0.65,
        }

        BASE_THRESHOLD_KM = 500.0   # every country gets at least this
        MAX_THRESHOLD_KM  = 900.0

        areaKm2 = COUNTRY_AREA_KM2.get( challenge.country, 500_000 )
        multiplier = DIFFICULTY_MULTIPLIER[ challenge.difficulty ]
        # Large countries push the threshold above the base; small ones stay at base
        countryKm = math.sqrt( areaKm2 ) * multiplier
        return min( MAX_THRESHOLD_KM, max( BASE_THRESHOLD_KM, countryKm ) )

    def _update_statistics(self, attempt: PlayerAttempt):
        """Update game statistics using Pandas analytics (percentage-based scoring)"""
        stats = self.game_statistics
        stats['total_games'] += 1
        stats['total_score'] += attempt.accuracy_score
        
        if attempt.accuracy_score > 70:  # Consider 70%+ as "correct"
            stats['correct_guesses'] += 1
        
        stats['best_score'] = max(stats['best_score'], attempt.accuracy_score)
        stats['worst_score'] = min(stats['worst_score'], attempt.accuracy_score)
        
        # Update difficulty-specific stats
        difficulty = self.current_challenge.difficulty.value
        stats['difficulty_stats'][difficulty]['attempts'] += 1
        if attempt.accuracy_score > 70:  # 70% threshold for success
            stats['difficulty_stats'][difficulty]['successes'] += 1
        
        # Calculate running averages using Pandas
        if len(self.player_history) > 0:
            stats['average_distance'] = self.player_history['distance_km'].mean()
    
    def get_performance_analytics(self) -> Dict:
        """
        Generate comprehensive performance analytics using Pandas
        Demonstrates advanced statistical analysis capabilities
        """
        if len(self.player_history) == 0:
            return {"message": "No games played yet"}
        
        df = self.player_history
        
        analytics = {
            "overview": {
                "total_games": len(df),
                "average_score": df['accuracy_score'].mean(),
                "median_score": df['accuracy_score'].median(),
                "score_std": df['accuracy_score'].std(),
                "best_score": df['accuracy_score'].max(),
                "worst_score": df['accuracy_score'].min()
            },
            "distance_analysis": {
                "average_distance_km": df['distance_km'].mean(),
                "median_distance_km": df['distance_km'].median(),
                "best_distance_km": df['distance_km'].min(),
                "worst_distance_km": df['distance_km'].max(),
                "distance_percentiles": {
                    "25th": df['distance_km'].quantile(0.25),
                    "75th": df['distance_km'].quantile(0.75),
                    "90th": df['distance_km'].quantile(0.90)
                }
            },
            "time_analysis": {
                "average_response_time": df['response_time'].mean(),
                "median_response_time": df['response_time'].median(),
                "fastest_response": df['response_time'].min(),
                "slowest_response": df['response_time'].max()
            },
            "difficulty_breakdown": df.groupby('difficulty').agg({
                'accuracy_score': ['count', 'mean', 'std'],
                'distance_km': 'mean',
                'response_time': 'mean'
            }).round(2).to_dict(),
            "performance_trends": self._calculate_performance_trends(),
            "geographic_analysis": self._analyze_geographic_performance()
        }
        
        return analytics
    
    def _calculate_performance_trends(self) -> Dict:
        """Calculate performance trends over time using Pandas"""
        if len(self.player_history) < 5:
            return {"message": "Need more games for trend analysis"}
        
        df = self.player_history.copy()
        df['game_number'] = range(1, len(df) + 1)
        
        # Calculate rolling averages
        df['rolling_score_5'] = df['accuracy_score'].rolling(window=5, min_periods=1).mean()
        df['rolling_distance_5'] = df['distance_km'].rolling(window=5, min_periods=1).mean()
        
        # Linear regression for trend analysis
        recent_games = df.tail(10)
        
        # Ensure numeric types for numpy polyfit
        game_numbers = recent_games['game_number'].astype(float).values
        scores = recent_games['accuracy_score'].astype(float).values
        distances = recent_games['distance_km'].astype(float).values
        
        score_trend = np.polyfit(game_numbers, scores, 1)[0]
        distance_trend = np.polyfit(game_numbers, distances, 1)[0]
        
        return {
            "score_trend": "improving" if score_trend > 0 else "declining" if score_trend < 0 else "stable",
            "distance_trend": "improving" if distance_trend < 0 else "declining" if distance_trend > 0 else "stable",
            "recent_average_score": recent_games['accuracy_score'].mean(),
            "score_improvement": score_trend,
            "distance_improvement": -distance_trend  # Negative because lower distance is better
        }
    
    def _analyze_geographic_performance(self) -> Dict:
        """Analyze performance by geographic regions using GeoPandas"""
        if len(self.player_history) == 0:
            return {}
        
        # Merge player history with challenges database for geographic analysis
        df = self.player_history.merge(
            self.challenges_database[['location_name', 'continent', 'country']], 
            on='location_name', 
            how='left'
        )
        
        # Performance by continent
        continent_stats = df.groupby('continent').agg({
            'accuracy_score': ['count', 'mean', 'std'],
            'distance_km': 'mean'
        }).round(2)
        
        # Best and worst performing regions
        continent_means = df.groupby('continent')['accuracy_score'].mean().sort_values(ascending=False)
        
        return {
            "best_continent": continent_means.index[0] if len(continent_means) > 0 else None,
            "worst_continent": continent_means.index[-1] if len(continent_means) > 0 else None,
            "continent_performance": continent_stats.to_dict(),
            "games_by_continent": df['continent'].value_counts().to_dict()
        }
    
    def get_hint(self, hint_level: int = 0) -> str:
        """Get a hint for the current challenge"""
        if not self.current_challenge:
            return "No active challenge"
        
        hints = self.current_challenge.hints
        if hint_level < len(hints):
            return hints[hint_level]
        else:
            # Generate geographic hint using spatial analysis
            lat, lon = self.current_challenge.actual_coordinates
            
            # Determine hemisphere and general region
            hemisphere_ns = "Northern" if lat > 0 else "Southern"
            hemisphere_ew = "Eastern" if lon > 0 else "Western"
            
            region_hint = f"Located in the {hemisphere_ns} and {hemisphere_ew} hemispheres"
            
            # Add climate zone hint
            if abs(lat) < 23.5:
                climate_hint = "In the tropical zone"
            elif abs(lat) < 66.5:
                climate_hint = "In the temperate zone"
            else:
                climate_hint = "In the polar zone"
            
            return f"{region_hint}. {climate_hint}."
    
    def export_performance_data(self) -> pd.DataFrame:
        """Export player history for external analysis"""
        return self.player_history.copy()
