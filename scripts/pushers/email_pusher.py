"""
pushers/email_pusher.py
Sends the daily briefing as an HTML email via SMTP.
Recommended providers: Resend (resend.com) or Gmail SMTP.
"""
import logging
import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

log = logging.getLogger("radar.pusher.email")


def _md_to_html(markdown: str) -> str:
    """Minimal Markdown → HTML conversion (no external markdown library required)."""
    import re
    html = markdown
    # headings
    html = re.sub(r"^### (.+)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
    html = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
    html = re.sub(r"^# (.+)$", r"<h1>\1</h1>", html, flags=re.MULTILINE)
    # bold / italic
    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
    html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html)
    # bullet lists
    html = re.sub(r"^- (.+)$", r"<li>\1</li>", html, flags=re.MULTILINE)
    html = re.sub(r"(<li>.*?</li>\n?)+", r"<ul>\g<0></ul>", html, flags=re.DOTALL)
    # horizontal rule
    html = re.sub(r"^---$", r"<hr/>", html, flags=re.MULTILINE)
    # paragraphs
    html = html.replace("\n\n", "</p><p>")
    html = f"<p>{html}</p>"

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         max-width: 700px; margin: 0 auto; padding: 20px; color: #333; }}
  h1 {{ color: #1a1a1a; border-bottom: 2px solid #e0e0e0; padding-bottom: 8px; }}
  h2 {{ color: #333; margin-top: 24px; }}
  h3 {{ color: #555; }}
  hr {{ border: none; border-top: 1px solid #e0e0e0; margin: 16px 0; }}
  li {{ margin: 4px 0; }}
  strong {{ color: #1a1a1a; }}
</style></head>
<body>{html}</body></html>"""


class EmailPusher:
    def __init__(self, config: dict):
        self.to = config.get("to", [])
        self.subject_tpl = config.get("subject_template", "📡 Blogger Radar | {date}")
        smtp = config.get("smtp", {})
        self.host = os.environ.get("SMTP_HOST", smtp.get("host", ""))
        self.port = int(os.environ.get("SMTP_PORT", smtp.get("port", 587)))
        self.username = os.environ.get("SMTP_USER", smtp.get("username", ""))
        self.password = os.environ.get("SMTP_PASS", smtp.get("password", ""))
        self.use_tls = smtp.get("use_tls", True)

    async def push(self, report: dict) -> bool:
        if not self.host or not self.username or not self.to:
            log.error("Email SMTP not configured")
            return False

        subject = self.subject_tpl.format(
            date=report["date"],
            blogger_count=report.get("blogger_count", 0),
        )
        html_body = _md_to_html(report["markdown"])

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.username
        msg["To"] = ", ".join(self.to)
        msg.attach(MIMEText(report["markdown"], "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        try:
            with smtplib.SMTP(self.host, self.port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
                server.sendmail(self.username, self.to, msg.as_string())
            log.info(f"  ✓ Email sent to {self.to}")
            return True
        except Exception as e:
            log.error(f"  ✗ Email send failed: {e}")
            return False
