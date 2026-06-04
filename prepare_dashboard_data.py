#!/usr/bin/env python3
"""
INFA Contractors Dashboard Data Preparation Script

Reads the INFA Contractors CSV and generates a JSON file for the dashboard.
Handles completion percentage calculation and data grouping.
"""

import csv
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# Input and output paths
CSV_PATH = Path.home() / "Downloads" / "INFA Contractors - Apr Data (1).csv"
AGGREGATE_CSV_PATH = Path.home() / "Downloads" / "INFA Contractors - Aggregate.csv"
OUTPUT_PATH = Path(__file__).parent / "dashboard_data.json"

def normalize_status(status):
    """Normalize status values to standardized categories."""
    if not status or not status.strip():
        return 'Not Started'

    status_lower = status.strip().lower()

    # Combine all "In Progress" variations
    if 'in progress' in status_lower:
        return 'In Progress'

    # Combine "Not Started" and "(Not Started)"
    if 'not started' in status_lower:
        return 'Not Started'

    # Keep specific statuses as-is
    if status_lower in ['complete', 'onboarded', 'no action needed', 'po migration', 'new']:
        return status.strip()

    # Handle SOW variations
    if 'sow' in status_lower:
        return 'In Progress - SOW'

    return status.strip()

def is_complete_status(status):
    """Determine if a status represents completion or out of scope."""
    if not status:
        return False
    status_lower = status.strip().lower()
    return status_lower in ['complete', 'onboarded', 'no action needed']

def is_out_of_scope(status):
    """Determine if contractor is out of scope."""
    if not status:
        return False
    return status.strip().lower() == 'no action needed'

def get_health_color(percentage):
    """Get health indicator color based on completion percentage."""
    if percentage < 25:
        return 'red'
    elif percentage < 50:
        return 'orange'
    elif percentage < 75:
        return 'yellow'
    else:
        return 'green'

def main():
    print(f"Reading CSV from: {CSV_PATH}")

    if not CSV_PATH.exists():
        print(f"ERROR: CSV file not found at {CSV_PATH}")
        return

    # Read all contractor data
    contractors = []
    with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            contractors.append(row)

    total_contractors = len(contractors)
    print(f"Loaded {total_contractors} contractor records")

    # Calculate overall completion and scope
    complete_count = sum(1 for c in contractors if is_complete_status(c['Status']))
    out_of_scope_count = sum(1 for c in contractors if is_out_of_scope(c['Status']))
    in_scope_count = total_contractors - out_of_scope_count

    # Completion is based on total contractors (including out of scope)
    overall_completion = (complete_count / total_contractors * 100) if total_contractors > 0 else 0

    # In-scope completion (for reference)
    in_scope_completion = (complete_count / in_scope_count * 100) if in_scope_count > 0 else 0

    overall_health = get_health_color(overall_completion)

    print(f"Overall completion: {complete_count}/{total_contractors} ({overall_completion:.1f}%)")
    print(f"Out of scope: {out_of_scope_count}")
    print(f"In scope: {in_scope_count} ({in_scope_completion:.1f}% complete)")

    # Group by Transition Plan and Supplier
    by_transition_plan = defaultdict(lambda: {
        'contractors': [],
        'status_counts': defaultdict(int),
        'fieldglass_status_counts': defaultdict(int)
    })

    by_supplier = defaultdict(list)

    for contractor in contractors:
        transition_plan = contractor['Transition Plan'].strip() if contractor['Transition Plan'] else '(Not Specified)'
        status = normalize_status(contractor['Status'])
        fieldglass_status = contractor['Fieldglass Status'].strip() if contractor['Fieldglass Status'] else '(Not Specified)'
        supplier = contractor['Supplier Organization'].strip() if contractor['Supplier Organization'] else '(Not Specified)'

        # Store normalized status back
        contractor['_normalized_status'] = status

        by_transition_plan[transition_plan]['contractors'].append(contractor)
        by_transition_plan[transition_plan]['status_counts'][status] += 1
        by_transition_plan[transition_plan]['fieldglass_status_counts'][fieldglass_status] += 1

        by_supplier[supplier].append(contractor)

    # Calculate completion per transition plan
    transition_plan_summary = []
    for plan_name, data in sorted(by_transition_plan.items(), key=lambda x: len(x[1]['contractors']), reverse=True):
        total = len(data['contractors'])
        complete = sum(1 for c in data['contractors'] if is_complete_status(c['Status']))
        completion_pct = (complete / total * 100) if total > 0 else 0
        health = get_health_color(completion_pct)

        # Convert status counts to list format
        status_breakdown = [
            {'status': status, 'count': count}
            for status, count in sorted(data['status_counts'].items(), key=lambda x: x[1], reverse=True)
        ]

        transition_plan_summary.append({
            'name': plan_name,
            'total': total,
            'complete': complete,
            'completion_percentage': round(completion_pct, 1),
            'health': health,
            'status_breakdown': status_breakdown
        })

    # Overall status distribution (normalized)
    status_distribution = defaultdict(int)
    for contractor in contractors:
        status = contractor['_normalized_status']
        status_distribution[status] += 1

    status_summary = [
        {'status': status, 'count': count}
        for status, count in sorted(status_distribution.items(), key=lambda x: x[1], reverse=True)
    ]

    # Fieldglass status distribution (in-scope only, with percentages)
    in_scope_contractors = [c for c in contractors if not is_out_of_scope(c['Status'])]
    fieldglass_distribution = defaultdict(int)
    for contractor in in_scope_contractors:
        fg_status = contractor['Fieldglass Status'].strip() if contractor['Fieldglass Status'] else '(Not Specified)'
        fieldglass_distribution[fg_status] += 1

    in_scope_total = len(in_scope_contractors)
    fieldglass_summary = [
        {
            'status': status,
            'count': count,
            'percentage': round((count / in_scope_total * 100) if in_scope_total > 0 else 0, 1)
        }
        for status, count in sorted(fieldglass_distribution.items(), key=lambda x: x[1], reverse=True)
    ]

    # Supplier distribution with status breakdown
    supplier_summary = []
    for supplier, supplier_contractors in sorted(by_supplier.items(), key=lambda x: len(x[1]), reverse=True):
        status_counts = defaultdict(int)
        for c in supplier_contractors:
            status_counts[c['_normalized_status']] += 1

        supplier_summary.append({
            'supplier': supplier,
            'count': len(supplier_contractors),
            'status_breakdown': dict(status_counts)
        })

    # Get latest update date
    last_updated = max(
        (c['Last updated'] for c in contractors if c.get('Last updated')),
        default=datetime.now().strftime('%Y-%m-%d')
    )

    # Load aggregate bill rate data
    aggregate_data = []
    if AGGREGATE_CSV_PATH.exists():
        print(f"\nReading aggregate data from: {AGGREGATE_CSV_PATH}")
        with open(AGGREGATE_CSV_PATH, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                sf_function = row.get('Salesforce Function', '').strip()
                bill_rate_raw = row.get('SUM of Bill Rate (USD)', '').strip()

                # Parse the bill rate - handle $, commas, #ERROR!
                if bill_rate_raw in ['#ERROR!', '', '$0.00']:
                    bill_rate = bill_rate_raw
                    bill_rate_numeric = 0
                else:
                    bill_rate = bill_rate_raw
                    bill_rate_numeric = float(bill_rate_raw.replace('$', '').replace(',', ''))

                aggregate_data.append({
                    'salesforce_function': sf_function,
                    'bill_rate_display': bill_rate,
                    'bill_rate_numeric': bill_rate_numeric
                })
        print(f"Loaded {len(aggregate_data)} aggregate rows")
    else:
        print(f"\nWARNING: Aggregate CSV not found at {AGGREGATE_CSV_PATH}")

    # Build output data structure
    output_data = {
        'generated_at': datetime.now().isoformat(),
        'last_data_update': last_updated,
        'summary': {
            'total_contractors': total_contractors,
            'complete_count': complete_count,
            'out_of_scope_count': out_of_scope_count,
            'in_scope_count': in_scope_count,
            'in_progress_count': in_scope_count - (complete_count - out_of_scope_count),
            'overall_completion_percentage': round(overall_completion, 1),
            'in_scope_completion_percentage': round(in_scope_completion, 1),
            'overall_health': overall_health
        },
        'status_distribution': status_summary,
        'fieldglass_distribution': fieldglass_summary,
        'supplier_distribution': supplier_summary,
        'aggregate_bill_rates': aggregate_data,
        'by_transition_plan': transition_plan_summary,
        'contractors': contractors
    }

    # Write JSON output
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\nDashboard data written to: {OUTPUT_PATH}")
    print(f"Data generated at: {output_data['generated_at']}")
    print(f"Overall health indicator: {overall_health.upper()}")

    # Print summary by transition plan
    print("\n=== Completion by Transition Plan ===")
    for plan in transition_plan_summary[:10]:  # Top 10
        print(f"  {plan['name'][:50]:50s} {plan['complete']:3d}/{plan['total']:3d} ({plan['completion_percentage']:5.1f}%) [{plan['health'].upper()}]")

    if len(transition_plan_summary) > 10:
        print(f"  ... and {len(transition_plan_summary) - 10} more")

if __name__ == '__main__':
    main()
