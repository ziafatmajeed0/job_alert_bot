import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from datetime import datetime

# 🔐 Email credentials (from GitHub Secrets in GitHub Actions)
email_user = os.getenv("EMAIL_USER")
email_pass = os.getenv("EMAIL_PASS")
receiver_email = os.getenv("EMAIL_TO")


# 🔍 Search parameters
SEARCH_TERMS = [
    "data science internship",
    "machine learning internship",
    "AI internship",
    "associate data scientist"
]
CITY = "Lahore"
EXCLUDED_TERMS = ["freelance", "contract", "short-term"]

# 🧠 Generate search queries
def generate_queries():
    base_url = "https://www.google.com/search?q=site:linkedin.com/jobs+"
    return [f"{base_url}{term.replace(' ', '+')}+{CITY.replace(' ', '+')}" for term in SEARCH_TERMS]

# ✅ Extract clean URL
def extract_clean_url(href):
    if href.startswith("/url?q="):
        clean = href.split("/url?q=")[-1].split("&")[0]
        return clean
    elif href.startswith("http"):
        return href
    return None

# 🧹 Filter out unwanted terms
def is_relevant(text):
    return not any(term.lower() in text.lower() for term in EXCLUDED_TERMS)

# 🔍 Scrape Google for LinkedIn job posts
def scrape_jobs():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    job_list = []

    for url in generate_queries():
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        for result in soup.select(".tF2Cxc"):
            raw_href = result.a['href']
            title = result.h3.text if result.h3 else ""
            if not is_relevant(title):
                continue
            link = extract_clean_url(raw_href)
            if link and "linkedin.com/jobs" in link:
                job_list.append({
                    "title": title,
                    "link": link,
                    "company": "Unknown",
                    "location": CITY,
                    "hiring_manager": "N/A",
                    "deadline": "N/A"
                })

    return job_list

# 📧 Send email with results
def send_email(job_data):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "📊 New Job Listings for You!"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = RECEIVER_EMAIL

    # 🧾 Create HTML Table
    html_content = """
    <html>
      <body>
        <p>Hi,<br><br>Here are the latest job listings that match your criteria:</p>
        <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
          <tr>
            <th>Company</th>
            <th>Job Title</th>
            <th>Location</th>
            <th>Application Link</th>
            <th>Hiring Manager</th>
            <th>Deadline</th>
          </tr>
    """

    for job in job_data:
        html_content += f"""
          <tr>
            <td>{job['company']}</td>
            <td>{job['title']}</td>
            <td>{job['location']}</td>
            <td><a href="{job['link']}">Apply</a></td>
            <td>{job['hiring_manager']}</td>
            <td>{job['deadline']}</td>
          </tr>
        """

    html_content += """
        </table>
        <br><br>
        <p>Sent automatically on {}</p>
      </body>
    </html>
    """.format(datetime.now().strftime('%Y-%m-%d %H:%M'))

    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, RECEIVER_EMAIL, msg.as_string())
        print("✅ Email sent successfully.")
    except Exception as e:
        print("❌ Failed to send email:", e)

# 🚀 Main execution
if __name__ == "__main__":
    jobs = scrape_jobs()
    if jobs:
        send_email(jobs)
    else:
        print("ℹ️ No jobs found today.")
