import json
from openai import OpenAI
from src.config.settings import OPENAI_API_KEY
from src.parsers.company_parser import format_ratio_for_display

def build_prompt(parsed_data: dict, rules: dict) -> str:
    prompt = """You are an expert Shariah compliance analyst trained in AAOIFI and MSCI Islamic finance screening methodology. Reason carefully, be transparent about uncertainty, never make up financial data, and always use the numbers provided.

=== SHARIAH RULES ===
"""
    prompt += f"Source: {rules.get('source', '')}\n\n"
    
    prohib = rules.get('prohibited_activities', {})
    prompt += "--- Prohibited Activities ---\n"
    prompt += f"List: {', '.join(prohib.get('list', []))}\n"
    prompt += f"Description: {prohib.get('description', '')}\n\n"
    
    ambig = rules.get('ambiguous_activities', {})
    prompt += "--- Ambiguous Activities Requiring Reasoning ---\n"
    prompt += f"List: {', '.join(ambig.get('list', []))}\n"
    prompt += f"Description: {ambig.get('description', '')}\n\n"
    
    thresh = rules.get('financial_thresholds', {})
    prompt += "--- Financial Thresholds ---\n"
    d_to_a = thresh.get('debt_to_assets', {})
    prompt += f"Debt-to-Assets: Max {d_to_a.get('maximum', 0)} - {d_to_a.get('description', '')}\n"
    i_to_r = thresh.get('interest_income_to_revenue', {})
    prompt += f"Interest Income-to-Revenue: Max {i_to_r.get('maximum', 0)} - {i_to_r.get('description', '')}\n\n"
    
    prompt += "--- Exception Guidance ---\n"
    prompt += f"{rules.get('exception_guidance', '')}\n\n"
    
    prompt += "=== COMPANY DATA ===\n"
    prompt += f"Company Name: {parsed_data.get('company_name', 'N/A')}\n"
    prompt += f"Business Description (Automatically sourced from Wikipedia): {parsed_data.get('business_description', 'N/A')}\n"
    prompt += f"Total Assets: {parsed_data.get('total_assets', 'N/A')}\n"
    prompt += f"Total Debt: {parsed_data.get('total_debt', 'N/A')}\n"
    prompt += f"Total Revenue: {parsed_data.get('total_revenue', 'N/A')}\n"
    prompt += f"Interest Income: {parsed_data.get('interest_income', 'N/A')}\n"
    prompt += f"Calculated Debt-to-Assets Ratio: {format_ratio_for_display(parsed_data.get('debt_to_assets'))}\n"
    prompt += f"Calculated Interest Income Ratio: {format_ratio_for_display(parsed_data.get('interest_income_to_revenue'))}\n"
    prompt += f"Additional Notes: {parsed_data.get('additional_notes', 'N/A')}\n"
    
    missing_fields = parsed_data.get('missing_fields', [])
    prompt += f"Missing Fields: {', '.join(missing_fields) if missing_fields else 'None'}\n"
    if missing_fields:
        prompt += f"Note: The following data was not provided: {', '.join(missing_fields)}\n"
    prompt += "\n"
    
    prompt += """=== INSTRUCTIONS ===
You must follow these four reasoning steps:

STEP 1 - BUSINESS ACTIVITY REASONING: Analyze the business description carefully. Do not rely on keywords. Reason about what this company actually does and how every part of its business generates money. Identify any prohibited activities explicitly. For ambiguous activities explain your reasoning about whether they involve prohibited elements. Consider the additional notes for any recent changes to the business.

STEP 2 - FINANCIAL RATIO ANALYSIS: For each ratio state the calculated value, the threshold, whether it passes or fails, and what this means in plain terms. If a ratio is None due to missing data do not skip it. Instead reason about whether that missing field is likely to be significant given this company's industry and description. State your assumption clearly and give a probable assessment.

STEP 3 - EXCEPTION AND EDGE CASE HANDLING: Consider whether any exceptional circumstances apply. Examples: is the company's debt likely asset-backed rather than interest-bearing? Does a prohibited activity represent such a minor portion of revenue that it falls under tolerance thresholds? Are there any recent acquisitions or business model changes noted that affect compliance? Reason through these explicitly.

STEP 4 - FINAL VERDICT: Produce your structured output using exactly these section headers on their own lines in capitals:

OVERALL VERDICT
BUSINESS ACTIVITY ASSESSMENT  
FINANCIAL RATIO ANALYSIS
EXCEPTION HANDLING AND EDGE CASES
MISSING DATA ASSUMPTIONS
PLAIN LANGUAGE SUMMARY

OVERALL VERDICT must be exactly one of: COMPLIANT, NON-COMPLIANT, or NEEDS SCHOLAR REVIEW — nothing else on that line.

PLAIN LANGUAGE SUMMARY must be 3 to 4 sentences written for a non-expert Muslim investor with no finance or legal background."""

    return prompt

def run_screening(parsed_data: dict, rules: dict) -> str:
    prompt = build_prompt(parsed_data, rules)
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert Shariah compliance analyst. Be thorough, honest, and transparent in your reasoning."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"Failed to generate screening report via OpenAI API: {str(e)}")
