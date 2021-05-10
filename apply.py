import sys
from bs4 import BeautifulSoup
import urllib.request
from urllib.request import urlopen
'''
LinkedIn
title class="t-24 t-bold" id='ember45'
company id="ember47"
location class="jobs-unified-top-card__bullet"
url
'''


class JobApplication:
    def __init__(self, url=None, title=None, company=None, location=None):
        self.url = url
        self.title = title
        self.company = company
        self.location = location


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
    # print(job_url)
    '''
    known_parsing
    '''

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
    # general_list = ['workday', 'icims', 'careers', 'gh_jid']

    for known in known_parsing:
        if known['name'] in job_url and known['name'] == 'linkedin':
            job = parse_linkedin(job_url)
        elif known['name'] in job_url and known['name'] == "greenhouse":
            job = parse_greenhouse(job_url)
        elif known['name'] in job_url and known['name'] == "jobs.lever.co":
            job = parse_jobsleverco(job_url)

    # job = general_parse(job_url)
    print(job.company)
    print(job.title)
    print(job.location)
    print(job.url, end='\n\n')


if __name__ == "__main__":
    try:
        '''Get 2nd argument'''
        job_url = sys.argv[1]
    except:
        print("\tEnter a job url")
    else:
        job = JobApplication()
        parse_website(job_url, job)
