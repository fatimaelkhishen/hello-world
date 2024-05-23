import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def get_job_links():
    job_links = []
    p = 0

    driver = webdriver.Chrome()
    while True:
        url = f"https://reliefweb.int/jobs?list=United%20States%20of%20America%20%28USA%29%20Jobs&advanced-search=%28C245%29&page={p}"

        driver.get(url)
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        job_cards = soup.find_all("article", class_="rw-river-article--card rw-river-article rw-river-article--job")
        for job_card in job_cards:
            title = job_card.find("h3", class_="rw-river-article__title")
            link = title.find('a').get('href')
            job_links.append(link)
        next_button = soup.find('li', class_="cd-pager__item cd-pager__item--next")
        if not next_button:
            break
        p += 1
    driver.quit()
    return job_links

def construct_job(driver, job_link):
    driver.get(job_link)
    time.sleep(7)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    try:
        title = soup.find('h1', class_='rw-article__title rw-page-title').text.strip()
    except:
        title = "NA"
    try:
        company = soup.find('a', class_="rw-entity-meta__tag-link").text.strip()
    except:
        company = "NA"
   
    try:
        job_description = soup.find('div', class_="rw-article__content").text.strip()
    except:
        job_description = "NA"
    try:
        date_element = soup.find('time')
        posting_date = date_element['datetime'][:10]
    except:
        posting_date = "NA"
    try:
        country = soup.find('dd', class_='rw-entity-meta__tag-value--country').text.strip()
    except:
        country = "NA"
    try:
        source = soup.find('dd', class_='rw-entity-meta__tag-value--source').text.strip()
    except:
        source = "NA"
    try:
        job_type = soup.find('dd', class_='rw-entity-meta__tag-value--type').text.strip()
    except:
        job_type = "NA"
    try:
        career_category = soup.find('dd', class_='rw-entity-meta__tag-value--career-category').text.strip()
    except:
        career_category = "NA"
    try:
        years_of_experience = soup.find('dd', class_='rw-entity-meta__tag-value--experience').text.strip()
    except:
        years_of_experience = "NA"

    jobPosting = {
        'SRC_Title': title,
        'SRC_Company': company,
        'SRC_Country': country,
        'SRC_Source': source,
        'SRC_Type': job_type,
        'SRC_Category': career_category,
        'SRC_Experience': years_of_experience,
        'SRC_Description': job_description,
        'Posting_date': posting_date,
        'Job_Link': job_link,
        'Website': 'reliefweb'
    }
    return jobPosting

def save_to_excel(job_data):
    df = pd.DataFrame(job_data)
    df.to_excel("jobs.xlsx", index=False)

def main():
    job_links = get_job_links()
    driver = webdriver.Chrome()
    job_data = []
    for link in job_links:
        job_posting = construct_job(driver, link)
        job_data.append(job_posting)
    driver.quit()
    save_to_excel(job_data)

if __name__ == "__main__":
    main()
# job_links = get_job_links()
# print(job_links)