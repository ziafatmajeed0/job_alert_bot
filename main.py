import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from datetime import datetime

def search_jobs():
    keywords = ["data science internship", "machine learning internship", "AI internship", "associate data scientist"]
    location = "Lahore"
    jobs = []

    for keyword in keywords:
        query = f"{keyword} {location}".replace(" ", "+")
        url = f"https://www.google.com/search?q=site:linkedin.com/jobs+{query}"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9"
        }

        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        results = soup.find_all("a", href=True)

        for link in results:
            href = link['href']
            if "linkedin.com/jobs" in href and "/url?q=" in href:
                clean_url = href.split("/url?q=")[-1].split("&")[0]
                job_title = link.text.strip()
                if clean_url and job_title:
                    jobs.append({
                        "company": "LinkedIn",
                        "title": job_title,
                        "location": location,
                        "link": clean_url,
                        "manager": "N/A",
                        "deadline": "N/A"
                    })

    return jobs

def create_email_table(jobs):
    if not jobs:
        return "<p>No matching jobs found.</p>"

    table = """
    <table border="1" cellspacing="0" cellpadding="6" style="border-collapse: collapse; width: 100%; font-family: Arial, sans-serif;">
        <thead style="background-color: #f2f2f2;">
            <tr>
                <th>Company</th>
                <th>Title</th>
                <th>Location</th>
                <th>Application Link</th>
                <th>Hiring Manager</th>
                <th>Deadline</th>
            </tr>
        </thead>
        <tbody>
    """
    for job in jobs:
        table += f"""
        <tr>
            <td>{job['company']}</td>
            <td>{job['title']}</td>
            <td>{job['location']}</td>
            <td><a href="{job['link']}">Apply</a></td>
            <td>{job['manager']}</td>
            <td>{job['deadline']}</td>
        </tr>
        """
    table += "</tbody></table>"
    return table

def send_email(job_data):
    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    receiver = os.getenv("EMAIL_TO")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🔎 {len(job_data)} New Job Listings - {datetime.now().strftime('%d %b %Y %I:%M %p')}"
    msg["From"] = sender
    msg["To"] = receiver

    cold_message = """
    <p>Dear Hiring Manager,</p>
    <p>I recently came across this opportunity and found it aligned with my background in data science and machine learning. I would love to connect and explore the opportunity further.</p>
    <p>Regards,<br>Ziafat Majeed</p>
    <hr>
    """

    html = f"""
    <html>
      <body>
        {cold_message}
        {create_email_table(job_data)}
      </body>
    </html>
    """

    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        print("✅ Email sent successfully!")
    except Exception as e:
        print("❌ Failed to send email:", e)

if __name__ == "__main__":
    jobs = search_jobs()
    send_email(jobs)
