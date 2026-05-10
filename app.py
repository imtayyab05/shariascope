from flask import Flask, render_template, request, jsonify
from src.agents.screening_agent import run_screening
from src.parsers.company_parser import parse_company_input
from src.rules.aaoifi_rules import SHARIAH_RULES
import src.config.settings  # Triggers env loading and validation on startup
from src.parsers.auto_scraper import get_wikipedia_description, auto_collect_company_data

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/report', methods=['GET'])
def report_page():
    return render_template('report.html')

@app.route('/screen', methods=['POST'])
def screen():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON payload provided"}), 400
            
        company_name = data.get("company_name", "")
        
        # Use provided description, or auto-fetch if missing
        user_description = data.get("business_description", "").strip()
        if not user_description:
            description = get_wikipedia_description(company_name)
            data["business_description"] = description
            data["additional_notes"] = data.get("additional_notes", "") + " (Business description automatically sourced from Wikipedia.)"
        
        parsed_data = parse_company_input(data)
        report = run_screening(parsed_data, SHARIAH_RULES)
        
        return jsonify({
            "company_name": parsed_data.get("company_name"),
            "debt_to_assets": parsed_data.get("debt_to_assets"),
            "interest_income_to_revenue": parsed_data.get("interest_income_to_revenue"),
            "missing_fields": parsed_data.get("missing_fields"),
            "report": report
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/auto', methods=['GET'])
def auto_page():
    return render_template('index.html')

@app.route('/auto-screen', methods=['POST'])
def auto_screen():
    try:
        data = request.get_json()
        if not data or not data.get("company_name"):
            return jsonify({"error": "company_name is required"}), 400
            
        company_name = data.get("company_name")
        
        # 1. Call auto_collect
        auto_data = auto_collect_company_data(company_name)
        
        # 2. Pass through parse_company_input
        parsed_data = parse_company_input(auto_data)
        
        # 3. Run screening
        report = run_screening(parsed_data, SHARIAH_RULES)
        
        # 4. Return JSON
        return jsonify({
            "company_name": parsed_data.get("company_name"),
            "debt_to_assets": parsed_data.get("debt_to_assets"),
            "interest_income_to_revenue": parsed_data.get("interest_income_to_revenue"),
            "missing_fields": parsed_data.get("missing_fields"),
            "report": report,
            "data_confidence": auto_data.get("data_confidence"),
            "auto_collected_fields": auto_data.get("additional_notes")
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(debug=True)
