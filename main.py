import requests
from bs4 import BeautifulSoup
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL = os.getenv("EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

KEYWORDS = ["data science internship", "machine learning internship", "AI internship", "associate data scientist"]
EXCLUDE = ["freelance", "contract", "short-term"]
LOCATION = "Lahore"

COLD_MESSAGE = """
Hello [Hiring Manager Name],

I came across your job listing and found it aligns with my skills and experience in data science and AI. I'm a recent software engineering graduate with practical projects in machine learning. I’d love to connect and learn more about your expectations for this role.

Best regards,
Ziafat Majeed
"""

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
                results.append({
                    "title": title,
                    "link": href,
                    "company": "N/A",
                    "location": LOCATION,
                    "hiring_manager": "Not Available",
                    "deadline": "Not Listed"
                })
    return list({job['link']: job for job in results}.values())

def send_email(jobs):
    print("Sending email...")
    message = MIMEMultipart("alternative")
    message["Subject"] = "📌 Latest Job Listings for You"
    message["From"] = EMAIL
    message["To"] = RECEIVER_EMAIL

    html = f"""
    <h3>🧠 Found {len(jobs)} job(s) for you!</h3>
    <table border='1' cellspacing='0' cellpadding='5'>
        <tr>
            <th>Company</th>
            <th>Job Title</th>
            <th>Location</th>
            <th>Application Link</th>
            <th>Hiring Manager</th>
            <th>Deadline</th>
        </tr>
    """
    for job in jobs:
        html += f"""
        <tr>
            <td>{job['company']}</td>
            <td>{job['title']}</td>
            <td>{job['location']}</td>
            <td><a href="{job['link']}">Apply</a></td>
            <td>{job['hiring_manager']}</td>
            <td>{job['deadline']}</td>
        </tr>
        """
    html += "</table><br><p><b>Suggested Cold Message:</b></p><pre>{}</pre>".format(COLD_MESSAGE)
    message.attach(MIMEText(html, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL, EMAIL_PASSWORD)
        server.sendmail(EMAIL, RECEIVER_EMAIL, message.as_string())
    print("Email sent!")

if __name__ == "__main__":
    jobs = scrape_jobs()
    if jobs:
        send_email(jobs)
    else:
        print("No jobs found.")
