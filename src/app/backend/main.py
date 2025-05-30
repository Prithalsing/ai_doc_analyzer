#!/usr/bin/env python3
"""
Simple AI-Powered Documentation Improvement Agent
Analyzes MoEngage documentation and suggests improvements.
"""

import os
import time
import json
import sys
from datetime import datetime
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API not found in environment variables")

genai.configure(api_key=GEMINI_API_KEY)


def scrape_page(url):
    """
    Scrape content from a documentation page.
    
    Args:
        url (str): URL to scrape
        
    Returns:
        str: Extracted content
    """
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--no-sandbox')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        print(f"Scraping content from: {url}")
        driver.get(url)
        time.sleep(10)  # Wait for page load and Cloudflare
        
        # Wait for content to load
        wait = WebDriverWait(driver, 20)
        
        # Get all content elements
        elements = wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "h1, h2, h3, h4, h5, h6, p, ul, ol, pre, code, tr, th")
        ))
        
        # Extract and structure content
        content_parts = []
        for element in elements:
            text = element.text.strip()
            if text:
                tag = element.tag_name.lower()
                if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    content_parts.append(f"\n{text}\n")
                else:
                    content_parts.append(text)
        
        content = "\n\n".join(content_parts)
        
        if not content.strip():
            raise Exception("No content found on the page")
        
        print(f"Successfully extracted {len(content)} characters")
        return content
        
    except Exception as e:
        print(f"Error scraping page: {e}")
        raise
    finally:
        driver.quit()


def analyze_with_gemini(content, url):
    """Analyze content using Gemini AI and return structured results."""
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    prompt = f"""
Analyze this MoEngage documentation article and provide structured feedback.
Return only the JSON in exactly this format, with these exact keys and value types:
{{
  "readability": {{
    "score": "Good",  # Must be exactly one of: Excellent, Good, Fair, Poor
    "issues": ["issue 1", "issue 2"],  # List of strings
    "suggestions": ["suggestion 1", "suggestion 2"]  # List of strings
  }},
  "structure": {{
    "score": "Good",
    "issues": ["issue 1", "issue 2"],
    "suggestions": ["suggestion 1", "suggestion 2"]
  }},
  "completeness": {{
    "score": "Good",
    "issues": ["issue 1", "issue 2"],
    "suggestions": ["suggestion 1", "suggestion 2"]
  }},
  "style_guidelines": {{
    "score": "Good",
    "issues": ["issue 1", "issue 2"],
    "suggestions": ["suggestion 1", "suggestion 2"]
  }}
}}

Article URL: {url}
Content: {content}

Remember:
1. Return ONLY the JSON object
2. Scores must be exactly one of: Excellent, Good, Fair, Poor
3. Issues and suggestions must be lists of strings
4. Use the exact category names shown above
"""

    try:
        print("Analyzing content with Gemini...")
        response = model.generate_content(prompt)
        
        # Clean up response
        analysis_text = response.text.strip()
        if analysis_text.startswith('```json'):
            analysis_text = analysis_text[7:-3]
        elif analysis_text.startswith('```'):
            analysis_text = analysis_text[3:-3]
            
        # Validate JSON structure before returning
        analysis = json.loads(analysis_text)
        required_keys = ["readability", "structure", "completeness", "style_guidelines"]
        valid_scores = ["Excellent", "Good", "Fair", "Poor"]
        
        # Validate structure
        for key in required_keys:
            if key not in analysis:
                raise ValueError(f"Missing required category: {key}")
            category = analysis[key]
            if "score" not in category or category["score"] not in valid_scores:
                category["score"] = "Fair"  # Default if invalid
            if "issues" not in category or not isinstance(category["issues"], list):
                category["issues"] = []
            if "suggestions" not in category or not isinstance(category["suggestions"], list):
                category["suggestions"] = []
                
        return analysis
        
    except json.JSONDecodeError as e:
        print(f"Error parsing AI response: {e}")
        # Return a valid default structure
        return {
            cat: {
                "score": "Fair",
                "issues": ["Analysis failed to generate proper response"],
                "suggestions": ["Please try again"]
            } for cat in required_keys
        }
    except Exception as e:
        print(f"Error during analysis: {e}")
        raise


def revise_article_with_gemini(original_content, analysis):
    """
    Revise the article based on analysis suggestions.
    
    Args:
        original_content (str): Original article content
        analysis (dict): Analysis results with suggestions
        
    Returns:
        str: Revised article content
    """
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    # Convert analysis to readable format for the prompt
    suggestions_text = ""
    for category, data in analysis.items():
        suggestions_text += f"\n{category.title()} Issues:\n"
        for issue in data.get('issues', []):
            suggestions_text += f"- {issue}\n"
        suggestions_text += f"{category.title()} Suggestions:\n"
        for suggestion in data.get('suggestions', []):
            suggestions_text += f"- {suggestion}\n"
    
    prompt = f"""
Revise this MoEngage documentation article based on the analysis feedback.

Guidelines:
- Improve readability for non-technical marketers
- Simplify complex sentences and jargon
- Make tone more customer-focused and friendly
- Improve structure and flow
- Keep all technical information accurate
- Don't add new technical details

Original Article:
{original_content}

Improvements to Apply:
{suggestions_text}

Return the revised article content only.
"""

    try:
        print("Generating revised content...")
        response = model.generate_content(prompt)
        revised_content = response.text.strip()
        print("Revision completed successfully")
        return revised_content
        
    except Exception as e:
        print(f"Error during revision: {e}")
        raise


def calculate_overall_score(analysis):
    """Calculate overall score from individual category scores."""
    scores = []
    score_values = {'Excellent': 4, 'Good': 3, 'Fair': 2, 'Poor': 1}
    
    for category_data in analysis.values():
        score = category_data.get('score', 'Fair')
        if score in score_values:
            scores.append(score_values[score])
    
    if not scores:
        return "Unknown"
    
    avg = sum(scores) / len(scores)
    
    if avg >= 3.5:
        return "Excellent"
    elif avg >= 2.5:
        return "Good"
    elif avg >= 1.5:
        return "Fair"
    else:
        return "Poor"


def print_results(url, analysis, revised_content=None):
    """Print analysis results in a readable format."""
    print("\n" + "="*60)
    print("DOCUMENTATION ANALYSIS RESULTS")
    print("="*60)
    
    print(f"\nURL: {url}")
    print(f"Overall Score: {calculate_overall_score(analysis)}")
    print(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Print each category
    categories = ['readability', 'structure', 'completeness', 'style_guidelines']
    
    for category in categories:
        if category in analysis:
            data = analysis[category]
            print(f"\n{'-'*30}")
            print(f"{category.upper().replace('_', ' ')}")
            print(f"{'-'*30}")
            print(f"Score: {data.get('score', 'N/A')}")
            
            if data.get('issues'):
                print("\nIssues:")
                for i, issue in enumerate(data['issues'], 1):
                    print(f"  {i}. {issue}")
            
            if data.get('suggestions'):
                print("\nSuggestions:")
                for i, suggestion in enumerate(data['suggestions'], 1):
                    print(f"  {i}. {suggestion}")
    
    # Print revised content if available
    if revised_content:
        print(f"\n{'='*60}")
        print("REVISED CONTENT")
        print("="*60)
        print(revised_content)


def save_results(url, analysis, revised_content=None):
    """Save results to files."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save analysis as JSON
    result_data = {
        "url": url,
        "timestamp": datetime.now().isoformat(),
        "overall_score": calculate_overall_score(analysis),
        "analysis": analysis
    }
    
    json_file = f"analysis_{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nAnalysis saved to: {json_file}")
    
    # Save revised content if available
    if revised_content:
        content_file = f"revised_content_{timestamp}.txt"
        with open(content_file, 'w', encoding='utf-8') as f:
            f.write(revised_content)
        print(f"Revised content saved to: {content_file}")


def main():
    """Main function to run the documentation analyzer."""
    try:
        # Get URL from command line or user input
        if len(sys.argv) < 2:
            url = input("Enter the MoEngage documentation URL: ").strip()
            if not url:
                print("No URL provided. Exiting.")
                sys.exit(1)
        else:
            url = sys.argv[1]
        
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            print("Please provide a valid URL starting with http:// or https://")
            sys.exit(1)
        
        print("Starting documentation analysis...")
        print("This may take a few minutes...\n")
        
        # Step 1: Scrape content
        content = scrape_page(url)
        
        # Step 2: Analyze content
        analysis = analyze_with_gemini(content, url)
        
        # Step 3: Generate revised content
        revised_content = revise_article_with_gemini(content, analysis)
        
        # Step 4: Display and save results
        print_results(url, analysis, revised_content)
        save_results(url, analysis, revised_content)
        
        print("\n" + "="*60)
        print("ANALYSIS COMPLETED SUCCESSFULLY!")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()