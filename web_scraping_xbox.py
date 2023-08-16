from selenium import webdriver
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
import time

start_time = time.time()

def get_titles(soup):
    title = []
    for div in soup.find_all(name="div", attrs={"class":"box box-success"}):
        for body in div.find_all(name="div", attrs={"class":"box-body comparison-table-entry"}):
            for title_box in body.find_all(name="span", attrs={"class":"box-title"}):
                title_ = title_box.find_all(name="a")
                if title_:
                    for title__ in title_:
                        title.append(title__['title'])
                else:
                    title.append('N/A')
    return title

def get_short_desc(soup):
    short_desc = []
    for div in soup.find_all(name="div", attrs={"class":"col-xs-12"}):
        for div_ in div.find_all(name="div", attrs={"class":"box box-success"}):
            for body in div_.find_all(name="div", attrs={"class":"box-body comparison-table-entry"}):
                for desc_box in body.find_all(name="div", attrs={"class":"box-body hidden-xs"}):
                    desc_elements = desc_box.find_all(name="div", attrs={"style":"text-align: justify;"})
                    if desc_elements:
                        for desc_ in desc_elements:
                            short_desc.append(desc_.text)
                    else:
                        short_desc.append('N/A')
    return short_desc

def get_desc(soup):
    desc = []
    for div in soup.find_all(name="div", attrs={"class":"col-xs-12"}):
        for div_ in div.find_all(name="div", attrs={"class":"box box-success"}):
            for body in div_.find_all(name="div", attrs={"class":"box-body comparison-table-entry"}):
                for desc_box in body.find_all(name="div", attrs={"class":"box-body hidden-xs"}):
                    desc_elements = desc_box.find_all(name="a")
                    if desc_elements:
                        for desc_ in desc_elements:
                            desc.append(desc_['data-content'])
                    else:
                        desc.append('N/A')
    return desc

def get_release(soup):
    release_date = []
    for div in soup.find_all(name="div", attrs={"class":"col-xs-12"}):
        for div_ in div.find_all(name="div", attrs={"class":"box box-success"}):
            for body in div_.find_all(name="div", attrs={"class":"box-body comparison-table-entry"}):
                release = body.find_all(name="div", attrs={"class":"col-xs-12 col-lg-6 col-lg-pull-6"})
                if release:
                    for releasedate in release:
                        release_date.append(releasedate.text.strip())
                else:
                    release_date.append('N/A')
    return release_date

def get_rating(soup):
    rating = []
    for div in soup.find_all(name="div", attrs={"class":"col-xs-12"}):
        for div_ in div.find_all(name="div", attrs={"class":"box box-success"}):
            for body in div_.find_all(name="div", attrs={"class":"box-body comparison-table-entry"}):
                for col_xs in body.find_all(name="div", attrs={"class":"col-xs-12 col-sm-8 col-md-7 col-md-push-1 col-sm-push-4 col-pad-left-5"}):
                    for rating_box in col_xs.find_all(name="div", attrs={"class":"rating-box"}):
                        for rating_detail in rating_box.find_all(name="span", attrs={"class":"showTooltip", "data-placement":"top"}):
                            rating.append(rating_detail.text.strip())
    return rating

def get_price(soup):
    price = []
    for div in soup.find_all(name="div", attrs={"class":"col-xs-12"}):
        for div_ in div.find_all(name="div", attrs={"class":"box box-success"}):
            for body in div_.find_all(name="div", attrs={"class":"box-body comparison-table-entry"}):
                for price_box in body.find_all(name="div", attrs={"class":"col-xs-6 col-sm-offset-4 col-md-offset-0 col-sm-4 col-md-2 col-lg-1 col-lg-pad-5"}):
                    price_ = price_box.find_all(name="dt", attrs={"style":"white-space: nowrap; margin-left: 1px"})
                    if price_:
                        for price_usd in price_:
                            price.append(price_usd.text.strip())
                    else:
                        price.append("N/A")
    return price

def scrape_data_from_soup(soup, page):
    titles = get_titles(soup)
    short_desc = get_short_desc(soup)
    descriptions = get_desc(soup)
    release_dates = get_release(soup)
    ratings = get_rating(soup)
    prices = get_price(soup)

    data = {
        'Page': page,
        'Title': titles,
        'Short Description': short_desc,
        'Description': descriptions,
        'Release Date': release_dates,
        'Rating': ratings,
        'Price': prices
    }

    return data

while True:
    page_start = input("Page start number to scrape: ")
    try:
        page_start = int(page_start)
    except ValueError:
        print("Select page in number (ex: 1)")
        continue

    page_end = input("Page end number to scrape: ")
    try:
        page_end = int(page_end)
    except ValueError:
        print("Select page in number (ex: 1)")
        continue

    sleep = input("Time to load webpage before closed (in second): ")
    try:
        sleep = int(sleep)
    except ValueError:
        print("Select time in number (ex: 1)")
        continue

    if page_start > 0:
        break
    else:
        print("Select page start number > 0")

print(f"Webpage will be scraped from page {page_start} to page {page_end}")


df_all_page = pd.DataFrame()

for page in tqdm(range(page_start-1, page_end)):
    page += 1
    # print(f"Processing page #{str(page)}")
    # url = 'https://www.xbox-now.com/en/games-with-gold?page='+str(page)
    url = 'https://www.xbox-now.com/en/xbox-360-comparison?page='+str(page)

    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options)

    # Navigate to the URL
    driver.get(url)
    
    time.sleep(sleep)
    page_source = driver.page_source

    # Close the browser after scraping
    driver.quit()

    soup = BeautifulSoup(page_source, 'html.parser')

    scrape_data = scrape_data_from_soup(soup, page)
    df = pd.DataFrame(scrape_data)
    df_all_page = pd.concat([df_all_page,df])
    # print(f"Processing page #{str(page)} done")


df_all_page = df_all_page.reset_index().drop(columns="index")
df_all_page.to_excel("result.xlsx",index=False)

# Record the end time
end_time = time.time()

# Calculate the duration
duration = end_time - start_time

print(f"Script took {duration:.2f} seconds to run.")





