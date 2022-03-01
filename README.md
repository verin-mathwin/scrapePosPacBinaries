# scrapePosPacBinaries
Collection of tools for importing PosPac binary files to pandas dataframes. 
Please note these are offered without guarantee. Always do your own testing.

#scrapeIINCAL
The iincal*.out file holds the lever arm values. As this file will always be present, it's a handy way to check for week or day over-runs in the data as well. This function will return not only the dataframe for this file but also boolan flags that can be applied to the other functions. 

#scrapeIINKARU
innkaru*.out files hold satellite information, as well as PDOP and processing mode information.

#scrapeSEP
Forward/reverse separation can be stored within the trj_sep or gnss_pp_nav_sep files. This module contains a function for each.

#scrapeSMRMSG
RMSEs for the associated trajectory files are stored in the smrmsg*.out file, covering (but not limited to) trajectory, attitude, and velocity errors.

#secsOfWeekToLASTime
A simple function to convert a seconds-of-week value in a dataframe row to LAS time (adjusted GPS).

As noted, these are supplied here without guarantee of accuracy, just the hope that they will be helpful.
