import re
import requests
import Interface

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

# This procedure scrapes additional job data from the 
# web site
def ScrapeLinkedIn (url) :

    "scrapes additional job data from the web site"

    # Matrices for converting raw job data to standard job data. 
    ConversionDict = {'company':['company'],'title':['title'],'location':['location'],'salary_min':['salary'],'salary_max':['salary']}

    # set regular expressions
    titlere = 'class=\"topcard__title">(.+?)<'
    attributere = 'topcard__flavor(''|--bullet|--closed)\">(.*?)<'
    companyre = 'sub-nav-cta__optional-url\"title=\"(\D+?)"'
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
        Httpmatch = re.search(locationre,Httpline)
        if Httpmatch: Altlocation = Httpmatch.group(1)
        Httpmatch = re.search(titlere,Httpline)
        if Httpmatch: EngineJobData['title'] = Httpmatch.group(1)
        Httpmatch = re.search(companyre,Httpline)
        if Httpmatch: Altcompany = Httpmatch.group(1)
        Httpmatch = re.findall(attributere,Httpline)
        if Httpmatch: Attributevalues = Httpmatch
     
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
    
    # Matrices for converting raw job data to standard job data. 
    ConversionDict = {'company':['Company:'],'title':['Title:'],'location':['Location:'],'salary_min':['Salary:'],'salary_max':['Salary:']} 

    # set regular expressions
    titlere = '<title>(.*?)<'
    attributere = '<t([h,d])(.*?)\"govuk-table(.*?)>(.*?)<(.*?)>'

    Httpresponse = requests.get(url)
    Httplines = Httpresponse.text.split('\n')

    # Search for job title in web text
    EngineJobData = {}

    for Httpline in Httplines : 
        Httpmatch = re.search(titlere,Httpline)
        if Httpmatch:
            EngineJobData['Title:'] =  Httpmatch.group(1)

    # Search for remaining job data in web text
    Attributekeys = []
    Attributevalues = []

    for Httpline in Httplines :  

        Httpmatch = re.search(attributere,Httpline)
        if Httpmatch:
            if ( Httpmatch.group(1) == 'h' ) : 
                Attributekeys.append(Httpmatch.group(4))
            else:
                Attributevalues.append(Httpmatch.group(4))

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
def ScrapeIndeed (url) :

    "scrapes additional job data from the web site"
    
    # Matrices for converting raw job data to standard job data. 
    ConversionDict = {'company':['company'],'title':['title'],'location':['location'],'salary_min':['salary'],'salary_max':['salary']} 

    # set regular expressions
    titlere = 'jobsearch-JobInfoHeader-title\">(.*?)<'
    valuere = '\"jobsearch-JobMetadataHeader-iconLabel\">(.*?)<'
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
    keyre = '<span\s*data-qa=\"(.*?)MobileLbl\"\s*>'
    valuere = '<span\s*data-qa=\"(.*?)MobileLbl\"\s*>(.*?)<'

    # Retrieve web text
    Httpresponse = requests.get(url)
    Httplines = Httpresponse.text.split('\n')

    # Search for job title and other job attributes
    EngineJobData = {}
    Attributekeys = []
    Attributevalues = []

    for Httpline in Httplines : 
        Httpmatch = re.search(titlere,Httpline)
        if Httpmatch: EngineJobData['title'] =  Httpmatch.group(1)
        Httpmatch = re.search(keyre,Httpline)
        if Httpmatch: Attributekeys.append(Httpmatch.group(1))
        Httpmatch = re.search(valuere,Httpline)
        if Httpmatch: Attributevalues.append(Httpmatch.group(2))
    
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