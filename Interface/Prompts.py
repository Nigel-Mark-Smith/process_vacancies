import subprocess
import time

# Prompts the user to make a choice. The user has 'count'
# tries to input one of the choices contained
# in 'list'
def GetChoice (prompt,list,count = 5 ) :

    "Prompts user to make a choice"
    
    abandon = 'User has failed to enter a valid value in %s tries, now exiting' % str(count)
    
    while True : 

        inputStr = input(prompt) 

        try: 
            value = str(inputStr)
        except: 
            count -= 1 
    
        if value in list : 
            return value
        else:
            count -= 1
           
        if ( count == 0 ) :
            print(abandon)
            exit()
    
    
# Prompts for a integer input. The user has 'count'
# tries to input a valid value.
def GetIntinput (prompt,count = 5 ) :

    "Prompts for an integer input"
    
    abandon = 'User has failed to enter a valid value in %s tries, now exiting' % str(count)
    
    while True : 

        inputStr = input(prompt) 

        try: 
            value = int(inputStr)
        except: 
            count -= 1 
        else:
            return value
           
        if ( count == 0 ) :
            print(abandon)
            exit()
            
# Prompts for a string input. The user has 'count'
# tries to input a valid value.
def GetStrinput (prompt,count = 5 ) :

    "Prompts for an integer input"
    
    abandon = 'User has failed to enter a valid value in %s tries, now exiting' % str(count)
    
    while True : 

        inputStr = input(prompt) 

        try: 
            value = str(inputStr)
        except: 
            count -= 1 
        else:
            return value
           
        if ( count == 0 ) :
            print(abandon)
            exit()
            
# Launches browser and displays job vacancy
def ViewVacancy (browser,url) :
 
    "Launches browser and displays job vacancy"
    
    launch = 'start' + ' ' + browser + ' ' + url
    subprocess.run(['cmd.exe','/C',launch])
    
    
# Launches browser and displays job vacancy using temp
# batch file. Required for use with Totaljobs vacancies 
# who's urls contain '&' characters which trip up command 
# line parsing

def ViewVacancyByBatch (browser,url,batch='C:\\temp\\vacancy.bat') :
 
    "Launches browser and displays job vacancy using temp batch file"
    
    # Create command strings
    no_echo = '@echo off' + '\n'
    command = 'start' + ' ' + browser + ' ' + '"' + url + '"' + '\n'
    quit = 'exit' + '\n'
    
    # Write command strings to batch file and close
    file = open(batch,'w')
    file.write(no_echo)
    file.write(command)
    file.write(quit)
    file.close
    
    # Run batch file
    subprocess.call(['cmd.exe','/C','start','/MIN',batch])
        
# Launches spreadsheet program with file argument
def ViewSpeadsheet (spreadsheet,file) :
 
    "Launches spreadsheet program with file argument"
    
    launch = 'start' + ' ' + spreadsheet + ' ' + file
    subprocess.run(['cmd.exe','/C',launch])
    
# Runs script 'script' and waits 'delay' seconds before returning
def RunScript (script,delay) :
 
    "Runs script 'script' and waits 'delay' seconds before returning"
    
    launch = 'start' + ' ' + script
    subprocess.run(['cmd.exe','/C',launch])
    
    time.sleep(delay)  

# Kills process 'process'. 
#
# Note: Waits 'delay' seconds  before returning.
def KillProcess (process,delay,empty) :

    "Kills process 'process'"
    
    Processresult = subprocess.run(['cmd.exe','/C','tasklist /fo csv'],capture_output=True,text=True)
    Processdetails = Processresult.stdout.split('\n')
    
    # Find first process matching string 'process'
    #
    # Note this procedure has only been tested with chrome.
    pid = empty
    for Processdetail in Processdetails :
        values = Processdetail.split(',')
        if ( process in values[0]) : 
            pid = values[1].strip('\"')
            break
    
        
    if ( pid != empty ) :
        Killstring = 'taskkill /pid %s' % pid
        Processresult = subprocess.run(['cmd.exe','/C',Killstring],capture_output=True,text=True)  
    
        # Prevents possible interference with new instance launched by ViewVacancy.
        time.sleep(delay)  

# Displays all standard job details detected for vacancy
def DisplayDetails (details) :        

    "Displays all standard job details detected"
    
    for key in details :
        print('%s : %c %s' % (key,'\t',details[key]))
        

    
    
    
