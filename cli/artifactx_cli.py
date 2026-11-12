#!/usr/bin/env python3
import argparse
import requests
import sys

API_URL = "http://localhost:8000/api"

def main():
    parser = argparse.ArgumentParser(description="ArtifactX CLI")
    parser.add_argument("--token", required=True, help="JWT Access Token")
    parser.add_argument("--workspace", required=True, help="Workspace ID")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("findings", help="List vulnerabilities")

    args = parser.parse_args()
    headers = {"Authorization": f"Bearer {args.token}"}

    if args.command == "findings":
        res = requests.get(f"{API_URL}/workspaces/{args.workspace}/vulnerabilities/findings", headers=headers)
        if res.status_code == 200:
            for f in res.json():
                print(f"[{f['advisory']['severity']}] {f['advisory']['external_id']} - Risk: {f['risk_score']}")
        else:
            print(f"Error: {res.text}")

if __name__ == "__main__":
    main()
