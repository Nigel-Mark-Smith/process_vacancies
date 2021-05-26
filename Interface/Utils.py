import re

# This procedure will extract maximum and minimum salary data
# from string 'string'. If no data exists value 'default' is  
# returned for both maximum and minimum salary
def Extractsalarydata (string,default=0) :

    "Extracts maximum and minimum salary data"
    
    # Initialize salary data
    salarydata = [default,default]

    # Set regular expression for salary values
    #amountre = '[^.]£?([1-9]{1}[0-9]*,?[0-9]+)'
    amountre = '£?([1-9]{1}[0-9]*,?[0-9]+)'
    
    # Translate utf-8 character string to '£' if required
    salary = re.sub('&#163;','£',string)
    
    # Set regular expersion data for salary periods or salary units. 
    # Salary values should all be expressed as annual amounts.
    #periodres = ((r'[\d ][Kk][ $]',1000),(r'[Aa]nnum',1),(r'[Yy](ear|r)',1),(r'[Dd](ay)',365),(r'[Hh](our|r)',1800))
    periodres = ((r'[Aa]nnum',1),(r'[\d ][Kk]\W*',1000),(r'[Yy](ear|r)',1),(r'[Dd](ay)',365),(r'[Hh](our|r)',1800))
    amountmultiplier = 1
    
    # Determine salary amounts, unit multipliers and time periods.
    if ( len(salary) != 0 ) :
        amountmatch = re.findall(amountre,salary)
        for periodre,multiplier in periodres :
            periodmatch = re.search(periodre,salary)
            if periodmatch : 
                amountmultiplier = multiplier
                break

        # Insert salary value in salarydata
        valueindex = 0
        value = default
        
        while ( valueindex < len(salarydata) ) :  
            if ( valueindex < len(amountmatch) ) : value = int(amountmatch[valueindex].replace(',','')) * amountmultiplier 
            salarydata[valueindex] = value
            valueindex += 1
        
        
    return salarydata   