#!/usr/bin/env python3
"""
LangChain-Powered Documentation Improvement Agent
Analyzes MoEngage documentation and suggests improvements using LangChain.
"""

import os
import time
import json
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# LangChain imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from pydantic import BaseModel, Field
from langchain.chains import LLMChain

# Load environment variables
load_dotenv()

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API") or os.getenv("GOOGLE_API_KEY")
if not GEMINI_API_KEY:
    print("Error: Google Gemini API key not found!")
    sys.exit(1)


# Pydantic models for structured output
class CategoryAnalysis(BaseModel):
    """Analysis for a specific category."""
    score: str = Field(description="Score must be one of: Excellent, Good, Fair, Poor")
    issues: List[str] = Field(description="List of identified issues")
    suggestions: List[str] = Field(description="List of improvement suggestions")


class DocumentationAnalysis(BaseModel):
    """Complete documentation analysis structure."""
    readability: CategoryAnalysis = Field(description="Readability analysis")
    structure: CategoryAnalysis = Field(description="Structure analysis")
    completeness: CategoryAnalysis = Field(description="Completeness analysis")
    style_guidelines: CategoryAnalysis = Field(description="Style guidelines analysis")


class DocumentationAnalyzer:
    """Main class for analyzing documentation using LangChain."""
    
    def __init__(self):
        """Initialize the analyzer with LangChain components."""
        # Initialize the LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=GEMINI_API_KEY,
        )
        
        # Initialize parsers
        self.json_parser = JsonOutputParser(pydantic_object=DocumentationAnalysis)
        self.str_parser = StrOutputParser()
        
        # Create analysis prompt template
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert technical writer analyzing MoEngage documentation. 
            Analyze the provided content and return structured feedback in the exact JSON format specified.
            
            Focus on:
            - Readability for non-technical marketers
            - Clear structure and organization
            - Completeness of information
            - Adherence to documentation style guidelines
            
            {format_instructions}"""),
            ("human", """
            Article URL: {url}
            
            Content to analyze:
            {content}
            
            Provide detailed analysis with specific, actionable feedback for each category.
            """)
        ])
        
        # Create revision prompt template
        self.revision_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert technical writer specializing in customer-facing documentation.
            Revise the provided article based on the analysis feedback to make it more user-friendly.
            
            Guidelines:
            - Improve readability for non-technical marketers
            - Simplify complex sentences and jargon
            - Make tone more customer-focused and friendly
            - Improve structure and flow
            - Keep all technical information accurate
            - Don't add new technical details"""),
            ("human", """
            Original Article:
            {original_content}
            
            Analysis Feedback:
            {feedback}
            
            Return only the revised article content.
            """)
        ])
        
        # Create chains
        self.analysis_chain = self.analysis_prompt | self.llm | self.json_parser
        self.revision_chain = self.revision_prompt | self.llm | self.str_parser

    def scrape_page(self, url: str) -> str:
        """
        Scrape content from a documentation page with robust error handling.
        
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
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        driver = webdriver.Chrome(options=options)
        
        try:
            print(f"Scraping content from: {url}")
            driver.get(url)
            
            # Execute script to disable automation detection
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Wait longer for dynamic content
            print("Waiting for page to load completely...")
            time.sleep(15)
            
            # Try multiple strategies to get content
            content_parts = []
            
            # Strategy 1: Try to get main content area first
            main_selectors = [
                "main", ".main-content", "#main-content", 
                ".article-content", ".content", ".post-content",
                ".entry-content", "[role='main']"
            ]
            
            main_content_found = False
            for selector in main_selectors:
                try:
                    main_element = driver.find_element(By.CSS_SELECTOR, selector)
                    if main_element and main_element.text.strip():
                        print(f"Found main content using selector: {selector}")
                        # Get all text content from main area
                        elements = main_element.find_elements(By.CSS_SELECTOR, "h1, h2, h3, h4, h5, h6, p, ul, ol, li, pre, code, div")
                        for element in elements:
                            try:
                                text = element.text.strip()
                                if text and len(text) > 10:  # Filter out very short text
                                    tag = element.tag_name.lower()
                                    if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                                        content_parts.append(f"\n{'#' * int(tag[1])} {text}\n")
                                    else:
                                        content_parts.append(text)
                            except Exception:
                                continue
                        main_content_found = True
                        break
                except Exception:
                    continue
            
            # Strategy 2: If main content not found, try body content
            if not main_content_found:
                print("Main content not found, trying body content...")
                try:
                    # Wait for any content to be present
                    wait = WebDriverWait(driver, 30)
                    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                    
                    # Get page source and extract text using JavaScript
                    content_text = driver.execute_script("""
                        // Remove script and style elements
                        var scripts = document.querySelectorAll('script, style, nav, footer, header, .nav, .footer, .header');
                        scripts.forEach(function(el) { el.remove(); });
                        
                        // Get main content
                        var mainContent = document.querySelector('main, .main-content, #main-content, .article-content, .content') || document.body;
                        return mainContent.innerText || mainContent.textContent || '';
                    """)
                    
                    if content_text and len(content_text.strip()) > 100:
                        content_parts = [content_text.strip()]
                    else:
                        # Fallback: get visible text from body
                        body_text = driver.find_element(By.TAG_NAME, "body").text
                        if body_text:
                            content_parts = [body_text.strip()]
                        
                except Exception as e:
                    print(f"Error with body content extraction: {e}")
            
            # Strategy 3: Last resort - get all text content
            if not content_parts:
                print("Trying fallback content extraction...")
                try:
                    all_text = driver.execute_script("return document.body.innerText || document.body.textContent || '';")
                    if all_text and len(all_text.strip()) > 50:
                        content_parts = [all_text.strip()]
                except Exception:
                    pass
            
            # Combine all content
            if content_parts:
                content = "\n\n".join(content_parts)
                # Clean up the content
                lines = content.split('\n')
                cleaned_lines = []
                for line in lines:
                    line = line.strip()
                    if line and len(line) > 3:  # Filter out very short lines
                        cleaned_lines.append(line)
                
                content = "\n".join(cleaned_lines)
                
                if len(content.strip()) > 100:
                    print(f"Successfully extracted {len(content)} characters")
                    return content
            
            raise Exception("No substantial content found on the page")
            
        except Exception as e:
            print(f"Error scraping page: {e}")
            # Try one more time with a different approach
            try:
                print("Attempting alternative scraping method...")
                time.sleep(5)
                page_source = driver.page_source
                if page_source and len(page_source) > 1000:
                    # Use BeautifulSoup-like approach with Selenium
                    text_content = driver.execute_script("""
                        var walker = document.createTreeWalker(
                            document.body,
                            NodeFilter.SHOW_TEXT,
                            null,
                            false
                        );
                        var textNodes = [];
                        var node;
                        while(node = walker.nextNode()) {
                            if(node.nodeValue.trim().length > 10) {
                                textNodes.push(node.nodeValue.trim());
                            }
                        }
                        return textNodes.join(' ');
                    """)
                    
                    if text_content and len(text_content.strip()) > 100:
                        print(f"Alternative method extracted {len(text_content)} characters")
                        return text_content.strip()
            except Exception as fallback_error:
                print(f"Alternative method also failed: {fallback_error}")
            
            raise Exception(f"All scraping methods failed. Original error: {e}")
        finally:
            try:
                driver.quit()
            except Exception:
                pass

    def analyze_content(self, content: str, url: str) -> Dict[str, Any]:
        """
        Analyze content using LangChain and return structured results.
        
        Args:
            content (str): Content to analyze
            url (str): URL of the content
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        try:
            print("Analyzing content with LangChain + Gemini...")
            
            # Get format instructions from the parser
            format_instructions = self.json_parser.get_format_instructions()
            
            # Invoke the analysis chain
            result = self.analysis_chain.invoke({
                "content": content,
                "url": url,
                "format_instructions": format_instructions
            })
            
            # Convert Pydantic model to dict for compatibility
            if hasattr(result, 'dict'):
                analysis_dict = result.dict()
            else:
                analysis_dict = result
                
            print("Analysis completed successfully")
            return analysis_dict
            
        except Exception as e:
            print(f"Error during analysis: {e}")
            # Return a valid default structure
            categories = ["readability", "structure", "completeness", "style_guidelines"]
            return {
                cat: {
                    "score": "Fair",
                    "issues": ["Analysis failed to generate proper response"],
                    "suggestions": ["Please try again"]
                } for cat in categories
            }

    def revise_content(self, original_content: str, analysis: Dict[str, Any]) -> str:
        """
        Revise the article based on analysis suggestions using LangChain.
        
        Args:
            original_content (str): Original article content
            analysis (Dict[str, Any]): Analysis results
            
        Returns:
            str: Revised content
        """
        try:
            print("Generating revised content with LangChain...")
            
            # Format analysis feedback for the prompt
            feedback_parts = []
            for category, data in analysis.items():
                feedback_parts.append(f"\n{category.title().replace('_', ' ')} Analysis:")
                feedback_parts.append(f"Score: {data.get('score', 'N/A')}")
                
                if data.get('issues'):
                    feedback_parts.append("Issues:")
                    for issue in data['issues']:
                        feedback_parts.append(f"- {issue}")
                
                if data.get('suggestions'):
                    feedback_parts.append("Suggestions:")
                    for suggestion in data['suggestions']:
                        feedback_parts.append(f"- {suggestion}")
            
            feedback_text = "\n".join(feedback_parts)
            
            # Invoke the revision chain
            revised_content = self.revision_chain.invoke({
                "original_content": original_content,
                "feedback": feedback_text
            })
            
            print("Revision completed successfully")
            return revised_content
            
        except Exception as e:
            print(f"Error during revision: {e}")
            raise

    def calculate_overall_score(self, analysis: Dict[str, Any]) -> str:
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

    def print_results(self, url: str, analysis: Dict[str, Any], revised_content: Optional[str] = None):
        """Print analysis results in a readable format."""
        print("\n" + "="*60)
        print("DOCUMENTATION ANALYSIS RESULTS")
        print("="*60)
        
        print(f"\nURL: {url}")
        print(f"Overall Score: {self.calculate_overall_score(analysis)}")
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

    def save_results(self, url: str, analysis: Dict[str, Any], revised_content: Optional[str] = None):
        """Save results to files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save analysis as JSON
        result_data = {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "overall_score": self.calculate_overall_score(analysis),
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

    def analyze_documentation(self, url: str) -> tuple[Dict[str, Any], str]:
        """
        Main method to analyze documentation.
        
        Args:
            url (str): URL to analyze
            
        Returns:
            tuple: (analysis_results, revised_content)
        """
        # Step 1: Scrape content
        content = self.scrape_page(url)
        
        # Step 2: Analyze content
        analysis = self.analyze_content(content, url)
        
        # Step 3: Generate revised content
        revised_content = self.revise_content(content, analysis)
        
        return analysis, revised_content


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
        
        print("Starting LangChain-powered documentation analysis...")
        print("This may take a few minutes...\n")
        
        # Initialize analyzer
        analyzer = DocumentationAnalyzer()
        
        # Run analysis
        analysis, revised_content = analyzer.analyze_documentation(url)
        
        # Display and save results
        analyzer.print_results(url, analysis, revised_content)
        analyzer.save_results(url, analysis, revised_content)
        
        print("\n" + "="*60)
        print("LANGCHAIN ANALYSIS COMPLETED SUCCESSFULLY!")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()