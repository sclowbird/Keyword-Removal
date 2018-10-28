# How to use keyword removal 

1. Export texts form Workbench.   
Add .xliff input file to "input" folder. 
   
2. Add keywords to keywords.csv, one keyword per line without quotation marks!  (Example keywords in file).
   
3. Open command line in the folder the script is located in.
   
   **!!! No spaces allowed in input file name !!!**

4. Type: `py removelines.py 'filename.xliff'` without quotation marks.

5. Output of the program:

    **"output"-Folder:**

    The first output file is located in the "output"-folder. It contains every id which is necessary
    for the translation. It is the file which is going to be imported to the workbench, after running it through the DataTranslator.

    **"for_translation"-Folder:**

    The second output file is located in the "for_translation"-Folder. In this file all duplicate <source> values has been removed. This file should be sent to the translation bureau.

 6. After getting the translations back from the translations bureau:  
    Import the file in to the translation data base using the DataTranslator tool. 

    **!! IMPORTANT !!** 

    After importing the translations from the translations bureau to the translations database, use the 
    **FIRST** output file located in the "output"-folder for the import in the workbench. Otherwhise IDs are missing in the workbench!
