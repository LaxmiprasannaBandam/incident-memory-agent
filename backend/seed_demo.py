#!/usr/bin/env python3
"""
Demo seed script for the Incident Memory & Response Agent.

This script seeds the Hindsight memory bank with pre-resolved incidents
from demo_incidents.json. Run this before a live demo of Incident 2
(Payment API 503) to ensure the memory is already present.

Usage:
    cd backend
    python seed_demo.py

Or to seed all incidents:
    python seed_demo.py --all

Or to seed only the first incident (Payment API):
    python seed_demo.py --payment-only
"""

import argparse
import asyncio
import json
import sys
import os
from pathlib import Path

# Allow running from backend/ directory
sys.path.insert(0, str(Path(__file__).parent))

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def load_demo_data() -> dict:
    data_path = Path(__file__).parent / "data" / "demo_incidents.json"
    with open(data_path) as f:
        return json.load(f)


def seed_incident(incident_data: dict, dry_run: bool = False) -> bool:
    """Seed a single incident into Hindsight memory."""
    from models.schemas import IncidentRequest, ResolveRequest
    from services.hindsight import HindsightService, build_memory_text

    inc_id = incident_data["id"]
    request = IncidentRequest(**incident_data["request"])
    resolution = ResolveRequest(**incident_data["resolution"])

    memory_text = build_memory_text(request, resolution, inc_id)

    print(f"\n{'='*60}")
    print(f"Seeding incident: {inc_id}")
    print(f"Title: {request.title}")
    print(f"Service: {request.service}")
    if dry_run:
        print("[DRY RUN] Memory text that would be stored:")
        print(memory_text)
        return True

    hindsight = HindsightService()

    # Ensure bank exists (async method — run in a fresh event loop)
    asyncio.run(hindsight.ensure_bank_exists())

    # Retain memory
    success = hindsight.retain(content=memory_text, document_id=inc_id)

    if success:
        print(f"✅ Seeded successfully (document_id={inc_id})")
    else:
        print(f"❌ Failed to seed incident {inc_id}")

    return success


def main():
    parser = argparse.ArgumentParser(description="Seed demo incidents into Hindsight memory")
    parser.add_argument("--all", action="store_true", help="Seed all demo incidents")
    parser.add_argument("--payment-only", action="store_true", help="Seed only the Payment API incident")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be stored without actually storing")
    args = parser.parse_args()

    data = load_demo_data()
    incidents = data["incidents"]

    if args.payment_only:
        incidents = [i for i in incidents if i["id"] == "demo-001"]
    elif not args.all:
        # Default: seed only the Payment API incident (demo-001)
        # This is the memory that makes the demo work for Incident 2
        incidents = [i for i in incidents if i["id"] == "demo-001"]

    print(f"Seeding {len(incidents)} incident(s) into Hindsight memory...")
    print(f"Hindsight URL: {os.getenv('HINDSIGHT_BASE_URL', 'http://localhost:8888')}")
    print(f"Bank ID: {os.getenv('HINDSIGHT_BANK_ID', 'incident-memory')}")

    results = []
    for incident in incidents:
        ok = seed_incident(incident, dry_run=args.dry_run)
        results.append(ok)

    print(f"\n{'='*60}")
    print(f"Seeding complete: {sum(results)}/{len(results)} incidents stored")

    if not args.dry_run and sum(results) == len(results):
        print("\n✅ Demo is ready. You can now submit Incident 2 (Payment API 503)")
        print("   and Hindsight will recall the previous incident.")
    elif args.dry_run:
        print("\n[DRY RUN] No data was stored. Remove --dry-run to actually seed.")


if __name__ == "__main__":
    main()
