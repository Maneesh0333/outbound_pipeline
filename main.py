from dotenv import load_dotenv
from pipeline.runner import run_pipeline

load_dotenv()

if __name__ == "__main__":
    domain = input("\nEnter seed domain: ").strip()
    if not domain:
        print("No domain provided.")
    else:
        run_pipeline(domain)
