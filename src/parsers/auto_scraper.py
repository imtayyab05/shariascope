from duckduckgo_search import DDGS
import wikipedia
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import os
import json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_wikipedia_description(company_name):
    try:
        summary = wikipedia.summary(company_name, sentences=5)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        try:
            # Try first option from disambiguation
            summary = wikipedia.summary(e.options[0], sentences=5)
            return summary
        except:
            return ""
    except wikipedia.exceptions.PageError:
        try:
            # Try adding "company" to the name
            summary = wikipedia.summary(company_name + " company", sentences=5)
            return summary
        except:
            return ""
    except:
        return ""

def search_financial_snippets(company_name):
    try:
        query = f"{company_name} total assets revenue annual report financial results 2024"
        results_text = ""
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
        for r in results:
            results_text += f"Title: {r.get('title','')}\n"
            results_text += f"Content: {r.get('body','')}\n\n"
        return results_text if results_text else ""
    except:
        return ""

def extract_partial_financials(raw_text, company_name):
    default_fail = {
        "total_assets": 0,
        "total_debt": 0, 
        "total_revenue": 0,
        "interest_income": 0,
        "data_found": False,
        "confidence": "low",
        "notes": "Could not extract financial data from search results."
    }
    if not raw_text:
        return default_fail
        
    prompt = f"""From the following web search snippets about {company_name}, extract any financial figures you can find. These snippets are from general web search results so data may be incomplete or approximate. Return ONLY a valid JSON object with these keys:
- total_assets (full number, 0 if not found)
- total_debt (full number, 0 if not found)
- total_revenue (full number, 0 if not found)
- interest_income (full number, 0 if not found)
- data_found (true if you found at least revenue or assets, false otherwise)
- confidence (low, medium, or high)
- notes (one sentence on what you found and what is missing)

Convert abbreviated numbers: 1.2B = 1200000000, 383M = 383000000. Return only the JSON, no other text."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt},
                {"role": "user", "content": f"Raw Text:\n{raw_text}"}
            ],
            response_format={ "type": "json_object" },
            max_tokens=500
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        
        # ensure keys exist
        for key in default_fail.keys():
            if key not in data or data[key] is None:
                data[key] = default_fail[key]
                
        # ensure numeric
        for key in ["total_assets", "total_debt", "total_revenue", "interest_income"]:
            try:
                data[key] = float(data[key])
            except ValueError:
                data[key] = 0.0
                
        return data
    except:
        return default_fail

def auto_collect_company_data(company_name):
    # Get description from Wikipedia
    description = get_wikipedia_description(company_name)
    
    # Search for financial snippets via DuckDuckGo
    raw_snippets = search_financial_snippets(company_name)
    
    # Extract whatever numbers GPT-4o can find
    financials = extract_partial_financials(raw_snippets, company_name)
    
    # Build notes explaining what was found
    if financials["data_found"]:
        notes = (
            f"Business description sourced from Wikipedia. "
            f"Financial data partially extracted from web "
            f"search results — accuracy not guaranteed. "
            f"{financials['notes']} "
            f"For accurate screening use Manual Entry mode "
            f"with verified figures from annual reports."
        )
        confidence = financials["confidence"]
    else:
        notes = (
            f"Business description sourced from Wikipedia. "
            f"Financial data could not be extracted from "
            f"available search results. Figures shown as 0. "
            f"For complete screening please use Manual Entry "
            f"mode with figures from the company annual report."
        )
        confidence = "low"
    
    missing = []
    if financials["total_assets"] == 0: 
        missing.append("total_assets")
    if financials["total_revenue"] == 0: 
        missing.append("total_revenue")
    if financials["total_debt"] == 0: 
        missing.append("total_debt")
    
    return {
        "company_name": company_name,
        "business_description": description,
        "total_assets": financials["total_assets"],
        "total_debt": financials["total_debt"],
        "total_revenue": financials["total_revenue"],
        "interest_income": financials["interest_income"],
        "additional_notes": notes,
        "data_confidence": confidence,
        "missing_fields": missing
    }
