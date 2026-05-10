def parse_company_input(data: dict) -> dict:
    company_name = data.get("company_name", "")
    business_description = data.get("business_description", "")
    additional_notes = data.get("additional_notes", "")
    
    missing_fields_set = set()
    
    def parse_numeric(field_name):
        val = data.get(field_name)
        try:
            if val is None or str(val).strip() == "":
                missing_fields_set.add(field_name)
                return 0.0
            return float(val)
        except ValueError:
            missing_fields_set.add(field_name)
            return 0.0

    total_assets = parse_numeric("total_assets")
    total_debt = parse_numeric("total_debt")
    total_revenue = parse_numeric("total_revenue")
    interest_income = parse_numeric("interest_income")

    # Calculate debt_to_assets
    if total_assets == 0.0:
        debt_to_assets = None
        missing_fields_set.add("total_assets")
    else:
        debt_to_assets = total_debt / total_assets

    # Calculate interest_income_to_revenue
    if total_revenue == 0.0:
        interest_income_to_revenue = None
        missing_fields_set.add("total_revenue")
    else:
        interest_income_to_revenue = interest_income / total_revenue

    missing_fields = list(missing_fields_set)

    return {
        "company_name": company_name,
        "business_description": business_description,
        "total_assets": total_assets,
        "total_debt": total_debt,
        "total_revenue": total_revenue,
        "interest_income": interest_income,
        "additional_notes": additional_notes,
        "debt_to_assets": debt_to_assets,
        "interest_income_to_revenue": interest_income_to_revenue,
        "missing_fields": missing_fields
    }

def format_ratio_for_display(ratio) -> str:
    if ratio is None:
        return "Data Missing"
    return f"{ratio * 100:.1f}%"
