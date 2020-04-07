import re

# This procedure will extract maximum and minimum salary data
# from string 'salary'. If no data exists value 'default' is  
# returned for both maximum and minimum salary
def Extractsalarydata (salary,default=0) :

    "Extracts maximum and minimum salary data"
    
    # Initialize salary data
    salarydata = [default,default]
    
    # Set regular expression for salary values
    ammountre = '[^.]£?([1-9]{1}[0-9]*,?[0-9]+)'
    
    # Set regular expersion data for salary periods or salary units. 
    # Salary values should all be expressed as annual amounts.
    periodres = ((r'[Aa]nnum',1),(r'[Yy](ear|r)',1),(r'[Dd](ay)',365),(r'[Hh](our|r)',1800),(r'[Kk]',1000))
    ammountmultiplier = 1
    
    # Determine salary amounts, unit multipliers and time periods.
    if ( len(salary) != 0 ) :
        ammountmatch = re.findall(ammountre,salary)
        for periodre,multiplier in periodres :
            periodmatch = re.search(periodre,salary)
            if periodmatch : 
                ammountmultiplier = multiplier
                break

        # Insert salary value in salarydata
        valueindex = 0
        value = default
        
        while ( valueindex < len(salarydata) ) :  
            if ( valueindex < len(ammountmatch) ) : value = int(ammountmatch[valueindex].replace(',','')) * ammountmultiplier 
            salarydata[valueindex] = value
            valueindex += 1
        
        
    return salarydata   