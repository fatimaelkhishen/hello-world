from bs4 import BeautifulSoup  
from selenium.webdriver.common.by import By  
from selenium.webdriver.support.ui import WebDriverWait  
from selenium.webdriver.support import expected_conditions as EC   
from selenium.common.exceptions import TimeoutException  
from selenium import webdriver  
import pandas as pd  
import time  

def get_job_links(max_pages=10):  
    job_links = []   
    driver = webdriver.Chrome()  
    base_url = "https://www.flexjobs.com"  
    p = 1  

    try:  
        while p <= max_pages:  
            url = f"{base_url}/search?joblocations=united%20states&usecLocation=true&Loc.LatLng=0%2C0&Loc.Radius=30&page={p}"  
            driver.get(url)  
            print(f"Accessing: {url}")  
            time.sleep(5)  

            try:  
                WebDriverWait(driver, 30).until(  
                    EC.presence_of_element_located((By.CLASS_NAME, "sc-14nyru2-2"))  
                )  
            except TimeoutException:  
                print(f"Timeout while waiting for page {p} to load. Exiting.")  
                break  

            soup = BeautifulSoup(driver.page_source, 'html.parser')  
            listings = soup.find_all("div", class_="sc-14nyru2-2")  

            if not listings:   
                print("No listings found; exiting.")  
                break  

            for listing in listings:  
                job_link_tag = listing.find('a', id=lambda x: x and x.startswith('job-name-'))  
                if job_link_tag and 'href' in job_link_tag.attrs:  
                    job_link = base_url + job_link_tag['href']  
                    job_links.append(job_link)  
             
            p += 1  

    finally:  
        driver.quit()  

    return job_links  

def construct_job(driver, job_link):  
    driver.get(job_link)  
    soup = BeautifulSoup(driver.page_source, 'html.parser')  

    try:  
        title = soup.find('h1', class_="sc-3znpb9-4 gHEvIB").text.strip()  
    except:  
        title = "NA"  
        
    # Extract job type  
    try:  
        job_type_elem = soup.find('li', class_='sc-x3l9np-2')  
        job_type = None  
        if job_type_elem:  
            job_type_value = job_type_elem.find('p', class_='sc-x3l9np-4')  
            if job_type_value:  
                job_type = job_type_value.text.strip()  
    except:  
        job_type = "NA"  
        
    try:  
        datePosted = soup.find('span', class_="sc-3znpb9-18 kKHHkJ").text.strip()  
    except:  
        datePosted = "NA"  
        
    try:  
        location = soup.find('div', class_="sc-x3l9np-14 kDfsCI").text.strip()  
    except:  
        location = "NA"  
        
    jobPosting = {  
        'SRC_Title': title,  
        'SRC_Country': location,  
        'Posting_Date': datePosted,  
        'Job_Type': job_type,  
        'Link': job_link  
    }  
    
    return jobPosting  

def save_to_excel(job_data):  
    df = pd.DataFrame(job_data)  
    df.to_excel("flex.xlsx", index=False)  

def main():  
    job_links = get_job_links()  # Changed this to match the correct function name  
    driver = webdriver.Chrome()  
    job_data = []  
    
    try:  
        for link in job_links:  
            job_posting = construct_job(driver, link)  
            job_data.append(job_posting)  
    finally:  
        driver.quit()  
        
    save_to_excel(job_data)  

if __name__ == "__main__":  
    main()