# src/processing/financial_analyzer.py

import yaml
import json

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
    total_cost = budget.get('total_cost', 0)
    
    # --- Rule Check 1: Disallowed Items (with Normalization) ---
    print("Checking for disallowed items...")
    disallowed_rules = rules.get('disallowed_items', [])
    budget_items = budget.get('items', [])
    normalization_map = rules.get('normalization_map', {})
    
    # Normalize the budget items before checking
    normalized_budget_items = [normalization_map.get(item, item) for item in budget_items]
    
    found_disallowed = False
    for i, item in enumerate(normalized_budget_items):
        if item in disallowed_rules:
            original_item = budget_items[i] # Get the original term for the error message
            results.append({
                "rule": "Disallowed Item", "status": "FAIL",
                "message": f"Expense '{original_item}' (normalized to '{item}') is explicitly disallowed."
            })
            found_disallowed = True
            
    if not found_disallowed:
        results.append({"rule": "Disallowed Item", "status": "PASS", "message": "No disallowed items found."})

    # --- Rule Check 2: Contingency Percentage ---
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

    # --- Rule Check 3: Equipment Percentage ---
    print("Checking equipment cost limit...")
    equipment_limit = rules.get('cost_limits_percent', {}).get('equipment', 40)
    if total_cost > 0:
        equipment_percent = (equipment_cost / total_cost) * 100
        if equipment_percent > equipment_limit:
            results.append({"rule": "Equipment Cost Limit", "status": "FAIL", "message": f"Equipment cost is {equipment_percent:.1f}% of total, exceeding the {equipment_limit}% limit."})
        else:
            results.append({"rule": "Equipment Cost Limit", "status": "PASS", "message": "Equipment cost is within the limit."})

    return results

if __name__ == '__main__':
    financial_rules = load_rules()
    
    if financial_rules:
        # We will use the original budget with the "International Travel" term
        mock_proposal_budget = {
            "total_cost": 2500000,
            "costs": { "equipment": 1250000, "travel": 200000, "consumables": 600000, "contingency": 150000 },
            "items": [ "High-Performance Computer", "Specialized Sensors", "International Travel" ]
        }
        
        print("\n--- Analyzing Mock Proposal Budget with Normalization ---")
        analysis_report = analyze_budget(mock_proposal_budget, financial_rules)
        
        print("\n--- Financial Compliance Report ---")
        print(json.dumps(analysis_report, indent=4))