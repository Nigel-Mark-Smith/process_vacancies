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
    
    
    
