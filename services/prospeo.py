import os
import time
import requests


class ProspeoClient:

    BASE_URL = "https://api.prospeo.io"

    SENIORITY_FILTERS = ["C-Suite", "Vice President"]

    def __init__(self):
        self.api_key = os.getenv("PROSPEO_API_KEY")

    # ── HTTP ──────────────────────────────────────────────────────────────────
    def _post(self, endpoint, payload):
        headers = {
            "X-KEY": self.api_key,
            "Content-Type": "application/json",
        }
        try:
            response = requests.post(
                f"{self.BASE_URL}/{endpoint}",
                json=payload,
                headers=headers,
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()

            if data.get("error"):
                code = data.get("error_code", "UNKNOWN")
                print(f"   ⚠ Prospeo error [{endpoint}]: {code}")
                return {}

            return data

        except requests.exceptions.HTTPError as e:
            print(f"   ⚠ HTTP {e.response.status_code} [{endpoint}]: {e.response.text[:120]}")
            return {}
        except Exception as e:
            print(f"   ⚠ Request error [{endpoint}]: {e}")
            return {}

    # ── Search ────────────────────────────────────────────────────────────────
    def search_people(self, domain, max_pages=1):
        """
        Paginate through search results and return all matching leads.
        Stops when a page returns no results or max_pages is reached.
        """
        leads = []

        for page in range(1, max_pages + 1):
            payload = {
                "page": page,
                "filters": {
                    "company": {
                        "websites": {
                            "include": [domain]
                        }
                    },
                    "person_seniority": {
                        "include": self.SENIORITY_FILTERS
                    },
                },
            }

            data = self._post("search-person", payload)
            results = data.get("results", [])

            if not results:
                break

            for row in results:
                person = row.get("person", {})
                leads.append({
                    "person_id":  person.get("person_id"),
                    "first_name": person.get("first_name"),
                    "last_name":  person.get("last_name"),
                    "full_name":  person.get("full_name"),
                    "title":      person.get("current_job_title"),
                    "linkedin":   person.get("linkedin_url"),
                    "domain":     domain,
                })

            print(f"   Page {page}: {len(results)} results")

            # Stop early if this page had fewer results than a full page
            if len(results) < 10:
                break

        return self._dedupe(leads)

    # ── Enrich ────────────────────────────────────────────────────────────────
    def enrich_person(self, person):
        """
        Enrich a single person using person_id (preferred) or linkedin_url.
        Sets only_verified_email=True so credits are only spent on usable results.
        """
        if person.get("person_id"):
            identifier = {"person_id": person["person_id"]}
        elif person.get("linkedin"):
            identifier = {"linkedin_url": person["linkedin"]}
        else:
            # Fallback: name + domain
            identifier = {
                "full_name":        person.get("full_name"),
                "company_website":  person.get("domain"),
            }

        payload = {
            "only_verified_email": True,
            "data": identifier,
        }

        return self._post("enrich-person", payload)

    def enrich_people(self, people, delay=0.5):
        """
        Sequentially enrich all people with a small delay to respect rate limits.
        """
        people = people[:5] 

        enriched = []
        total = len(people)

        for index, person in enumerate(people, start=1):
            print(f"   [{index}/{total}] {person['full_name']}")

            data = self.enrich_person(person)

            person_obj = data.get("person") or {}
            email_obj  = (person_obj.get("email") or {})
            mobile_obj = (person_obj.get("mobile") or {})
            company    = data.get("company") or {}

            enriched.append({
                **person,
                "email":        email_obj.get("email"),
                "email_status": email_obj.get("status"),
                "company_name": company.get("name"),
                "industry":     company.get("industry"),
                "mobile":       mobile_obj.get("mobile") if mobile_obj.get("revealed") else None,
            })

            if index < total:
                time.sleep(delay)

        return enriched

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _dedupe(leads):
        """Remove duplicate leads by person_id, falling back to linkedin URL."""
        seen = set()
        unique = []
        for lead in leads:
            key = lead.get("person_id") or lead.get("linkedin")
            if key and key not in seen:
                seen.add(key)
                unique.append(lead)
        return unique
