# Basketball-Reference-Table-Scaper
Scrapes data from any table from basketball reference

Just have to input the table id (inspect element) and the URL

**Example of how to use the scraper**

1. Scrape mvp data from 1956 to 2021

table_id = "mvp"

url = "https://www.basketball-reference.com/awards/awards_2021.html"

mvp = NbaDataCollector(table_id=table_id, url=url)

`for year in range(1956, 2022):`

    mvp.url = f"https://www.basketball-reference.com/awards/awards_{year}.html"
    mvp.get_data(year=year)

`mvp.collect_upload_all_data("mvp-from-1956-to-2021.csv")`

#Please email me at royalcheng99@gmail.com if you find any bugs

