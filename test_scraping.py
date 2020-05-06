# This script tests the web scraping functionality 
# provided in the 'Web' module. 

import re
import requests
import Interface
import Web

# Test data
LinkedInurls = ['https://www.linkedin.com/jobs/view/1830362046/','https://www.linkedin.com/jobs/view/1832231619/']
CVLibraryurls = ['https://www.cv-library.co.uk/job/211966039']
FindAJoburls = ['https://findajob.dwp.gov.uk/details/4000823']
Indeedurls = ['https://www.indeed.co.uk/rc/clk/dl?jk=e2b42ca35392f534']
Reedurls = ['https://www.reed.co.uk/jobs/solution-architect/40198488']

# Test LinkedIn scraping
for LinkedInurl in LinkedInurls :
    print(LinkedInurl)
    print(Web.ScrapeLinkedIn(LinkedInurl))
    
# Test CVLibrary scraping
for CVLibraryurl in CVLibraryurls :
    print(CVLibraryurl)
    print(Web.ScrapeCVLibrary(CVLibraryurl))
    
# Test FindAJob scraping
for FindAJoburl in FindAJoburls :
    print(FindAJoburl)
    print(Web.ScrapeFindAJob(FindAJoburl))
    
# Test FindAJob scraping
for Indeedurl in Indeedurls :
    print(Indeedurl)
    print(Web.ScrapeIndeed(Indeedurl))
    
# Test Reed scraping
for Reedurl in Reedurls :
    print(Reedurl)
    print(Web.ScrapeReed(Reedurl))