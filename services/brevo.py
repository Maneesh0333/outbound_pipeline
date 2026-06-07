import os
import requests


class BrevoClient:

    BASE_URL = "https://api.brevo.com/v3/smtp/email"

    def __init__(self):
        self.api_key    = os.getenv("BREVO_API_KEY")
        self.from_email = os.getenv("FROM_EMAIL")
        self.from_name  = os.getenv("FROM_NAME")

    # ── Single send ───────────────────────────────────────────────────────────
    def send_email(self, lead):
        """
        Send a personalised outreach email to a single lead.
        Returns {"ok": True} or {"ok": False, "email": ..., "error": ...}.
        """
        email      = lead.get("email")
        first_name = lead.get("first_name") or lead.get("full_name", "there")
        title      = lead.get("title", "")
        company    = lead.get("company_name") or lead.get("domain", "your company")

        headers = {
            "accept": "application/json",
            "api-key": self.api_key,
            "content-type": "application/json",
        }

        payload = {
            "sender": {
                "name":  self.from_name,
                "email": self.from_email,
            },
            "to": [{"email": email, "name": lead.get("full_name", "")}],
            "subject": f"Quick question for you, {first_name}",
            "htmlContent": self._build_html(first_name, title, company),
            "textContent": self._build_text(first_name, title, company),
        }

        try:
            response = requests.post(
                self.BASE_URL,
                headers=headers,
                json=payload,
                timeout=30,
            )
            if response.status_code in (200, 201):
                return {"ok": True, "email": email}
            else:
                return {
                    "ok":    False,
                    "email": email,
                    "error": f"HTTP {response.status_code}: {response.text[:120]}",
                }
        except Exception as e:
            return {"ok": False, "email": email, "error": str(e)}

    # ── Bulk send ─────────────────────────────────────────────────────────────
    def send_bulk(self, leads):
        results = []
        for lead in leads:
            email = lead.get("email")
            if not email:
                continue
            print(f"   Sending → {email}")
            result = self.send_email(lead)
            results.append(result)
            if not result["ok"]:
                print(f"   ⚠ Failed: {result.get('error')}")
        return results

    # ── Templates ─────────────────────────────────────────────────────────────
    @staticmethod
    def _build_html(first_name, title, company):
        title_line = f" as {title}" if title else ""
        return f"""
        <p>Hi {first_name},</p>

        <p>
            I came across your profile and noticed you're working{title_line}
            at {company}. I'd love to connect and explore whether there's a
            fit for a potential collaboration.
        </p>

        <p>
            Would you be open to a quick 15-minute call this week or next?
        </p>

        <p>
            Thanks,<br>
        </p>
        """

    @staticmethod
    def _build_text(first_name, title, company):
        title_line = f" as {title}" if title else ""
        return (
            f"Hi {first_name},\n\n"
            f"I came across your profile and noticed you're working{title_line} "
            f"at {company}. I'd love to connect and explore whether there's a "
            f"fit for a potential collaboration.\n\n"
            f"Would you be open to a quick 15-minute call this week or next?\n\n"
            f"Thanks,"
        )
