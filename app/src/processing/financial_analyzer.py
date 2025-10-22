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

def analyze_budget(budget: dict, rules: dict) -> dict:
    """
    Enhanced financial analysis with detailed budget breakdown and recommendations.
    """
    results = []
    total_cost = budget.get('total_cost', 0)
    costs = budget.get('costs', {})
    
    # Detailed cost breakdown
    equipment_cost = costs.get('equipment', 0)
    travel_cost = costs.get('travel', 0) + costs.get('domestic_travel', 0) + costs.get('international_travel', 0)
    consumables_cost = costs.get('consumables', 0) + costs.get('materials', 0)
    contingency_cost = costs.get('contingency', 0)
    personnel_cost = costs.get('personnel', 0) + costs.get('salary', 0)
    overhead_cost = costs.get('overhead', 0) + costs.get('administrative', 0)
    
    # Calculate percentages
    equipment_percent = (equipment_cost / total_cost * 100) if total_cost > 0 else 0
    travel_percent = (travel_cost / total_cost * 100) if total_cost > 0 else 0
    contingency_percent = (contingency_cost / total_cost * 100) if total_cost > 0 else 0
    
    # Cost category analysis
    cost_breakdown = {
        "total_budget": total_cost,
        "equipment": {"amount": equipment_cost, "percentage": round(equipment_percent, 1)},
        "travel": {"amount": travel_cost, "percentage": round(travel_percent, 1)},
        "consumables": {"amount": consumables_cost, "percentage": round((consumables_cost / total_cost * 100) if total_cost > 0 else 0, 1)},
        "personnel": {"amount": personnel_cost, "percentage": round((personnel_cost / total_cost * 100) if total_cost > 0 else 0, 1)},
        "contingency": {"amount": contingency_cost, "percentage": round(contingency_percent, 1)},
        "overhead": {"amount": overhead_cost, "percentage": round((overhead_cost / total_cost * 100) if total_cost > 0 else 0, 1)}
    }
    
    print("Checking for disallowed items...")
    disallowed_rules = rules.get('disallowed_items', [])
    budget_items = budget.get('items', [])
    normalization_map = rules.get('normalization_map', {})
    normalized_budget_items = [normalization_map.get(item, item) for item in budget_items]
    found_disallowed = []
    
    for i, item in enumerate(normalized_budget_items):
        if item in disallowed_rules:
            original_item = budget_items[i]
            found_disallowed.append(original_item)
            results.append({
                "rule": "Disallowed Item", 
                "status": "FAIL", 
                "message": f"Expense '{original_item}' is explicitly disallowed.",
                "recommendation": f"Remove '{original_item}' from budget or find alternative."
            })
    
    if not found_disallowed:
        results.append({
            "rule": "Disallowed Items Check", 
            "status": "PASS", 
            "message": "No disallowed items found.",
            "recommendation": "Budget items comply with funding guidelines."
        })
    
    print("Checking contingency cost limit...")
    contingency_limit = rules.get('cost_limits_percent', {}).get('contingency_of_revenue', 5)
    revenue_cost = total_cost - equipment_cost
    
    if revenue_cost > 0:
        contingency_percent_calc = (contingency_cost / revenue_cost) * 100
        if contingency_percent_calc > contingency_limit:
            results.append({
                "rule": "Contingency Limit", 
                "status": "FAIL", 
                "message": f"Contingency is {contingency_percent_calc:.1f}% of revenue (limit: {contingency_limit}%)",
                "recommendation": f"Reduce contingency by ₹{int((contingency_percent_calc - contingency_limit) / 100 * revenue_cost):,}"
            })
        else:
            results.append({
                "rule": "Contingency Limit", 
                "status": "PASS", 
                "message": f"Contingency is {contingency_percent_calc:.1f}% of revenue (within {contingency_limit}% limit)",
                "recommendation": "Contingency allocation is appropriate."
            })
    
    print("Checking equipment cost limit...")
    equipment_limit = rules.get('cost_limits_percent', {}).get('equipment', 40)
    
    if equipment_percent > equipment_limit:
        excess_amount = int((equipment_percent - equipment_limit) / 100 * total_cost)
        results.append({
            "rule": "Equipment Cost Limit", 
            "status": "FAIL", 
            "message": f"Equipment is {equipment_percent:.1f}% of total (limit: {equipment_limit}%)",
            "recommendation": f"Reduce equipment costs by ₹{excess_amount:,} or increase total budget."
        })
    else:
        results.append({
            "rule": "Equipment Cost Limit", 
            "status": "PASS", 
            "message": f"Equipment is {equipment_percent:.1f}% of total (within {equipment_limit}% limit)",
            "recommendation": "Equipment allocation is within guidelines."
        })
    
    # Budget optimization suggestions
    optimization_tips = []
    
    if travel_percent > 15:
        optimization_tips.append("High travel costs detected. Consider virtual meetings or local alternatives.")
    
    if contingency_percent < 2:
        optimization_tips.append("Low contingency fund. Consider increasing for unexpected expenses.")
    
    if equipment_percent < 10 and total_cost > 1000000:
        optimization_tips.append("Low equipment allocation for large project. Verify if adequate for deliverables.")
    
    # Calculate financial health score
    health_score = 100
    for result in results:
        if result['status'] == 'FAIL':
            health_score -= 25
    
    if equipment_percent > 35:
        health_score -= 5
    if travel_percent > 20:
        health_score -= 5
    if contingency_percent < 3:
        health_score -= 5
    
    # Calculate overall financial status
    financial_passed = all(result['status'] == 'PASS' for result in results)
    
    return {
        "rules_analysis": results,
        "cost_breakdown": cost_breakdown,
        "financial_health_score": max(0, health_score),
        "optimization_tips": optimization_tips,
        "compliance_summary": {
            "total_rules_checked": len(results),
            "rules_passed": sum(1 for result in results if result['status'] == 'PASS'),
            "rules_failed": sum(1 for result in results if result['status'] == 'FAIL'),
            "disallowed_items": found_disallowed
        },
        "financial_passed": financial_passed,
        "total_rules": len(results),
        "passed_rules": sum(1 for result in results if result['status'] == 'PASS')
    }

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