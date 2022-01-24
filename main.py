import string
from nba_data_collector import *

start_time = time.time()


#Get all players information
alphabets = [i for i in string.ascii_lowercase]
all_players = NbaDataCollector("players", "https://www.basketball-reference.com/players/a/")

for alpha in alphabets:
    all_players.url = f"https://www.basketball-reference.com/players/{alpha}/"
    all_players.get_data()


all_players.collect_upload_all_data("all_players_info.csv")

mvp = NbaDataCollector("mvp", "https://www.basketball-reference.com/awards/awards_2021.html")

for year in range(1956, 2022):
    mvp.url = f"https://www.basketball-reference.com/awards/awards_{year}.html"
    mvp.get_data(year=year)

mvp.collect_upload_all_data("mvp-from-1956-to-2021.csv")


#DPOY
dpoy = NbaDataCollector("dpoy", "https://www.basketball-reference.com/awards/awards_2010.html")

for year in range(1983, 2022):
    dpoy.url = f"https://www.basketball-reference.com/awards/awards_{year}.html"
    dpoy.get_data(year=year)


dpoy.collect_upload_all_data("dpoy-from-1984-to-2021.csv")

#ROY
roy = NbaDataCollector("roy", "https://www.basketball-reference.com/awards/awards_2010.html")

for year in range(1964, 2022):
    roy.url = f"https://www.basketball-reference.com/awards/awards_{year}.html"
    roy.get_data(year=year)

roy.collect_upload_all_data("roy-from-1964-to-2021.csv")

#SMOY
smoy = NbaDataCollector("smoy", "https://www.basketball-reference.com/awards/awards_2010.html")

for year in range(1984, 2022):
    smoy.url = f"https://www.basketball-reference.com/awards/awards_{year}.html"
    smoy.get_data(year=year)

smoy.collect_upload_all_data("smoy-from-1984-to-2021.csv")

#MIP
mip = NbaDataCollector("mip", "https://www.basketball-reference.com/awards/awards_2010.html")

for year in range(1986, 2022):
    try:
        mip.url = f"https://www.basketball-reference.com/awards/awards_{year}.html"
        mip.get_data(year=year)
    except:
        pass

mip.collect_upload_all_data("mip-from-1986-to-2021.csv")
print("--- %s seconds ---" % (time.time() - start_time))