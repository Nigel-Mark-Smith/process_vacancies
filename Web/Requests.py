import re
import requests
import Interface
import json

# This procedure will find the Reed Job ID and Job url.
# It is necessary to scrape web content to find this 
# information    
def FindReedID (url,urlre) :

    "Finds the Job ID and url for Reed engine vacancies"
       
    # Retrieve javascript text
    Httpresponse = requests.get(url)
    Httplines = Httpresponse.text.split('\n')

    # Search for joburl in javascript
    for Httpline in Httplines :
    
        Httpmatch = re.search(urlre,Httpline)
        if Httpmatch : break
      
    return Httpmatch.group(0)
    
# This procedure scrapes additional json encoded job data from the 
# web site
def ScrapeLinkedInJson (url) :

    "scrapes additional json encoded job data from the web site"
    
    # Dictionary to hold standard job data.
    StandardData = {}
    StandardDataKeys = ['company','title','location','salary_min','salary_max']
    
    # Request http content and convert to character stream 
    Httpresponse = requests.get(url)
    Httpcontent = Httpresponse.text.replace('\n','')
        
    # Extract JSON encoded data
    Httpmatch = re.search('<script type=\"application\/ld\+json\">(.*?)</script>',Httpcontent)
    if Httpmatch : JobData = json.loads(Httpmatch.group(1))
      
    # Populate standard data dictionary
    StandardData['company'] = JobData['hiringOrganization']['name']
    StandardData['title'] = JobData['title']
    StandardData['location'] = JobData['jobLocation']['address']['addressLocality']
    StandardData['salary_min'] = 0
    StandardData['salary_max'] = 0
    
    return StandardData
    
# This procedure scrapes additional job data from the 
# web site
def ScrapeLinkedIn (url) :

    "scrapes additional job data from the web site"

    # Matrices for converting raw job data to standard job data. 
    ConversionDict = {'company':['company'],'title':['title'],'location':['location'],'salary_min':['salary'],'salary_max':['salary']}

    # set regular expressions
    titlere = 'class=\"topcard__title">(.+?)<'
    attributere = 'topcard__flavor(''|--bullet|--closed)\">(.*?)<'
    companyre = 'sub-nav-cta__optional-url\"title=\"(.*?)\"'
    locationre = '<span class=\"job-result-card__location\">(\D+?)</span><time class=\"job-result-card'
    
    # Retrieve web text
    Httpresponse = requests.get(url)
    Httplines = Httpresponse.text.split('\n')
       
    # Search for job title and other job attributes
    EngineJobData = {}
    ProcessedJobData = {}
    Attributevalues = []
    Altcompany = ''
    Altlocation = ''

    for Httpline in Httplines : 
        #print(Httpline)
        Httpmatch = re.search(locationre,Httpline)
        if Httpmatch: Altlocation = Httpmatch.group(1)
        Httpmatch = re.search(titlere,Httpline)
        if Httpmatch: EngineJobData['title'] = Httpmatch.group(1)
        Httpmatch = re.search(companyre,Httpline)
        if Httpmatch: Altcompany = Httpmatch.group(1)
        Httpmatch = re.findall(attributere,Httpline)
        if Httpmatch: Attributevalues = Httpmatch
        
    # General protection against scraping failure.
    if ( len(Attributevalues) == 0 ) : return ProcessedJobData
     
    # Checked if job closed. The following additional attribute key/value pair will
    # be detected if it is.
    #
    # ('--closed', ''), ('--closed', 'No longer accepting applications')
    Attributekeys = ['company','location']
    if ( len(Attributevalues) > len(Attributekeys) ) : return ProcessedJobData
    
    # Create a distionary of job atributes
    Attributeindex = 0 
    while ( Attributeindex < len(Attributekeys) ) :
        EngineJobData[Attributekeys[Attributeindex]] = Attributevalues[Attributeindex][1]
        Attributeindex += 1

    # Convert raw job data to standard job data
    for StandardDataKey in ConversionDict : 
        StandardDataValue = ''
        for EngineDataKey in ConversionDict[StandardDataKey] : 
            if EngineDataKey in EngineJobData : StandardDataValue = StandardDataValue + EngineJobData[EngineDataKey] + ','
        
        ProcessedJobData[StandardDataKey] = StandardDataValue.rstrip(',')
    
    # Set salary values.  
    ProcessedJobData['salary_min'] = 0
    ProcessedJobData['salary_max'] = 0
    
    # Fill in any blank company and location data
    if ( len(ProcessedJobData['company']) == 0 ) : ProcessedJobData['company'] = Altcompany
    if ( len(ProcessedJobData['location']) == 0 ) : ProcessedJobData['location'] = Altlocation
    
    return ProcessedJobData
    
# This procedure scrapes additional job data from the 
# web site
def ScrapeCVLibrary (url) :

    "scrapes additional job data from the web site"
    
    # Matrices for converting raw job data to standard job data. 
    ConversionDict = {'company':['JOB_COMPANY_NAME'],'title':['JOB_TITLE'],'location':['JOB_TOWN','JOB_COUNTY'],'salary_min':['JOB_SALARY'],'salary_max':['JOB_SALARY']} 

    # set regular expressions
    attributesre = 'dataLayer\.push\(\{(.*?)\}\)'

    # Retrieve web text
    Httpresponse = requests.get(url)
    Httplines = Httpresponse.text.split('\n')

    # Search for required job data
    # in web text
    for Httpline in Httplines :  
        Httpmatch = re.search(attributesre,Httpline)
        if Httpmatch : break

    # Process data line              
    JobAttributes = Httpmatch.group(1)
    JobAttributes = JobAttributes.replace('\"','')
    JobAttributes = JobAttributes.split(',')
    
    # Convert engine job attributes into key value pairs
    EngineJobData = {}
    for JobAttribute in JobAttributes : 
        # It's possible that data doesn't follow <key>:<value> format.
        if ':' in JobAttribute :
            AttributePair = JobAttribute.split(':')
            EngineJobData[AttributePair[0]] = AttributePair[1]
    
    # Convert raw job data to standard job data
    ProcessedJobData = {}
    for StandardDataKey in ConversionDict : 
        StandardDataValue = ''
        for EngineDataKey in ConversionDict[StandardDataKey] : 
            if EngineDataKey in EngineJobData : StandardDataValue = StandardDataValue + EngineJobData[EngineDataKey] + ','
        
        ProcessedJobData[StandardDataKey] = StandardDataValue.rstrip(',')
        
    # Convert salary strings.  
    # LinkedIn does not display salaries in a consistent location
    SalaryValues = Interface.Extractsalarydata(ProcessedJobData['salary_min'])
    ProcessedJobData['salary_min'] = int(SalaryValues[0])
    ProcessedJobData['salary_max'] = int(SalaryValues[1])
         
    return ProcessedJobData
    
# This procedure scrapes additional job data from the 
# web site
def ScrapeFindAJob (url) :

    "scrapes additional job data from the web site"
    
    # Dictionary to hold standard job data.
    StandardData = {}
    StandardDataKeys = ['company','title','location','salary_min','salary_max']
    
    # Request http content and convert to character stream 
    Httpresponse = requests.get(url)
    Httpcontent = Httpresponse.text.replace('\n','')
    
    # Extract web data. Note job details are provided encoded in JSON format
    Httpmatch = re.search('<script type=\"application\/ld\+json\">(.*?)</script>',Httpcontent)
    if Httpmatch : 
        JobData = json.loads(Httpmatch.group(1))
    else :
        return StandardData
         
    # Populate standard data dictionary
    StandardData['company'] = JobData['hiringOrganization']
    StandardData['title'] = JobData['title']
    StandardData['location'] = JobData['jobLocation']['address']
    StandardData['salary_min'] = 0
    StandardData['salary_max'] = 0
    
    # Salary data for post
    if ( JobData['baseSalary']['currency'] == 'GBP' ) :
        if 'minValue' in JobData['baseSalary'] : 
            StandardData['salary_min'] = int(JobData['baseSalary']['minValue'])
            if 'maxValue' in JobData['baseSalary'] : 
                StandardData['salary_max'] = int(JobData['baseSalary']['maxValue'])
            else:
                StandardData['salary_max'] = int(JobData['baseSalary']['minValue'])
    
    return StandardData
    
# This procedure scrapes additional job data from the 
# web site
def ScrapeIndeed (url) :

    "scrapes additional job data from the web site"
    
    # Matrices for converting raw job data to standard job data. 
    ConversionDict = {'company':['company'],'title':['title'],'location':['location'],'salary_min':['salary'],'salary_max':['salary']} 

    # set regular expressions
    titlere = 'jobsearch-JobInfoHeader-title\">(.*?)<'
    valuere = '\"jobsearch-JobMetadataHeader-iconLabel\">(.*?)<'   
    # valuere ='icl-u-xs-m[rt]--xs\">(.*?)<'
    # The above may work on some Indeed job adverts however
    # the display code looks too unstable to warrant any changes.
    keyre = 'icl-IconFunctional--(.*?) icl'

    # Retrieve web text
    Httpresponse = requests.get(url)
    Httplines = Httpresponse.text.split('\n')

    # Search for job title and other job attributes
    EngineJobData = {}
    Attributekeys = []
    Attributevalues = []

    for Httpline in Httplines : 
        # if 'title' in Httpline : print(Httpline)
        Httpmatch = re.search(titlere,Httpline)
        if Httpmatch: EngineJobData['title'] =  Httpmatch.group(1)
        Httpmatch = re.findall(keyre,Httpline)
        if Httpmatch: Attributekeys = Httpmatch
        Httpmatch = re.findall(valuere,Httpline)
        if Httpmatch: Attributevalues = Httpmatch
     
    # Create a distionary of job atributes
    Attributeindex = 0

    while ( Attributeindex < len(Attributekeys) ) :
        EngineJobData[Attributekeys[Attributeindex]] = Attributevalues[Attributeindex]
        Attributeindex += 1

    # Convert raw job data to standard job data
    ProcessedJobData = {}
    for StandardDataKey in ConversionDict : 
        StandardDataValue = ''
        for EngineDataKey in ConversionDict[StandardDataKey] : 
            if EngineDataKey in EngineJobData : StandardDataValue = StandardDataValue + EngineJobData[EngineDataKey] + ','
        
        ProcessedJobData[StandardDataKey] = StandardDataValue.rstrip(',')
        
    # Convert salary strings.  
    SalaryValues = Interface.Extractsalarydata(ProcessedJobData['salary_min'])
    ProcessedJobData['salary_min'] = int(SalaryValues[0])
    ProcessedJobData['salary_max'] = int(SalaryValues[1])
    
    return ProcessedJobData
    
# This procedure scrapes additional job data from the 
# web site
def ScrapeReed (url) :

    "scrapes additional job data from the web site"
    
    # Matrices for converting raw job data to standard job data. 
    ConversionDict = {'company':['company'],'title':['title'],'location':['locality','region'],'salary_min':['salary'],'salary_max':['salary']} 

    # set regular expressions
    titlere = '<meta itemprop=\"title\" content=\"(.*?)\" />'
    companyre = '<span itemprop=\"name\">(.*?)<'
    keyre = '<span\s*data-qa=\"(.*?)MobileLbl\"\s*>'
    valuere = '<span\s*data-qa=\"(.*?)MobileLbl\"\s*>(.*?)<'
    expiredre = 'The following job is no longer available'

    # Retrieve web text
    Httpresponse = requests.get(url)
    Httplines = Httpresponse.text.split('\n')

    # Search for job title and other job attributes
    EngineJobData = {}
    Attributekeys = []
    Attributevalues = []
    ProcessedJobData = {}
    JobExpired = False

    for Httpline in Httplines : 
        Httpmatch = re.search(titlere,Httpline)
        if Httpmatch: EngineJobData['title'] =  Httpmatch.group(1)
        Httpmatch = re.search(companyre,Httpline)
        if Httpmatch: EngineJobData['company'] =  Httpmatch.group(1)
        Httpmatch = re.search(keyre,Httpline)
        if Httpmatch: Attributekeys.append(Httpmatch.group(1))
        Httpmatch = re.search(valuere,Httpline)
        if Httpmatch: Attributevalues.append(Httpmatch.group(2))
        Httpmatch = re.search(expiredre,Httpline)
        if Httpmatch: JobExpired = True
        
    # Return with no data if job is expired
    if ( JobExpired ) : return ProcessedJobData
    
    # Create a distionary of job atributes
    Attributeindex = 0

    while ( Attributeindex < len(Attributekeys) ) :
        EngineJobData[Attributekeys[Attributeindex]] = Attributevalues[Attributeindex]
        Attributeindex += 1
    
    # Convert raw job data to standard job data  
    for StandardDataKey in ConversionDict : 
        StandardDataValue = ''
        for EngineDataKey in ConversionDict[StandardDataKey] : 
            if EngineDataKey in EngineJobData : StandardDataValue = StandardDataValue + EngineJobData[EngineDataKey] + ','
        
        ProcessedJobData[StandardDataKey] = StandardDataValue.rstrip(',')
        
    # Convert salary strings.  
    SalaryValues = Interface.Extractsalarydata(ProcessedJobData['salary_min'])
    ProcessedJobData['salary_min'] = int(SalaryValues[0])
    ProcessedJobData['salary_max'] = int(SalaryValues[1])
    
    return ProcessedJobData
    
# This procedure scrapes additional job data from the 
# web site
def ScrapeTotalJobs (url) :

    # Dictionary to hold standard job data.
    StandardData = {}
    StandardDataKeys = ['company','title','location','salary_min','salary_max']
        
    # Populate dictionary holding regular expressions used to extract job data from web.
    WebFieldRes = {}
    WebFieldRes['title'] = '<h1 class=\"brand-font\">(.*?)</h1>'
    WebFieldRes['location'] = '<li class=\"location icon\">(.*?)</li>'
    WebFieldRes['commute'] = 'locationText\">.*?<ul>.*?<li>(.*?)</li'
    WebFieldRes['salary'] = '<li class=\"salary icon\">.*?<div>(.*?)</div>'
    WebFieldRes['company'] = '<li class="company icon">.*?\"View jobs\">(.*?)</a>.*?</li>'
    WebFieldRes['job_type'] = '<li class=\"job-type icon\">.*?<div>(.*?)</div>'
    WebFieldRes['expiry'] = '<li class=\"date-posted icon\">.*?<span>(.*?)</span>'
    
    # Request http content and convert to character stream 
    Httpresponse = requests.get(url)
    Httpcontent = Httpresponse.text.replace('\n','')
    
    # Dictionary to hold web job data
    WebData = {}
    for WebFieldRe in WebFieldRes : WebData[WebFieldRe] = ''
    
    # Extract web data
    for WebFieldRe in WebFieldRes :
        Httpmatch = re.search(WebFieldRes[WebFieldRe],Httpcontent)
        if Httpmatch: 
            WebData[WebFieldRe] = Httpmatch.group(1).strip()
            Httpcontent = Httpcontent[Httpmatch.end(1):]
            
    # Return an empty dictionary of data if the job has expired. 
    if ( WebData['expiry'] == 'Expired' ) : return StandardData
    
    # Populate standard data dictionary
    StandardData['company'] = WebData['company']
    StandardData['title'] = WebData['title']
    
    # Standard location value needs to be derived from one of two web values
    Location = ''
    
    if ( len(WebData['location']) != 0 ) :   
        LocationParts = re.findall('class=\"engagement-metric\">(.*?)<',WebData['location'])
    else: 
        LocationParts = re.findall('class=\"engagement-metric\">(.*?)<',WebData['commute'])
        if not LocationParts :
            LocationParts = WebData['commute'].split(',')
            
    # Create location string.
    if LocationParts :
        for LocationPart in LocationParts :
            Location = Location + ',' + LocationPart
            StandardData['location'] = Location.lstrip(',')
       
    # Standard salary values need deriving form web value.
    SalaryValues = Interface.Extractsalarydata(WebData['salary'])
    StandardData['salary_min'] = int(SalaryValues[0])
    StandardData['salary_max'] = int(SalaryValues[1])
   
    return StandardData