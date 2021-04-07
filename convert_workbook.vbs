  REM This script extracts data from a downloaded Excel file
  REM and stores it in a csv file. This script relies on an
  REM Excel macro to create the csv file.
  
  Dim ExcelApp 
  Dim ExcelBook 
  Dim ScriptObj
  Dim CsvFile 
  Dim ExcelObjType 
  Dim MacroName 

  CsvFile = "C:\JOBSEARCH\2019\Co-Ordination\reports\application_history.csv"
  ExcelObjType = "Excel.Application"
  MacroName1 = "PERSONAL.XLSB!ReformatData"
  MacroName2 = "PERSONAL.XLSB!SaveAsXlsx"
   
  REM Create a new csv file from the excel file
  Set ExcelApp = CreateObject(ExcelObjType) 
  Set ExcelBook = ExcelApp.Workbooks.Open(CsvFile, 0, True) 
  ExcelApp.Run(MacroName1)
  ExcelApp.Run(MacroName2)
  ExcelApp.Quit 

  REM Destroy objects
  Set ExcelBook = Nothing 
  Set ExcelApp = Nothing 