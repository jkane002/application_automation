import sys
from bs4 import BeautifulSoup
import urllib.request
from urllib.request import urlopen
from datetime import date

import gspread
from oauth2client.service_account import ServiceAccountCredentials

'''
Automation script that enters the job's title, company, location, and url
into Google Sheets given a URL
'''


class JobApplication:
    def __init__(self, url=None, title=None, company=None, location=None):
        self.url = url
        self.title = title
        self.company = company
        self.location = location

    def addRecord(self):
        '''Enters job onto Google Sheets '''

        # Authorize Google Sheets
        sheetName = 'Job Search 2021'
        scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
                 "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

        creds = ServiceAccountCredentials.from_json_keyfile_name(
            'creds.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open(sheetName).sheet1
        data = sheet.get_all_records()

        # Enter today's date
        today = date.today()
        applied_date = today.strftime("%m/%d/%Y")

        # Insert a new row into Google Sheets
        newEntry = [self.company, self.title,
                    self.location, self.url, applied_date]
        sheet.insert_row(newEntry, 2)


def parse_jobsleverco(job_url):
    html = urlopen(job_url)
    soup = BeautifulSoup(html, 'html.parser')
    posting_headline = soup.find(
        'div', attrs={'class': 'posting-headline'}
    )
    # Job Title
    title = posting_headline.contents[0].get_text()

    # Job Location
    details = posting_headline.contents[1]
    location = details.find_all(
        'div', {'class': 'sort-by-time posting-category medium-category-label'}
    )[0].get_text().strip('/')

    # Company name
    footer = soup.find_all(
        'div', {
            'class': 'main-footer-text page-centered'}
    )
    footer_name = footer[0].find('p').text.strip()
    stopwords = ['home', 'page']
    querywords = footer_name.split()

    resultwords = [word for word in querywords if word.lower()
                   not in stopwords]
    company_name = ' '.join(resultwords)

    return JobApplication(job_url, title, company_name, location)


def parse_linkedin(job_url):
    html = urlopen(job_url)
    soup = BeautifulSoup(html, 'html.parser')

    # Job Location
    span_loc = soup.find(
        'span', {'class': 'topcard__flavor topcard__flavor--bullet'})
    location = span_loc.get_text().strip()

    # Company name
    company_atag = soup.find(
        'a', {'class': 'topcard__org-name-link topcard__flavor--black-link'})
    company_name = company_atag.get_text().strip()

    # Job title
    title = soup.find('h1', {'class': 'topcard__title'}).get_text().strip()

    return JobApplication(job_url, title, company_name, location)


def parse_greenhouse(job_url):
    html = urlopen(job_url)
    soup = BeautifulSoup(html, 'html.parser')

    # Job Location
    location_loc = soup.find(
        'div', {'class': 'location'})
    location = location_loc.get_text().strip()

    # Company name
    company_loc = soup.find(
        'span', {'class': 'company-name'})
    company_name = company_loc.get_text().strip()
    stopwords = ['at']
    querywords = company_name.split()

    resultwords = [word for word in querywords if word.lower()
                   not in stopwords]
    company_name = ' '.join(resultwords)

    # Job title
    title = soup.find('h1', {'class': 'app-title'}).get_text().strip()

    return JobApplication(job_url, title, company_name, location)


def general_parse(job_url):
    while True:
        title = input("Job title: ")
        company_name = input("Company name: ")
        location = input("Location: ")
        print(f"{title} at {company_name} in {location} ({job_url})")

        res = input('Is this good? (y/n)')
        if res == '' or not res[0].lower() in ['y', 'n']:
            print('Please answer with yes or no!')
        elif res[0].lower() == 'n':
            continue
        else:
            break

    return JobApplication(job_url, title, company_name, location)


def parse_website(job_url, job):
    '''
    Factory pattern in parsing websites
    '''
    # web scraped these websites
    known_parsing = [
        {
            'name': 'linkedin',
            'parser': parse_linkedin
        },
        {
            'name': 'greenhouse',
            'parser': parse_greenhouse
        },
        {
            'name': 'jobs.lever.co',
            'parser': parse_jobsleverco
        }
    ]

    # known websites for general parsing
    general_list = ['workday', 'icims', 'careers', 'gh_jid']

    for known in known_parsing:
        if known['name'] in job_url and known['name'] == 'linkedin':
            job = parse_linkedin(job_url)
        elif known['name'] in job_url and known['name'] == "greenhouse":
            job = parse_greenhouse(job_url)
        elif known['name'] in job_url and known['name'] == "jobs.lever.co":
            job = parse_jobsleverco(job_url)

    for co in general_list:
        if co in job_url:
            job = general_parse(job_url)

    if job.title:
        job.addRecord()
        print(
            f"Entered:\n{job.company}\n{job.title}\n{job.location}\n{job.url}\n"
        )
    else:
        '''Link not in known_parsing nor general_list lists'''
        while True:
            valid_url = input(f"Valid url at {job_url}? (y/n)")
            if valid_url == '' or not valid_url[0].lower() in ['y', 'n']:
                print('Please answer with yes or no!')
            elif valid_url[0].lower() == 'n':
                break
            else:
				'''
				Can force inputting wrong entries
				Honor code when inputting data
				TODO: have more checks regarding url patterns
				'''
                job = general_parse(job_url)
                job.addRecord()
                break


if __name__ == "__main__":
    try:
        '''Get 2nd argument'''
        job_url = sys.argv[1]
    except:
        print("\tEnter a job url")
    else:
        job = JobApplication()
        parse_website(job_url, job)
