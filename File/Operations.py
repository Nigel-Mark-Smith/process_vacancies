import time
import sys

# Opens a file
def Open (filename,mode,failure):
    
    "Opens a file"

    try:
        fo = open(filename,mode)
    except:
        return failure
    else:
        return fo
      

# Closes a file      
def Close (Fileobject,failure):
    
    "Closes a file"

    try:
        Fileobject.close()
    except:
        return failure

# Read contents of a file      
def Read (Fileobject,failure):
    
    "Closes a file"

    try:
        contents = Fileobject.read()
    except:
        return failure
    else:
        return contents
        
# Reads a line from a file      
def Readline (Fileobject,failure):
    
    "Reads a line from a file"

    try:
        line = Fileobject.readline()      
    except:
        return failure
    else:
        return line
        
# Writes buffer to a file      
def Write (Fileobject,buffer,failure):
    
    "Writes line to a file"

    try:
        Fileobject.write(buffer)      
    except:
        return failure
    else:
        return True
        
# Writes a line to a file      
def Writeline (Fileobject,line,failure):
    
    "Writes line to a file"

    try:
        Fileobject.writelines(line)      
    except:
        return failure
    else:
        return line
        
# Write error log entry. The program will exit if the error level
# is 'error'
def Logerror (Fileobject,module,text,level):

    "Write an entry in the error log"
    
    timestamp = time.asctime( time.localtime(time.time()) )
    message = timestamp + ' ' + level + ': ' +  module + ': ' + text
    
    try:
        Fileobject.writelines('%s%s' % ( message,'\n') )
    except:
        print ('Unable to log %s%s%s' % ('\"',message,'\"') )
        sys.exit()
    else:
        if ( level != 'LOG' ) : print ('%s' % message )
        if ( level == 'ERROR' ) : sys.exit()

# Splits a line in a CSV file into a list of
# values.      
def SplitCSVline (line,failure):
    
    "Splits a line in a CSV file into a list of values"
    
    # Remove newline and space characters
    line = line.replace('\n','')
    line = line.replace(' ','')

    try:
        result = line.split(',')      
    except:
        result = failure
    finally:
        return result
    
    