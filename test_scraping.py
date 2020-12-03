# This script tests the web scraping functionality 
# provided in the 'Web' module. 

import re
import requests
import Interface
import Web
import json

# Test data
LinkedInurls = ['https://www.linkedin.com/comm/jobs/view/2268940863','https://www.linkedin.com/jobs/view/2309557960','https://www.linkedin.com/jobs/view/2274720858']
CVLibraryurls = ['https://www.cv-library.co.uk/job/211966039','https://www.cv-library.co.uk/job/212704569','https://www.cv-library.co.uk/job/212560637']
FindAJoburls = ['https://findajob.dwp.gov.uk/details/4914228','https://findajob.dwp.gov.uk/details/4830033']
Indeedurls = ['https://www.indeed.co.uk/rc/clk/dl?jk=ff722d003689dc2d']
#Reedurls = ['https://www.reed.co.uk/jobs/data-engineering-developer/40558764','https://www.reed.co.uk/jobs/operations-platform-engineer/40982898']
Reedurls = ['https://www.reed.co.uk/jobs/data-engineering-developer/40558764','https://www.reed.co.uk/jobs/operations-platform-engineer/40982898','https://www.reed.co.uk/jobs/linux-systems-administrator-devops-engineer/41150293']
Totalurls = ['https://www.totaljobs.com/JobSearch/EmailLink.aspx?JobID=91093673&GUID=adc0e0ad9b034ca29f3d130f8662993d&','https://www.totaljobs.com/JobSearch/EmailLink.aspx?JobID=91130453&GUID=adc0e0ad9b034ca29f3d130f8662993d&']

# Test LinkedIn scraping
#for LinkedInurl in LinkedInurls :
#    print(LinkedInurl)
#    print(Web.ScrapeLinkedIn(LinkedInurl))
#    print(Web.ScrapeLinkedInJson(LinkedInurl))
    
# Test CVLibrary scraping
#for CVLibraryurl in CVLibraryurls :
#    print(CVLibraryurl)
#    print(Web.ScrapeCVLibrary(CVLibraryurl))
    
# Test FindAJob scraping
#for FindAJoburl in FindAJoburls :
#    print(FindAJoburl)
#    print(Web.ScrapeFindAJob(FindAJoburl))
    
# Test FindAJob scraping
#for Indeedurl in Indeedurls :
#    print(Indeedurl)
#    print(Web.ScrapeIndeed(Indeedurl))
    
# Test Reed scraping
#for Reedurl in Reedurls :
#    print(Reedurl)
#    print(Web.ScrapeReed(Reedurl))

# Test Totaljobs scraping
for Totalurl in Totalurls :
    print(Totalurl)
    print(Web.ScrapeTotalJobs(Totalurl))
    