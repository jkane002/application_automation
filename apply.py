import sys
from bs4 import BeautifulSoup
import requests
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


def parse_website(job_url):
    # print(job_url)
    # try:
    # jobs.lever.co
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

    job = JobApplication(job_url, title, company_name, location)
    print(job.company)
    print(job.title)
    print(job.location)
    print(job.url, end='\n\n')
    # except:
    #     print("404 error")

    # job = JobApplication(job_url,)


if __name__ == "__main__":
    try:
        '''Get 2nd argument'''
        job_url = sys.argv[1]
    except:
        print("\tEnter a job url")
    else:
        parse_website(job_url)
