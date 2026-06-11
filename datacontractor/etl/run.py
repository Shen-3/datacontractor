import argparse
import sys

import requests

API_BASE = "http://localhost:8000"


def run_validation(dataset_path: str, contract_name: str):
    print(f"Running validation for contract '{contract_name}' with dataset '{dataset_path}'")

    response = requests.post(
        f"{API_BASE}/contracts/{contract_name}/validate-data",
        json={
            "dataset_path": dataset_path,
            "contract_name": contract_name,
            "dataset_name": dataset_path.split("/")[-1],
        },
    )

    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        sys.exit(1)

    result = response.json()

    print(f"\nContract: {result['contract']}")
    print(f"Version:  {result['version']}")
    print(f"Dataset:  {result['dataset']}")
    print(f"Status:   {result['status']}")
    print(f"Rows:     {result['rows_checked']}")
    print(f"Violations: {result['violations_count']}")

    if result["violations"]:
        print("\nViolations:")
        for v in result["violations"]:
            print(f"  - [{v['severity']}] {v['check_name']}: {v['message']} ({v['failed_rows_count']} rows)")

    if result["status"] in ("failed", "blocked"):
        print(f"\nETL load BLOCKED due to {result['status']} validation")
        sys.exit(1)
    else:
        print("\nETL load allowed - all checks passed")


def main():
    parser = argparse.ArgumentParser(description="DataContractor ETL Runner")
    parser.add_argument("--dataset", required=True, help="Path to CSV dataset")
    parser.add_argument("--contract", required=True, help="Contract name")
    args = parser.parse_args()

    run_validation(args.dataset, args.contract)


if __name__ == "__main__":
    main()
