from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import re
import json
from bs4 import BeautifulSoup
import pandas as pd
import google.generativeai as genai
 
def scrape_website(url):
    """Scrapes a website and extracts relevant text content."""
    try:
        service = Service()
        driver = webdriver.Chrome(service=service)
        driver.get(url)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
 
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
 
        # Extract all text content, filter irrelevant parts
        all_text = [p.text for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']) if p.text.strip()]
        cleaned_text = [clean_text(text) for text in all_text if clean_text(text) and not is_irrelevant_text(text)]
 
        return "\n".join(cleaned_text)
 
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""
    finally:
        if 'driver' in locals() and driver:
            driver.quit()
 
def clean_text(text):
    """Cleans text by removing extra whitespace and non-printable characters."""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text).strip()
    text = ''.join(char for char in text if ord(char) >= 32)
    return text
 
def is_irrelevant_text(text):
    """Checks if text is likely irrelevant (e.g., ads, navigation)."""
    irrelevant_patterns = [
        r'advertisement',
        r'subscribe',
        r'privacy policy',
        r'cookie policy',
        r'navigation',
        r'menu',
        r'social media',
        r'contact us',
        r'legal',
        r'terms of use'
    ]
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in irrelevant_patterns)
 
def extract_website_details(text):
    """Extracts website details using Gemini AI."""
    genai.configure(api_key="AIzaSyBViF7tOANKLuft3aE8knTNybv8-KLNXAM")  # Replace with your actual API key
 
    model = genai.GenerativeModel('gemini-1.5-flash')  # Specify Gemini model
 
    questions = {
        "mission_statement": "What is the company's mission statement or core values?",
        "products_services": "What products or services does the company offer?",
        "company_founded": "When was the company founded, and who were the founders?",
        "headquarters_location": "Where is the company's headquarters located?",
        "key_executives": "Who are the key executives or leadership team members?",
        "awards_recognitions": "Has the company received any notable awards or recognitions?"
    }
 
    answers = {}
    for question_key, question_text in questions.items():
        prompt = f"Answer the following question based on the provided data:\n\nQuestion: {question_text}\n\nData:\n{text}"
        try:
            response = model.generate_content(prompt)
            answers[question_key] = response.text
        except Exception as e:
            answers[question_key] = f"Error: {e}"
    return answers
 
def save_to_excel(data, filename="website_data.xlsx"):
    """Saves the extracted details to an Excel file."""
    df = pd.DataFrame.from_dict(data, orient='index')
    df.reset_index(inplace=True)
    df.columns = ["Website", "Mission Statement", "Products/Services", "Founded", "Headquarters", "Executives", "Awards"]
   
    df.to_excel(filename, index=False, engine='openpyxl')
    print(f"Data saved to {filename}")
 
# Main execution
website_urls = [
    "https://www.snap.com",
    "https://www.dropbox.com",
    "https://www.tesla.com",
    "https://www.spacex.com",
    "https://robinhood.com",
    "https://stripe.com",
    "https://squareup.com",
    "https://www.shopify.com",
    "https://www.zara.com",
    "https://hmgroup.com"
]
 
website_data = {}
for url in website_urls:
    print(f"Processing {url}...")
    scraped_text = scrape_website(url)
    if scraped_text:
        details = extract_website_details(scraped_text)
        website_data[url] = details
 
# Save extracted data to an Excel file
save_to_excel(website_data)
 