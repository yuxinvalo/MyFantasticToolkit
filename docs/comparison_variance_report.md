# Comparison Variance Report
This plugin is used to generate comparison variance report according to user's request. 
Normally, we have to only report UK and HK.     
The data provided from user is usually in excel format, and the UK data is in a single sheet excel file, HK data is in a multiple sheets excel file. These formats are stable.  

## Plugin UI
- A file chooser to choose the UK excel file
- A file chooser to choose the HK excel file
- A editable text area to generate the Bigquery according to excel file. 
- An other file chooser to choose the csv file, the result of bigquery which will be used to do the comparison.
- A log area to show the comparison steps.
- A dropdown list to choose the report format
- A button to generate the report

## Excel Format
For UK, it's in a single sheet excel file, the sheet name is not sure, just read it directly.
For HK, it's in a multiple sheets excel file, the sheet name is "HK".

These 2 types of excel file contains same columns:   
1. Reporting Date
2. Country
3. Frequency
4. Group System ID
5. Group Sub System ID
6. Record Type
7. Rule ID
8. Rule Action
9. Source Table Name
10. Dictionary Reference
11. Source Column Name
12. Source Column Rule
13. Output Table Name
14. Output Column Name
15. Output Column Rule
16. Variance
17. Status
18. Filter
19. Stat
20. Check Type
21. Creation Date
22. Run UUID
23. Group Run UUID
24. Batch Token Key

Indeed, we only use Reporting Date, Country, Frequency, Group Sub System ID, Record Type, Source Table Name, Source Column Rule, Output Table Name, Output Column Rule, Variance, Status, to generate biqury.

## Bigquery Format
The bigquery format example is as follows:
```
SELECT
  reporting_date,
  file_freq,
  radar_country_code,
  radar_group_sys_id,
  radar_group_sub_sys_id,
  rule_action,
  table_name_source,
  col_source,
  source_col_rule,
  table_name_output,
  col_output,
  status,
  filter,
  stat, 
  check_type
  
FROM
  `hsbc-xxx-radar-prod.TABLE_NAME_REPORT_V01_00`
WHERE
  reporting_date = '<DATE>'  # For example 2025-07-31
  AND radar_country_code in ('GB','HK')
  AND file_freq = '<FREQ>'
  AND upper(record_type) in upper(<UNIQ_RECORD_TYPE_LIST>) 
  AND radar_group_sub_sys_id in (<UNIQ_GROUP_SUB_SYS_ID_LIST>)
  AND table_name_source in (<UNIQ_SOURCE_TABLE_NAME_LIST>)
  AND table_name_output in (<UNIQ_OUTPUT_TABLE_NAME_LIST>);
```
## Process
1. Read the UK,HK as pandas, as type "str"
2. Remove all the line which Country is not "GB" or "HK"
3. Remove all the line which Variance is in "-", "0", None, ""
4. Generate the Bigquery SQL according to the UK,HK data and the description above.
5. Waiting for the user select the downloaded csv file, and read it as pandas.
6. Compare the csv file with original UK,HK data, showing the comparison steps in log. For example, comparing the Source Column Rule and Output Column Rule for UK, status = 0...
7. Waiting for user input the report format and click generate report button.
8. Generate the report

### How to compare data?
1. Filter UK, HK data by Status = 0, 1 sequencely
2. Compare, for the same Group System ID, Group Subsystem Id, Record Type, Rule ID, Source Table Name, Source Column Name, Source Column Rule and Output Table Name, the CSV data has the same Output Column Rule.
3. Generate CSV file, the file name is CVR_{Country}_{Status}_{Reporting Date}_{YYMMDDHH}.csv
4. Repeat step 1, 2, 3 for HK data, the file name is CVR_{Country}_{Status}_{Reporting Date}_{YYMMDDHH}.csv
5. Read the 4 csv files, and compare the data, generate the report.


## Report Format
After click the generate button, the report will be generated according to selected format. 
Only 2 type formats are supported:
1. HTML
2. Docx

### Report Content
We are supposed to generate 2 reports, UK and HK. 
For each report, we need to compare the output csv from gcp, for status(Original Excel) = 0, compare the Source Column Rule and Output Column Rule for each same line.

For each same line, we need to show the comparison, and highlight or text the column Output Column Rule, add a mark if the values are different for this column below. 

The same as status = 1. 

So, there will be 4 sections in the same textual file regarding the final report, 
1. UK, status = 0
2. UK, status = 1
3. HK, status = 0
4. HK, status = 1

### Output
- HTML name: reports/CVR_{Reporting Date}_{YYMMDDHH}.html
- Docx name: reports/CVR_{Reporting Date}_{YYMMDDHH}.docx
- Csv name: reports/CVR_{Country}_{Status}_{Reporting Date}_{YYMMDDHH}.csv

The plugin is supposed to export also a csv file with name reports/CVR_{Reporting Date}_{YYMMDDHH}.csv, the format is as follows:
1. Country
2. GCP_Country
3. Group System ID
4. GCP_Group System ID
5. Group Sub System ID
6. GCP_Group Sub System ID
7. Record Type
8. GCP_Record Type
9. Rule ID
10. GCP_Rule ID
13. Source Table Name
14. GCP_Source Table Name
17. Source Column Rule
18. GCP_Source Column Rule
19. Output Table Name
20. GCP_Output Table Name
23. Output Column Rule
24. GCP_Output Column Rule
25. Variance
26. GCP_Variance
27. Status
28. GCP_Status





