SHARIAH_RULES = {
    "source": "AAOIFI Shariah Standard No. 21 — Financial Papers and MSCI Islamic Index Methodology",
    "prohibited_activities": {
        "list": [
            "alcohol", "tobacco", "pork", "conventional banking", 
            "conventional insurance", "gambling", "weapons manufacturing", 
            "pornography", "adult entertainment"
        ],
        "description": "A company whose primary business involves any of these is immediately non-compliant regardless of financial ratios. If a prohibited activity is a minor secondary revenue stream, it is flagged but assessed against a tolerance threshold rather than automatic failure."
    },
    "ambiguous_activities": {
        "list": [
            "financial services", "lending", "insurance", "streaming", 
            "advertising", "pharmaceuticals", "cryptocurrency", "defense", 
            "hospitality"
        ],
        "description": "These are not automatically prohibited but require deeper AI reasoning about the nature of the activity in context."
    },
    "financial_thresholds": {
        "debt_to_assets": {
            "maximum": 0.33,
            "description": "Total interest-bearing debt must not exceed 33% of total assets per AAOIFI Standard 21."
        },
        "interest_income_to_revenue": {
            "maximum": 0.05,
            "description": "Income from interest or prohibited sources must not exceed 5% of total revenue. Any amount must be purified by donating that proportion of dividends to charity."
        }
    },
    "exception_guidance": "If financial data is missing, the agent should reason about materiality based on industry — a retail company missing interest income is probably immaterial but a financial services company missing it should be treated conservatively."
}
