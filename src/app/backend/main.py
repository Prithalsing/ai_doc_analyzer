import sys
import time
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import google.generativeai as genai

# Set your Gemini API Key
GEMINI_API_KEY = "AIzaSyB7x81BRsUcQwfMcnENs0NumkaaRPkY_gM"
genai.configure(api_key=GEMINI_API_KEY)

def scrape_page(url):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36')
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        time.sleep(10)  # Wait for Cloudflare
        wait = WebDriverWait(driver, 20)
        paragraphs = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "p")))
        content = "\n\n".join([p.text.strip() for p in paragraphs if p.text.strip()])
    finally:
        driver.quit()

    return content

def analyze_with_gemini(content, url):
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f"""
You are an AI assistant helping improve product documentation at MoEngage.

follow the basic 
1. dont give markdowns
2. always form a sentence in simpleway it shouldnt be complex
3. understand the {content} and then reply 
4. try to give ans in points and simple way
5. stricklty dont "\n" for going to the new line

Please analyze the following article from {url} and give feedback based on the guidelines below. Your feedback should be clear, actionable, and easy to understand for content writers and marketers.

**1. Readability for a Marketer**
- Evaluate how readable this article is for a non-technical marketer.
- You may use readability scores (e.g., Flesch-Kincaid, Gunning Fog), or use your own language understanding to assess it.
- Explain why the article is or isn’t easy to read for a marketer. Focus on tone, complexity, and word choice.

**2. Structure and Flow**
- Review the article’s structure: are the headings and subheadings clear and helpful?
- Are paragraphs too long or short? Are lists used effectively?
- Does the content flow logically from one section to another?
- Is it easy for someone to scan and find specific information?

**3. Completeness of Information & Examples**
- Does the article include enough detail for a user to understand and use the feature or concept?
- Are examples clear, relevant, and helpful?
- If examples are missing or weak, suggest where and how they can be added or improved.

**4. Adherence to Style Guidelines (Simplified)**
Follow these simplified style principles based on the Microsoft Style Guide:

- **Voice and Tone:** Is the writing customer-focused, clear, and friendly?
- **Clarity and Conciseness:** Are any sentences too complex or filled with jargon? Suggest simpler alternatives.
- **Action-oriented Language:** Does the article clearly guide the user on what to do?

Call out areas where the article does not follow these principles, and suggest how to improve them.

---

**Article Content:**
{content}
"""


    response = model.generate_content(prompt)
    return response.text

def revise_article_with_gemini(original_content, suggestions):
    """
    Second agent: Attempts to revise the article based on suggestions.
    Focus: Readability and simple stylistic changes.
    """
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = f"""
You are an AI assistant tasked with revising a documentation article.

Your goal is to automatically incorporate the following suggestions into the original article content. 
Focus on:
- Improving readability for non-technical marketers.
- Simplifying complex sentences and jargon.
- Making tone more customer-focused and friendly.
- Improving structure and flow if possible.

Do NOT add or remove technical details unless suggested.
Do NOT use markdown formatting.
Keep the revised article clear, concise, and actionable.

--- 
Original Article:
{original_content}

---
Suggestions to Apply:
{suggestions}

---
Revised Article (apply as many suggestions as possible):
"""
    response = model.generate_content(prompt)
    return response.text

def main():
    if len(sys.argv) < 2:
        url = input("Enter the documentation URL: ").strip()
        if not url:
            print("No URL provided. Exiting.")
            sys.exit(1)
    else:
        url = sys.argv[1]
    print(f"Scraping content from: {url}")
    content = scrape_page(url)

    print("\nAnalyzing with Gemini...\n")
    analysis = analyze_with_gemini(content, url)
    print(analysis)

    print("revised analysis \n")
    rev_analysis = revise_article_with_gemini(content, analysis)
    print(rev_analysis) 


if __name__ == "__main__":
    main()
