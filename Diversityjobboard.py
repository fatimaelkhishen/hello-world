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
    
    driver = webdriver.Chrome()   
    driver.get("https://www.diversityjobboard.com/jobs")  
    time.sleep(5)   
    base_url = "https://www.diversityjobboard.com"  
    page_number = 1  
    
    try:  
        while True:  
                
            WebDriverWait(driver, 30).until(  
                EC.presence_of_element_located((By.CSS_SELECTOR, ".job-listings-item"))  
            )  
            soup = BeautifulSoup(driver.page_source, 'html.parser')  
            listings = soup.find_all("div", class_="job-listings-item")  

            
            if not listings:  
                print("No job listings found on this page.")  
                break  
            
              
            for listing in listings:  
                try:  
                    job_link = listing.find("a")['href']  
                    if job_link:  
                         
                        if job_link.startswith('/'):  
                            job_link = base_url + job_link  
                        job_links.append((job_link, page_number))    
                        print(f"Found job link on page {page_number}: {job_link}") 
                except Exception as e:  
                    print(f"Error extracting job link: {e}")  

             
            try:  
                next_button = WebDriverWait(driver, 10).until(  
                    EC.element_to_be_clickable((By.XPATH, "//a[@aria-label='Next' and not(@disabled)]"))  
                )  
                next_button.click()   
                time.sleep(random.uniform(2, 5)) 
                page_number += 1  
                print(f"Going to next page {page_number}...")   
            except Exception as e:  
                print("No next button found or an error occurred:", e)  
                break    

    except Exception as e:   
        print(f"An error occurred while getting job links: {e}")  
    finally:  
        driver.quit()  

    return job_links  

def construct_job(driver, job_link_page):  
    job_link, page_number = job_link_page  

    if not job_link or not job_link.startswith(('http://', 'https://')):  
        print(f"Invalid job link: {job_link}")  
        return None    

    driver.get(job_link)  
    WebDriverWait(driver, 30).until(  
        EC.presence_of_element_located((By.CLASS_NAME, "job-inner-title"))  
    )  
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')  
    
    jobposting = {  
        "SRC_Title": "NA",  
        "SRC_Description": "NA",  
        "SRC_Country": "NA",  
        "job_type": "NA",  
        "SRC_Company": "NA",  
        "Link": job_link,   
        "Salary": "NA",  
        "Date Posted": "NA",   
        "Website": "DiversityJobBoard"  
    }  

  
    try:  
        title = soup.find("h1", class_="job-inner-title")  
        if title:  
            jobposting["SRC_Title"] = title.text.strip()  
    except Exception as e:  
        print(f"Error extracting title: {e}")  

    try:  
        description = soup.find(id='quill-container-with-job-details')  
        if description:  
            jobposting["SRC_Description"] = description.text.replace('\n', '').strip()  
    except Exception as e:  
        print(f"Error extracting description: {e}")  

      
    try:  
        info_items = soup.findAll("a", class_='job-inner-info-item')  
        jobposting["SRC_Company"] = info_items[0].text.strip() if len(info_items) > 0 else "NA"  
        jobposting["job_type"] = info_items[1].text.strip() if len(info_items) > 1 else "NA"  
        jobposting["SRC_Country"] = info_items[2].text.strip() if len(info_items) > 2 else "NA"  
    except Exception as e:  
        print(f"Error extracting company, job type, or location: {e}")  

     
    try:  
        info_ = soup.findAll("span", class_='job-inner-info-item')  
        for item in info_:  
            text = item.text.strip()  
            if "$" in text or "per year" in text:  
                jobposting["Salary"] = text  
            elif "ago" in text or any(char.isdigit() for char in text):  
                jobposting["Date Posted"] = text  
    except Exception as e:  
        print(f"Error extracting salary or date posted: {e}")  

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
    for link_page in job_links:  
        job_posting = construct_job(driver, link_page)  
        if job_posting:  
            job_data.append(job_posting)  

    driver.quit()  
    save_to_excel(job_data)  

if __name__ == "__main__":  
    main()



