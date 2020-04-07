import win32com.client
import win32com
import sys
import os
import requests
import re
from datetime import date, datetime, timedelta


# Connect to Outlook
def Mailconnect (failure):

    "Connect to Outlook"
    
    try:
        outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    except:
        return failure
    else:
        return outlook
        
        
# Return Outlook accounts
def Mailaccounts (failure):

    "Return Outlook accounts"
    
    try:
        accounts = win32com.client.Dispatch("Outlook.Application").Session.Accounts;
    except:
        return failure
    else:
        return accounts
        
# Find Outlook account
def Findaccount (accounts,name,failure):

    "Find Outlook accounts"
    
    result = failure
    for account in ( accounts ) : 
        if ( account.DisplayName == name ) : result = account
    
    return result
    
# Find top level folder
def Topfolder (outlook,account,failure):

    "Find top level folder"
    
    try:
        folder = outlook.Folders(account.DeliveryStore.DisplayName)
    except:
        return failure
    else: 
        return folder

# Find sub level folder
def Subfolder (folders,name,failure):

    "Find sub level folder"
    
    result = failure
    for folder in (folders):
        if ( folder.name == name ) :
            result = folder
            break
        
    return result
         
    
# Determine if mail is less than 'agelimit' seconds old
def Isrecent (received,agelimit,failure):

    "Determine if mail is less than 'agelimit' seconds old"
    
    # Processing Outlook date stamp which looks like:
    # '2020-03-08 16:32:59+00:00'
    pattern = '%Y-%m-%d %H:%M:%S'
    received = received.split('+')[0]
    received = datetime.strptime(received,pattern)
    
    # Calculating how old mail is in seconds
    current = datetime.now()
    value = current - received
    value = value.total_seconds()
    
    # Check if e-mail too old
    if ( value > agelimit ) : value = failure
    
    return value
    
# Determines if a line should be excluded 
# in a search for job urls
def ExcludeLine (line,exclusions) :

    "Determines if a line should be excluded in a search for job urls"
    
    value = False
    
    for exclusion in exclusions :
        if exclusion in line:
            value = True
            break
            
    return value
    
# Determines if a line should be included 
# in a search for job urls
def IncludeLine (line,inclusions) :

    "Determines if a line should be included in a search for job urls"
    
    value = False
    
    for inclusion in inclusions:
        if inclusion in line:
            value = True
            break
            
    return value
    
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
    