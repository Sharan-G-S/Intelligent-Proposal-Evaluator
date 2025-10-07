# src/processing/financial_analyzer.py

import yaml
import json
from datetime import datetime

def load_rules(filepath='financial_rules.yaml'):
    """Loads the financial rules from the YAML file."""
    try:
        with open(filepath, 'r') as f:
            rules = yaml.safe_load(f)
        print("Successfully loaded financial rules.")
        return rules
    except FileNotFoundError:
        print(f"Error: Rules file not found at {filepath}")
        return None

def analyze_budget(budget: dict, rules: dict) -> list:
    """
    Analyzes a project budget against a set of rules and returns a list of compliance results.
    """
    results = []
    # ... (The logic of this function is the same, so it's omitted for brevity) ...
    total_cost = budget.get('total_cost', 0)
    print("Checking for disallowed items...")
    disallowed_rules = rules.get('disallowed_items', [])
    budget_items = budget.get('items', [])
    normalization_map = rules.get('normalization_map', {})
    normalized_budget_items = [normalization_map.get(item, item) for item in budget_items]
    found_disallowed = False
    for i, item in enumerate(normalized_budget_items):
        if item in disallowed_rules:
            original_item = budget_items[i]
            results.append({"rule": "Disallowed Item", "status": "FAIL", "message": f"Expense '{original_item}' (normalized to '{item}') is explicitly disallowed."})
            found_disallowed = True
    if not found_disallowed:
        results.append({"rule": "Disallowed Item", "status": "PASS", "message": "No disallowed items found."})
    print("Checking contingency cost limit...")
    contingency_limit = rules.get('cost_limits_percent', {}).get('contingency_of_revenue', 5)
    contingency_cost = budget.get('costs', {}).get('contingency', 0)
    equipment_cost = budget.get('costs', {}).get('equipment', 0)
    revenue_cost = total_cost - equipment_cost
    if revenue_cost > 0:
        contingency_percent = (contingency_cost / revenue_cost) * 100
        if contingency_percent > contingency_limit:
            results.append({"rule": "Contingency Limit", "status": "FAIL", "message": f"Contingency cost is {contingency_percent:.1f}% of revenue, exceeding the {contingency_limit}% limit."})
        else:
            results.append({"rule": "Contingency Limit", "status": "PASS", "message": "Contingency cost is within the limit."})
    print("Checking equipment cost limit...")
    equipment_limit = rules.get('cost_limits_percent', {}).get('equipment', 40)
    if total_cost > 0:
        equipment_percent = (equipment_cost / total_cost) * 100
        if equipment_percent > equipment_limit:
            results.append({"rule": "Equipment Cost Limit", "status": "FAIL", "message": f"Equipment cost is {equipment_percent:.1f}% of total, exceeding the {equipment_limit}% limit."})
        else:
            results.append({"rule": "Equipment Cost Limit", "status": "PASS", "message": "Equipment cost is within the limit."})
    return results

def log_report_to_file(report_data: list, proposal_filename: str, log_path: str = "financial_audit_log.txt"):
    """Appends a formatted report of the analysis to a text log file."""
    
    # Get the current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 'a' mode opens the file for appending. If the file doesn't exist, it's created.
    with open(log_path, 'a') as f:
        f.write("==================================================\n")
        f.write(f"Log Entry: {timestamp}\n")
        f.write(f"Analyzed File: {proposal_filename}\n")
        f.write("--------------------------------------------------\n")
        
        overall_status = "PASS"
        for item in report_data:
            f.write(f"[{item['status']}] Rule: {item['rule']}\n")
            f.write(f"       Details: {item['message']}\n")
            if item['status'] == 'FAIL':
                overall_status = "FAIL"
        
        f.write("--------------------------------------------------\n")
        f.write(f"Overall Compliance Status: {overall_status}\n")
        f.write("==================================================\n\n")

    print(f"Report has been appended to {log_path}")

# --- Main block for testing the analyzer and logging the report ---
if __name__ == '__main__':
    financial_rules = load_rules()
    
    if financial_rules:
        mock_proposal_budget = {
            "filename": "Test_Proposal__Finance_Check.docx",
            "total_cost": 2500000,
            "costs": { "equipment": 1250000, "travel": 200000, "consumables": 600000, "contingency": 150000 },
            "items": [ "High-Performance Computer", "Specialized Sensors", "International Travel" ]
        }
        
        print("\n--- Analyzing Mock Proposal Budget ---")
        analysis_report = analyze_budget(mock_proposal_budget, financial_rules)
        
        # --- Log the report to our text file ---
        log_report_to_file(analysis_report, mock_proposal_budget["filename"])