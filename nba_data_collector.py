import requests
from bs4 import BeautifulSoup, Comment
import pandas as pd
import time

header_parameter = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
}

"""
https://www.basketball-reference.com/players/a/
https://www.basketball-reference.com/awards/awards_2021.html
https://www.basketball-reference.com/players/m/mitchdo01.html
https://www.basketball-reference.com/leaders/mp_career.html

"""

"""
url should be the whole thing. If need to change change outside of the class
"""

class NbaDataCollector:
    def __init__(self, table_id, url):
        self.award = table_id
        self.url = url
        self.headers = []
        self.table = None
        self.all_stats = []
        self.tmp_dict = {}
        self.data = {}
        self.soup = None
        self.web_content = None
        self.df = None
        self.get_headers()

    def get_stats_from_comments(self):
        self.web_content = requests.get(url=self.url, headers=header_parameter).text
        self.soup = BeautifulSoup(self.web_content, "lxml")
        comments = self.soup.find_all(string=lambda text: isinstance(text, Comment))
        for comment in comments:
            if "table" in comment:
                if self.award in comment:
                    commentsoup = BeautifulSoup(comment, 'lxml')
                    table_soup = commentsoup.select_one(selector="table")
                    # all_stats_comments = commentsoup.select(selector=f"table tbody tr {tag}")
        return table_soup

    def get_table(self):
        print(self.url)
        self.web_content = requests.get(url=self.url, headers=header_parameter).text
        self.soup = BeautifulSoup(self.web_content, "lxml")

        all_tables = self.soup.select(selector="table")
        for table in all_tables:
            if self.award in table.get("id"):
                self.table = table
                # To get the first table with the id
                break

        if self.table == None:
            self.table = self.get_stats_from_comments()
            print("got it from comments")

    def get_headers(self, year=""):
        self.get_table()

        try:
            header_html = self.table.select(selector="thead tr")[1].select(selector="th")
        except:
            header_html = self.table.select(selector="thead tr")[0].select(selector="th")

        self.headers = [header.get('data-stat') for header in header_html]
        if None in self.headers:
            self.headers = [header.text for header in header_html]
        self.populate_data_headers()

    def populate_data_headers(self):
        for header in self.headers:
            self.data[header] = []
        self.data['year'] = []
        self.data['player_url'] = []
        self.data['player_img'] = []

    def get_data_with_overheader(self, all_stats, year):
        for header in self.headers:
            tmp_list = [stat.text for stat in all_stats if stat.get('data-stat') == header]
            # print(f"length of tmp_list is {len(tmp_list)}")

            years = [year for i in range(len(tmp_list))]
            self.data[header].extend(tmp_list)

        self.data['year'].extend(years)
        print("Collected data with data-stat")

    def get_data_without_overheader(self, all_stats, year):
        for i in range(len(self.headers)):
            tmp_list = [stat.text for stat in all_stats[i::len(self.headers)]]
            years = [year for i in range(len(tmp_list))]
            self.data[self.headers[i]].extend(tmp_list)

        self.data['year'].extend(years)
        print("Collected data without overheader")

    def get_data(self, year=""):
        self.all_stats = []
        self.table = None
        self.get_table()

        all_stats_th = self.table.select(selector="tbody tr th")
        all_stats_td = self.table.select(selector="tbody tr td")
        if len(all_stats_td) == 0:
            # Table somehow doesn't have a tbody
            all_stats_td = self.table.select(selector="tr td")

        if len(all_stats_th) != 0:
            columns_no = len(self.headers)
            all_stats_len = len(all_stats_td) + len(all_stats_th)
            for i in range(all_stats_len):
                if i == 0:
                    self.all_stats.append(all_stats_th[i])
                elif i % columns_no == 0:
                    self.all_stats.append(all_stats_th[int(i / columns_no)])
                else:
                    self.all_stats.append(all_stats_td[0])
                    all_stats_td = all_stats_td[1:]
        else:
            self.all_stats = all_stats_td

        self.get_data_with_overheader(self.all_stats, year)
        if len(self.data[self.headers[0]]) == 0:
            self.get_data_without_overheader(self.all_stats, year)

        self.get_player_links(self.all_stats)

        print(f"{self.url} Done Collecting")

    def get_player_links(self, all_stats):
        """Get player links and their image url"""
        tmp_list = [f"https://www.basketball-reference.com/{stat.find(name='a').get('href')}" for stat in all_stats if stat.get('data-stat') == 'player']
        player_img = [f"https://www.basketball-reference.com/req/202106291/images/players/{link.split('/')[-1].split('.')[0]}.jpg" for link in tmp_list]
        self.data['player_url'].extend(tmp_list)
        self.data['player_img'].extend(player_img)

    def populate_dict(self):
        for stat, values in self.data.items():
            for i in range(len(values)):
                if values[i] == "":
                    values[i] = "NO DATA"
                self.tmp_dict[i] = values[i]
            self.data[stat] = self.tmp_dict
            self.tmp_dict = {}

    def collect_upload_all_data(self, csv_name):
        start_time = time.time()
        self.populate_dict()
        self.df = pd.DataFrame(self.data)
        self.df.to_csv(csv_name)
        print(f"{csv_name} has been created")
        print("--- %s seconds ---" % (time.time() - start_time))






