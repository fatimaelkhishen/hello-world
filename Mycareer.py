import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import json

def get_job_links():
    job_links = []
    p = 1

    driver = webdriver.Chrome()
    while True:
        url = f"https://mycareer.aicpa-cima.com/jobs/united-states/{p}"

        driver.get(url + "/")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        job_cards = soup.find_all("li", class_="lister__item")
        for job_card in job_cards:
            link = job_card.find('a').get('href')
            job_links.append("https://mycareer.aicpa-cima.com"+link.replace(" \n\t", "").replace("\n\n\n\n", ""))
        next_arrow = soup.find('a', title="Next page")
        if not next_arrow:
            break  # Exit the loop if "Next page" button is not found
        p += 1
    driver.quit()
    return job_links

def construct_job(driver, job_link):
    driver.get(job_link)
    try:
        read_more_button =   driver.find_element_by_css_selector('button.mds-accordion-trigger__button')
        read_more_button.click()
    except:
        pass  # Handle the case where the "Read more" button is not found
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    try:
        title = soup.find('h1', class_='mds-font-s6').text.strip()
    except:
        title = "NA"
    try:
        company = soup.find('dd', class_='mds-list__value').text.strip()
    except:
        company = "NA"
    try:
        closingdate = soup.find('dt', string='Closing date').find_next_sibling('dd').text.strip()
    except:
        closingdate = "NA"
    try:
        location = soup.find('dt', string='Location').find_next_sibling('dd').text.strip()
    except:
        location = "NA"
    try:
        salary = soup.find('dt', string='Salary').find_next_sibling('dd').text.strip()
    except:
        salary = "NA"
    try:
        script_tag = soup.find('script', {'type': 'application/ld+json'})
        json_data = json.loads(script_tag.contents[0])
        posting_date = json_data.get('datePosted').split('T')[0]
    except:
        posting_date = "NA"
    try:
        job_role = soup.find('dt', string='Job Role').find_next_sibling('dd').text.strip()
    except:
        job_role = "NA"
    try:
        sector = soup.find('dt', string='Sector').find_next_sibling('dd').text.strip()
    except:
        sector = "NA"
    try:
        contract_type = soup.find('dt', string='Contract Type').find_next_sibling('dd').text.strip()
    except:
        contract_type = "NA"
    try:
        hours = soup.find('dt', string='Hours').find_next_sibling('dd').text.strip()
    except:
        hours = "NA"
    try:
        desc = soup.find('div', class_='mds-surface__inner').text.strip()
    except:
        desc = "NA"

    jobPosting = {
        'SRC_Title': title,
        'SRC_Company': company,
        'Closingdate': closingdate,
        'SRC_Country': location,
        'Salary': salary,
        'Posting_date': posting_date,
        'Job_Link': job_link,
        'Job_Role': job_role,
        'SRC_Category': sector,
        'SRC_Type': contract_type,
        'SRC_Modality': hours,
        'SRC_Description': desc,
        'Website': 'Mycareer'
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
