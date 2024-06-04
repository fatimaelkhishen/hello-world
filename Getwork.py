import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import json

def get_job_links():
    job_links = []
    p = 1

    driver = webdriver.Chrome()
    while True:
        url = f"https://www.getwork.com/search?loc=151946&page={p}"    
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        job_cards = soup.find_all("div", class_="ui-job")
        for job_card in job_cards:
            link = job_card.find('a', href=True)['href']
            job_links.append(link)
        next_button = soup.find('a', class_='text-lg', string='❯')
        if not next_button:
            break  # Exit the loop if "Next page" button is not found
        p += 1
    driver.quit()
    return job_links

def construct_job(driver, job_link):
    driver.get(job_link)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    try:
        title = soup.find('h1', class_='text-2xl lg:text-3xl font-semibold mb-2').text.strip()
    except:
        title = "NA"
    try:
        company = soup.find('p', class_='text-lg').text.strip().split('\n')[0]
    except:
        company = "NA"
    try:
        location = soup.find('p', class_='text-lg').text.strip().split('\n')[1]
    except:
        location = "NA"
    try:
        json_script = soup.find("script", {"type": "application/ld+json"})
        if json_script:
            job_json = json.loads(json_script.string)
            posting_date = job_json.get("datePosted").split("T")[0]
    except:
        posting_date = "NA"
    try:
        description = soup.find('div', class_='text-lg mb-8').text.strip()
    except:
        description = "NA"

    jobPosting = {
        'SRC_Title': title,
        'SRC_Company': company,
        'SRC_Country': location,
        'Posting_date': posting_date,
        'Job_Link': job_link,
        'SRC_Description': description,
        'Website': 'Getwork'
    }
    return jobPosting
def save_to_excel(job_data):
    df = pd.DataFrame(job_data)
    df.to_excel("Getwork.xlsx", index=False)

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