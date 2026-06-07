import sys
import os

from services.prospeo import ProspeoClient
from services.brevo import BrevoClient
from utils.preview import preview
from utils.logger import save_results


REQUIRED_ENV = ["PROSPEO_API_KEY", "BREVO_API_KEY", "FROM_EMAIL", "FROM_NAME"]


def validate_env():
    missing = [k for k in REQUIRED_ENV if not os.getenv(k)]
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        sys.exit(1)


def run_pipeline(domain):
    validate_env()

    print("\n🚀 Outbound pipeline starting...\n")

    prospeo = ProspeoClient()
    brevo = BrevoClient()

    # ── Step 1: Search ────────────────────────────────────────────────────────

    print("[1] Searching decision makers...")

    people = prospeo.search_people(domain)

    if not people:
        print("❌ No people found. Check the domain or seniority filters.")
        return

    print(f"[2] Found {len(people)} profiles")

    # ── Step 2: Enrich ────────────────────────────────────────────────────────

    print("[3] Enriching profiles (only 5) (verified emails only)...")

    enriched = prospeo.enrich_people(people)

    verified = [p for p in enriched if p.get("email")]

    if not verified:
        print("❌ No verified emails found.")
        return

    print(f"[4] Verified emails: {len(verified)}")

    # ── Step 3: Preview + confirm ─────────────────────────────────────────────
    preview(verified)

    send = input("\nSend outreach emails? (y/n): ").strip().lower()

    if send != "y":
        print("Aborted.")
        return

    # ── Step 4: Send ──────────────────────────────────────────────────────────
    print("\n[5] Sending emails to myself...")

    results = brevo.send_bulk(verified)
    
    sent     = [r for r in results if r["ok"]]
    failed   = [r for r in results if not r["ok"]]

    print(f"\n✅ Sent: {len(sent)}  ❌ Failed: {len(failed)}")

    if failed:
        print("\nFailed recipients:")
        for f in failed:
            print(f"  {f['email']} — {f.get('error', 'unknown error')}")

    # ── Step 5: Log ───────────────────────────────────────────────────────────
    log_path = save_results(verified, domain)
    print(f"\n📄 Results saved to {log_path}")
    print("\nDone.")
