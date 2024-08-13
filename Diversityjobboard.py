import pandas as pd  
from bs4 import BeautifulSoup  
from selenium import webdriver  
import time  
import random  
from selenium.webdriver.common.by import By  
from selenium.webdriver.support.ui import WebDriverWait  
from selenium.webdriver.support import expected_conditions as EC  

def get_job_links():  
    job_links = []  
    driver = webdriver.Chrome()  # Configure path if necessary  
    driver.get("https://www.diversityjobboard.com/jobs")  
    time.sleep(5)  # Wait for the page to load  
    base_url = "https://www.diversityjobboard.com"  
    
    try:  
        while True:  
            WebDriverWait(driver, 30).until(  
                EC.presence_of_element_located((By.CSS_SELECTOR, ".job-listings-item"))  
            )  
            soup = BeautifulSoup(driver.page_source, 'html.parser')  
            listings = soup.find_all("div", class_="job-listings-item")  

            # Check if any listings found  
            if not listings:  
                print("No job listings found on this page.")  
                break  
            
            # Collect job links from the current page  
            for listing in listings:  
                job_link = listing.find("a")['href']  
                if job_link:  
                    # Convert to absolute URL if it's a relative link  
                    if job_link.startswith('/'):  
                        job_link = base_url + job_link  
                    job_links.append(job_link)  
                    print(f"Found job link: {job_link}")  # Debug print  

            # Attempt to load more jobs if the "Load More" button is present  
            try:  
                load_more_button = driver.find_element(By.CSS_SELECTOR, "button.load-more")  # Adjust the selector as needed  
                if load_more_button.is_displayed() and load_more_button.is_enabled():  
                    load_more_button.click()  # Click to load more jobs  
                    print("Loading more job listings...")  
                    time.sleep(random.uniform(2, 5))  # Random sleep to mimic human behavior  
                else:  
                    print("No more jobs to load.")  
            except Exception as e:  
                print("No Load More button found or an error occurred:", e)  
                break  # If no more load action can be performed, we can exit the loop  

            # Check for the presence of the "Next" button and click it if found  
            try:  
                next_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Next']")  
                if "disabled" in next_button.get_attribute('class'):  
                    print("Reached the last page, no more job listings.")  
                    break  
                next_button.click()  # Click the next button to go to the next page  
                time.sleep(random.uniform(2, 5))  # Random sleep to mimic human behavior  
                print("Going to next page...")  # Debug print  
            except Exception as e:  
                print("No next button found or an error occurred:", e)  
                break  # If no next button found, break from the loop  

    except Exception as e:   
        print(f"An error occurred while getting job links: {e}")  
    finally:  
        driver.quit()  

    return job_links  


def construct_job(driver, job_link):  
    if not job_link or not job_link.startswith(('http://', 'https://')):  
        print(f"Invalid job link: {job_link}")  
        return None  # Early exit for invalid URLs  

    driver.get(job_link)  
    WebDriverWait(driver, 30).until(  
        EC.presence_of_element_located((By.CLASS_NAME, "job-inner-title"))  
    )  
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')  
    title = soup.find("h1", class_="job-inner-title").text.strip() if soup.find("h1", class_="job-inner-title") else "NA"  
    
    description = soup.find(id='quill-container-with-job-details').text.replace('\n', '').strip() if soup.find(id='quill-container-with-job-details') else "NA"  
    
    info_items = soup.findAll("a", class_='job-inner-info-item')  
    company_name = info_items[0].text.strip() if len(info_items) > 0 else "NA"  
    job_type = info_items[1].text.strip() if len(info_items) > 1 else "NA"  
    location = info_items[2].text.strip() if len(info_items) > 2 else "NA"  
    
    info_ = soup.findAll("span", class_='job-inner-info-item')  
    salary = None  
    date_posted = None  
    for item in info_:  
        text = item.text.strip()  
        if "$" in text or "per year" in text:  
            salary = text  
        elif "ago" in text or any(char.isdigit() for char in text):  
            date_posted = text  

    jobposting = {  
        "SRC_Title": title,  
        "SRC_Description": description,  
        "SRC_Country": location,    
        "job_type": job_type,  
        "SRC_Company": company_name,  
        "Link": job_link,   
        "Salary": salary,  
        "Date Posted": date_posted,   
        "Website": "DiversityJobBoard"  
    }  

    return jobposting  

def save_to_excel(job_data):  
    if job_data:  
        df = pd.DataFrame(job_data)  
        df.to_excel("DiversityJobBoard.xlsx", index=False)  
        print("Data saved to Excel.")  
    else:  
        print("No job data to save.")  

def main():  
    job_links = get_job_links()  
    if not job_links:  
        print("No job links were found. Exiting.")  
        return  

    driver = webdriver.Chrome()  
    job_data = []  
    for link in job_links:  
        job_posting = construct_job(driver, link)  
        if job_posting:  
            job_data.append(job_posting)  

    driver.quit()  
    save_to_excel(job_data)  

if __name__ == "__main__":  
    main()



