import csv
import datetime
import os


FIELDS = [
    "full_name",
    "first_name",
    "last_name",
    "title",
    "email",
    "email_status",
    "company_name",
    "industry",
    "mobile",
    "linkedin",
    "domain",
]


def save_results(leads, domain, output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)

    ts       = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"outreach_{domain.replace('.', '_')}_{ts}.csv"
    path     = os.path.join(output_dir, filename)

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(leads)

    return path
