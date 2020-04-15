# This test utility will allow users to determine the following per engine
# data that requires to be specified in file ..\Data\engines.csv
#
# mailbox
# joburlre
# url_len 
# id_len
# Exclusions
# Inclusions
# 
# The script accepts a number of command line arguments 
# though none are compulsory. The n'th command line argument
# is always interpreted in the same way so if a user requires
# to specify argument n + 1 then values must be entered for all 
# arguments 1 -> n+1. Command line syntax is as follows:
#
# python test_email.py <mail folder> <Job url regular expression> <url length> <exclusion strings> <inclusion strings>
#
# The script will perfom in the following way:
#
# - If no command line argument is specfied the utility will display all e-mail accounts specified in the
#   local instance of Outlook. All top level mail folders and the number of e-mails contained in each of
#   these top level folders will also be displayed.
#
# - If a 'mail folder' arguments is specified all sub-folders defined below this folder will be displayed
#   together with the number of e-mails they contain
#
# - If a 'job url regular expression' is specified all e-mails in the specified folder will be searched for
#   url's matching the regular expression and stored. The user will then be given the choice of whether to
#   jump to these url's to see if a vacancy is displayed.
#
# - If a 'url length' is specified then any urls detected will be truncated to/by the length specified
#   before use.

import win32com.client
import win32com
import sys
import os
import requests
import re
from datetime import date, datetime, timedelta
import subprocess
import time
import Email
import File
import Interface

# File names and modes
Currentdir = os.getcwd()
Datadir = Currentdir + '\\Data'
Errorfilename = Datadir + '\\' + 'log.txt'

# Error levels
error = 'ERROR'
warning = 'WARNING'
info = 'INFO'
log = 'LOG'
module = 'test_email'

# File modes 
append = 'a'
read = 'r'
overwrite = 'w'

# Function return values
invalid = failure = 0
empty = ''

# Mail client detsils.
Outlook = 'OUTLOOK.EXE'
Delay = 7

# Broswer
Browser = 'chrome.exe'
Killdelay = 1

# Assume no exclusion or inclusion strings.
ExclusionsApply = False
InclusionsApply = False

# Command line parsing 
NoOfArgs = len(sys.argv)
if ( NoOfArgs >= 2 ) : FolderArg = sys.argv[1]
if ( NoOfArgs >= 3 ) : ReArg = sys.argv[2]
if ( NoOfArgs >= 4 ) : LenArg = int(sys.argv[3])
if ( NoOfArgs >= 5 ) : 
    ExcArg = sys.argv[4]
    ExclusionsApply = True
    Exclusions = ExcArg.split(':')
if ( NoOfArgs == 6 ) : 
    IncArg = sys.argv[5]
    InclusionsApply = True
    Inclusions = IncArg.split(':')

# Initiate job url list
JoburlList = []

# Create/open log file
ErrorfileObject = File.Open(Errorfilename,append,failure)
Errormessage = 'Could not open ' + Errorfilename
if ( ErrorfileObject == failure ) : File.Logerror(ErrorfileObject,module,Errormessage,error)

# Log start of script
File.Logerror(ErrorfileObject,module,'Started',info)

# Killing outlook process if it exists.
Interface.KillProcess (Outlook,Delay,empty) 

# Progress update
Errormessage = 'Killed any existing instance of %s' % Outlook
File.Logerror(ErrorfileObject,module,Errormessage,info)

# Connect to Outlook
OutlookObj = Email.Mailconnect(invalid)
Errormessage = 'Unable to connect to Outlook'
if ( OutlookObj == invalid ) : File.Logerror(ErrorfileObject,module,Errormessage,error)

# Display e-mail accounts and mail sub-folders defined in Outlook.
OutlookAccounts = Email.Mailaccounts(failure)
for OutlookAccount in OutlookAccounts :

    # Display e-mail account name
    print('Email account %s is defined in the local instance of Outlook ' % OutlookAccount.DisplayName) 
    OutlookFolder = Email.Topfolder(OutlookObj,OutlookAccount,failure)
    
    # Display top level sub-folder detail
    if ( NoOfArgs == 1 ) :
    
        # Print top level sub-folders
        for SubFolder in OutlookFolder.Folders :
            print('Top level folder %s is defined and contains %i e-mail(s)' % (SubFolder.name,(len(SubFolder.Items))))
    else:
    
        # Print details for sub-folder passed as 1st command line argument
        SubFolderDetails = FolderArg.split('/')
        
        for SubFolderDetail in SubFolderDetails :
            OutlookFolder = Email.Subfolder(OutlookFolder.Folders,SubFolderDetail,failure) 
            Errormessage = 'E-mail sub-folder ' + FolderArg + ' does not exist'
            if ( OutlookFolder == failure ) : File.Logerror(ErrorfileObject,module,Errormessage,error)
         
        if ( len(OutlookFolder.Folders) > 0 ) :
            
            # Print sub-folder names and number of e-mails contained in it
            for SubFolder in OutlookFolder.Folders :
                FullSubFolderName = FolderArg + '/' + SubFolder.name
                print('Sub-folder %s contains %i e-mail(s)' % (FullSubFolderName,(len(SubFolder.Items))))
                
        else:
            
            if ( NoOfArgs == 2 ) :
                # Print number of emails in folder.
                print('Sub-folder %s contains %i e-mail(s)' % (FolderArg,(len(OutlookFolder.Items))))
            
            else:
            
                # Store and display matches to ReArg found in e-mail text.  
                Mailnumber = len(OutlookFolder.Items) - 1
                
                while ( Mailnumber >= 0 ) :
                    Message = OutlookFolder.Items[Mailnumber]
                    MessageLines = Message.Body.split('\n')
                    for messageLine in MessageLines :
                        # Apply and exclusion or inclusions.
                        if ( ExclusionsApply ) : 
                            if ( Email.ExcludeLine(messageLine,Exclusions) ) : continue
                        if ( InclusionsApply ) : 
                            if not ( Email.IncludeLine(messageLine,Inclusions) ) : continue
                            
                        MatchObj = re.search(ReArg, messageLine)
                        if MatchObj : 
                            JoburlList.append(MatchObj.group(0))
                            Errormessage = 'LINE -----------> : ' +  messageLine
                            File.Logerror(ErrorfileObject,module,Errormessage,log)
                            Errormessage = 'CONTAINS URL ---> : ' + MatchObj.group(0)
                            File.Logerror(ErrorfileObject,module,Errormessage,log)
                        
                    Mailnumber -= 1
                
                # Remove duplicate matches. This is how parse_mail.py works.
                JoburlSet = set(JoburlList)
                JoburlList = list(JoburlSet)

# Display the contents of any links detected if requested.
if ( len(JoburlList) >= 1 ) :

    # Create list of possible actions.
    Choices = ['y','n','exit']  
    
    for Joburl in JoburlList :
        
        # Set length of the url. 
        if ( NoOfArgs >= 4 ) : Joburl = Joburl[0:LenArg]
        
        # Chose whether or not to see contents of detected link 
        Prompt = 'Do you wish to show contents of link %s length %i %s  : ' % ( Joburl,len(Joburl),str(Choices) )
        Choice = Interface.GetChoice(Prompt,Choices,count = 2)
        
        # Display vacancy.
        if ( Choice == 'y') : Interface.ViewVacancy(Browser,Joburl)
        if ( Choice == 'exit') : break

# Remove vacancy from view
# Interface.KillProcess(Browser,Killdelay,empty)
    
# Log end of script
File.Logerror(ErrorfileObject,module,'Completed',info)

# Close error log file
Errormessage = 'Could not close ' + Errorfilename
if ( File.Close(ErrorfileObject,failure) == failure ) : File.Logerror(ErrorfileObject,module,Errormessage,warning)

