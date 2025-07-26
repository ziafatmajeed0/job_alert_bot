import requests
from bs4 import BeautifulSoup
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# --- Load secrets ---
EMAIL = os.getenv("EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

# --- Job keywords and filters ---
KEYWORDS = ["data science internship", "machine learning internship", "AI internship", "associate data scientist"]
EXCLUDE = ["freelance", "contract", "short-term"]
LOCATION = "Lahore"

# --- Cold outreach message ---
COLD_MESSAGE = """
Hello [Hiring Manager Name],

I came across your job listing and found it aligns with my skills and experience in data science and AI. I'm a recent software engineering graduate with practical projects in machine learning. I’d love to connect and learn more about your expectations for this role.

Best regards,
Ziafat Majeed
"""

# --- Scrape LinkedIn jobs ---
def scrape_jobs():
    print("Scraping jobs...")
    results = []
    headers = {"User-Agent": "Mozilla/5.0"}
    for keyword in KEYWORDS:
        url = f"https://www.google.com/search?q=site:linkedin.com/jobs+{keyword.replace(' ', '+')}+{LOCATION}"
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        for link in soup.select("a"):
            href = link.get("href")
            if href and "linkedin.com/jobs" in href:
                title = link.get_text().strip()
                if any(ex in title.lower() for ex in EXCLUDE):
                    continue
                results.append((title, href))
    return list(set(results))  # remove duplicates

# --- Email job list ---
def send_email(jobs):
    print("Sending email...")
    message = MIMEMultipart("alternative")
    message["Subject"] = "📌 Latest Job Listings for You"
    message["From"] = EMAIL
    message["To"] = RECEIVER_EMAIL

    html = f"<h3>🧠 Found {len(jobs)} job(s) for you!</h3><ul>"
    for title, link in jobs:
        html += f"<li><b>{title}</b> — <a href='{link}'>Apply</a></li>"
    html += "</ul><br><p><b>Suggested Cold Message:</b></p><pre>{COLD_MESSAGE}</pre>"

    message.attach(MIMEText(html, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL, EMAIL_PASSWORD)
        server.sendmail(EMAIL, RECEIVER_EMAIL, message.as_string())
    print("Email sent!")

# --- Main ---
if __name__ == "__main__":
    jobs = scrape_jobs()
    if jobs:
        send_email(jobs)
    else:
        print("No jobs found.")
