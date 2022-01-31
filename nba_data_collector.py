import requests
from bs4 import BeautifulSoup, Comment
import pandas as pd
import time

class NbaDataCollector:
    def __init__(self, table_id, url):
        """table_id is the id attribute of the table (inspect element)
            url is the url of the page"""
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

    def get_table_from_comments(self):
        """Extract table from comments if not found in main body"""

        self.web_content = requests.get(url=self.url).text
        self.soup = BeautifulSoup(self.web_content, "lxml")
        comments = self.soup.find_all(string=lambda text: isinstance(text, Comment))
        for comment in comments:
            if "table" in comment:
                if self.award in comment:
                    commentsoup = BeautifulSoup(comment, 'lxml')
                    table_soup = commentsoup.select_one(selector="table")
        return table_soup

    def get_table(self):
        """Extra table from page using the table_id and url"""

        self.web_content = requests.get(url=self.url).text
        self.soup = BeautifulSoup(self.web_content, "lxml")

        all_tables = self.soup.select(selector="table")
        for table in all_tables:
            if self.award in table.get("id"):
                self.table = table
                # To get the first table with the id
                break

        # If table not found, find table from the comments
        if self.table == None:
            try:
                self.table = self.get_table_from_comments()
            except UnboundLocalError:
                print(f"{self.url}: Table/Website is not available")

    def get_headers(self):
        """Get the headers/column names of the table"""
        self.get_table()
        if self.table == None:
            return "No Table"

        try:
            header_html = self.table.select(selector="thead tr")[1].select(selector="th")
        except:
            try:
                # Means there is no overheader, get the first row
                header_html = self.table.select(selector="thead tr")[0].select(selector="th")
            except IndexError:
                # If header cannot be found in the thead, find it in the tbody
                try:
                    header_html = self.table.select(selector="tbody tr")[0].select(selector="th")
                except:
                    # If still cannot find, find with the class "thead"
                    try:
                        header_html = self.table.select(selector="tbody tr.thead")[0].select(selector="th")
                    except:
                        # Table does not have a tbody
                        header_html = self.table.select(selector="tr.thead")[1].select(selector="th")


        self.headers = [header.get('data-stat') for header in header_html]

        # If headers cannot be extracted with attribute data-stat, extract the text of the element
        if None in self.headers:
            self.headers = [header.text for header in header_html]
        self.populate_data_headers()

    def populate_data_headers(self):
        """Populate the object dictionary with the table's headers"""

        for header in self.headers:
            self.data[header] = []

        # Add extra headers that cannot be extracted from the table
        self.data['year'] = []
        self.data['player_url'] = []
        self.data['player_img'] = []

    def get_data_with_datastat(self, all_stats, year):
        """Extract the data from tables with data-stat attribute in element"""

        for header in self.headers:
            tmp_list = [stat.text for stat in all_stats if stat.get('data-stat') == header]

            years = [year for i in range(len(tmp_list))]
            self.data[header].extend(tmp_list)

        self.data['year'].extend(years)

    def get_data_without_datastat(self, all_stats, year):
        """Extract the data from tables without data-stat attribute in element"""

        for i in range(len(self.headers)):
            tmp_list = [stat.text for stat in all_stats[i::len(self.headers)]]
            years = [year for i in range(len(tmp_list))]
            self.data[self.headers[i]].extend(tmp_list)

        self.data['year'].extend(years)
        print("Data Collected Without Datastat")

    def get_data(self, year=""):
        """Extract the data from the page"""
        # Reset the data if a loop is used
        self.all_stats = []
        self.table = None
        self.get_table()
        if self.table == None:
            return "No Table Found"

        all_stats_tr = []

        # Get all the tr in the table, remove the tr that have a class on it as they do not hold data
        all_stats_tr_uncleaned = self.table.select(selector="tbody tr")
        if len(all_stats_tr_uncleaned) == 0:
            all_stats_tr_uncleaned = self.table.select(selector="tr")

        for stats in all_stats_tr_uncleaned:
            if not stats.has_attr("class"):
                all_stats_tr.append(stats)

        # Get the th and td element within the tr and populate the all stats list
        for stats in all_stats_tr:
            ths = stats.find_all(name="th")
            tds = stats.find_all(name="td")
            if ths != None:
                if len(ths) == 1:
                    self.all_stats.append(ths[0])
                else:
                    for th in ths:
                        self.all_stats.append(th)
            if tds != None:
                if len(tds) == 1:
                    self.all_stats.append(tds[0])
                else:
                    for td in tds:
                        self.all_stats.append(td)

        # If statistics cannot be scraped with data-stat, use other function
        self.get_data_with_datastat(self.all_stats, year)
        if len(self.data[self.headers[0]]) == 0:
            self.get_data_without_datastat(self.all_stats, year)

        self.get_player_links(self.all_stats)

        print(f"{self.url} Done Collecting")


    def get_data_failed(self, year=""):
        """Extract the data from the page: Failed version as it didnt work on all tables"""

        # Reset the data if a loop is used
        self.all_stats = []
        self.table = None
        self.get_table()

        # Some tables include rows where the th element contain the statistics instead of td
        all_stats_th_uncleaned = self.table.select(selector="tbody tr th")
        all_stats_th = []
        for stats in all_stats_th_uncleaned:
            try:
                if "right" in stats.get("class") or "left" in stats.get("class"):
                    all_stats_th.append(stats)
            except:
                pass

        all_stats_td_uncleaned = self.table.select(selector="tbody tr td")
        all_stats_td = []
        for stats in all_stats_td_uncleaned:
            try:
                if "right" in stats.get("class") or "left" in stats.get("class") or "center" in stats.get("class") or "right" in stats.get("claass") or "skip" not in stats.get("data-stat"):
                    all_stats_td.append(stats)
            except:
                pass


        # If all_stats_td have no stats, it means the table has no tbody element
        if len(all_stats_td) == 0:
            all_stats_td = self.table.select(selector="tr td")

        # If each row of statistics contain a th element, we will have to arrange the statistics in proper order
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

        # If statistics cannot be scraped with data-stat, use other function
        self.get_data_with_datastat(self.all_stats, year)
        if len(self.data[self.headers[0]]) == 0:
            self.get_data_without_datastat(self.all_stats, year)

        self.get_player_links(self.all_stats)

        print(f"{self.url} Done Collecting")

    def get_player_links(self, all_stats):
        """Get player links and their image url"""

        tmp_list = [f"https://www.basketball-reference.com/{stat.find(name='a').get('href')}" for stat in all_stats if stat.get('data-stat') == 'player']
        player_img = [f"https://www.basketball-reference.com/req/202106291/images/players/{link.split('/')[-1].split('.')[0]}.jpg" for link in tmp_list]
        self.data['player_url'].extend(tmp_list)
        self.data['player_img'].extend(player_img)

    def populate_dict(self):
        """Populate the data dictionary so that it can be converted into a csv"""

        for stat, values in self.data.items():
            for i in range(len(values)):
                if values[i] == "":
                    values[i] = "NO DATA"
                self.tmp_dict[i] = values[i]
            self.data[stat] = self.tmp_dict
            self.tmp_dict = {}

    def collect_upload_all_data(self, csv_name):
        """Upload the data into a pandas dataframe and csv file"""

        start_time = time.time()
        self.populate_dict()
        self.df = pd.DataFrame(self.data)
        self.df.to_csv(csv_name)
        print(f"{csv_name} has been created")
        print("--- %s seconds ---" % (time.time() - start_time))





