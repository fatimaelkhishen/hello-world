import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
import re

def get_job_links():
    job_links = []
    p = 0

    driver = webdriver.Chrome()
    while True:
        url = f"https://jobs.sap.com/go/SAP-Jobs-in-USA/883901/{p}"

        driver.get(url + "/?q=&sortColumn=referencedate&sortDirection=desc&scrollToTable=true")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        job_cards = soup.find_all("tr", class_="data-row")
        for job_card in job_cards:
            link = job_card.find('a').get('href')
            job_links.append("https://jobs.sap.com"+link)
        pagination_label_row = soup.find("div", class_="pagination-label-row")
        if pagination_label_row:
            pagination_label = pagination_label_row.find("span", class_="paginationLabel")
            if pagination_label:
                results_text = pagination_label.get_text()
                if "Results" in results_text:
                    results_numbers = list(map(int, re.findall(r'\d+', results_text)))
                    current_page_results, total_results = results_numbers[1], results_numbers[-1]
                    if current_page_results == total_results: 
                        break
  
        p += 25
    driver.quit()
    return job_links

def construct_job(driver, job_link):
    driver.get(job_link)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
   
    try:
        title = soup.find('h1', class_='text-black fw-bold display-5 text-break mb-3').text.strip()
    except:
        title = "NA"

    try:
        posted_date = soup.find('div', class_='joblayouttoken rtltextaligneligible displayDTM data-date col-xs-12 col-sm-6 col-md-12 same-height sap-font-72-Book').find('span', class_='rtltextaligneligible').text.strip()
    except:
        posted_date = "NA"

    try:
        work_area = soup.find('div', class_='joblayouttoken rtltextaligneligible displayDTM data-department col-xs-12 col-sm-6 col-md-12 same-height sap-font-72-Book').find('span', class_='rtltextaligneligible').text.strip()
    except:
        work_area = "NA"

    try:
        career_status = soup.find('div', class_='joblayouttoken rtltextaligneligible displayDTM data-customfield3 col-xs-12 col-sm-6 col-md-12 same-height sap-font-72-Book').find('span', class_='rtltextaligneligible').text.strip()
    except:
        career_status = "NA"

    try:
        employment_type = soup.find('div', class_='joblayouttoken rtltextaligneligible displayDTM data-shifttype col-xs-12 col-sm-6 col-md-12 same-height sap-font-72-Book').find('span', class_='rtltextaligneligible').text.strip()
    except:
        employment_type = "NA"
    try:
        expected_travel = soup.find('div', class_='joblayouttoken rtltextaligneligible displayDTM data-travel col-xs-12 col-sm-6 col-md-12 same-height sap-font-72-Book').find('span', class_='rtltextaligneligible').text.strip()
    except:
        expected_travel = "NA"

    try:
        location = soup.find('div', class_='joblayouttoken rtltextaligneligible displayDTM data-location col-xs-12 col-sm-6 col-md-12 same-height sap-font-72-Book').find('span', class_='rtltextaligneligible').text.strip()
    except:
        location = "NA"
    try:
        desc = soup.find('div', class_='joblayouttoken rtltextaligneligible displayDTM marginTopNone marginBottomNone marginRightNone marginLeftNone data-description').text.strip()
    except:
        desc = "NA"

    jobPosting = {
        'SRC_Title': title,
        'Area': work_area,
        'SRC_Country': location,
        'Posting_date': posted_date,
        'Job_Link': job_link,
        'Website': 'Sap',
        'expected_travel': expected_travel,
        'career_status': career_status,
        'SRC_Modality': employment_type,
        'SRC_Description': desc
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
# test_link = "https://jobs.sap.com/job/Chicago-Sr_-Client-Delivery-Manager-IL-60606/1075244401/"
# test_job = construct_job(webdriver.Chrome(), test_link)
# print(test_job)