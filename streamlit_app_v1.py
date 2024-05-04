import streamlit as st
import time
import pandas as pd
from datetime import datetime
import os
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

## Deploy streamlit app on streamlit server with selenium integration

#### https://github.com/andfanilo/s4a-selenium/tree/main

class RealDiscountUdemyCoursesCouponCodeScraper:
    def __init__(self):
        self.url = "https://www.real.discount/udemy-coupon-code/"
        # options = webdriver.FirefoxOptions()
        # options.add_argument("--headless")
        # self.driver = webdriver.Firefox(options=options)
        self.driver = None
        
        
    def load_webpage(self):
        # Deploy on streamlit server selenium integration
        firefoxOptions = Options()
        firefoxOptions.add_argument("--headless")
        service = Service(GeckoDriverManager().install())
        self.driver = webdriver.Firefox(
            options=firefoxOptions,
            service=service,
        )
        self.driver.implicitly_wait(5)
        self.driver.get(self.url)
        
    # Call the previous function before calling this function
    def scrape_coupons(self):
        
        try:
            # COUPONS DATA SCRAPED AND RETURNED
            COUPONS_DATA_AND_LABEL = []
            coupons_data_list_list = [] # declaration of list of courses data as list of list
            header = ["title","course","category","provider","duration","rating","language","students_enrolled","price_discounted","price_original","views"]
            courses_container = self.driver.find_element(By.CLASS_NAME, 'list-unstyled')
            courses = courses_container.find_elements(By.TAG_NAME, "a")
            for course in reversed(courses):
                if 'https://www.real.discount' not in course.get_attribute('href'):
                    continue  # Skip ad elements
                
                if 'https://www.real.discount/ads/' in course.get_attribute('href'):
                    continue # Skip ad elements
                coupon_data_list = []
                coupon_data_list.append(course.find_element(By.TAG_NAME, 'h3').text.strip())
                coupon_data_list.append(course.get_attribute('href'))
                coupon_data_list.append(course.find_element(By.TAG_NAME, 'h5').text.strip())
                coupon_data_list.append(course.find_element(By.CSS_SELECTOR, '.p-2:nth-child(1) .mt-1').text.strip())
                coupon_data_list.append(course.find_element(By.CSS_SELECTOR, '.p-2:nth-child(2) .mt-1').text.strip())
                coupon_data_list.append(course.find_element(By.CSS_SELECTOR, '.p-2:nth-child(3) .mt-1').text.strip())
                coupon_data_list.append(course.find_element(By.CSS_SELECTOR, '.p-2:nth-child(4) .mt-1').text.strip())
                coupon_data_list.append(course.find_element(By.CSS_SELECTOR, '.p-2:nth-child(5) .mt-1').text.strip())
                coupon_data_list.append(course.find_element(By.TAG_NAME, 'span').text.strip())
                coupon_data_list.append(course.find_element(By.CLASS_NAME, 'card-price-full').text.strip())
                coupon_data_list.append(course.find_element(By.CSS_SELECTOR, '.p-2:nth-child(7) .ml-1').text.strip())
                coupons_data_list_list.append(coupon_data_list)
            
            COUPONS_DATA_AND_LABEL = [header, coupons_data_list_list] # Data i need to convert to dataframe for comparison and saving
            
            return COUPONS_DATA_AND_LABEL
        
        
        except NoSuchElementException:
            return None

    def close_driver(self):
        self.driver.quit()

def main():
    st.title('Real-Time Udemy Course Discounts Scraper')
    st.text("Automatically scraping available Udemy course discounts from Real.Discount")
    
    scraper = RealDiscountUdemyCoursesCouponCodeScraper()
    
    while True:
        scraper.load_webpage()
        scraped_data = scraper.scrape_coupons()
        if scraped_data:
            header, new_courses = scraped_data
            display_new_courses(header, new_courses)
        else:
            st.write("No coupons found at the moment.")
            
        scraper.close_driver()
        # Sleep for 1 hour before scraping again
        time.sleep(300)  # 5*60 = 5 minutes
    
    scraper.close_driver()


def display_new_courses(header, new_courses):
    try:
        existing_courses = pd.read_csv(get_today_csv_filename(), header=0).iloc[:, 1].tolist()

        # print(existing_courses)
    except FileNotFoundError:
        existing_courses = []
    
    new_courses = [course for course in new_courses if course[1] not in existing_courses]
    if new_courses:
        save_to_csv(new_courses,header)
        st.write("Available New Udemy Course Coupons:")
        df = pd.DataFrame(new_courses, columns=header)
        st.write(df)


def save_to_csv(new_courses, header):
    filename = get_today_csv_filename()
    
    # Check if the file exists
    if not os.path.isfile(filename):
        # If the file doesn't exist, write the header
        df = pd.DataFrame(columns=header)  # Create an empty DataFrame with the header
        df.to_csv(filename, index=False)   # Write the header to the CSV file
    
    # Append the new data without the header
    df = pd.DataFrame(new_courses, columns=header)
    df.to_csv(filename, mode='a', header=False, index=False)


def get_today_csv_filename():
    today = datetime.now().strftime("%Y-%m-%d")
    return f"coupon_courses_{today}.csv"


if __name__ == "__main__":
    main()
 