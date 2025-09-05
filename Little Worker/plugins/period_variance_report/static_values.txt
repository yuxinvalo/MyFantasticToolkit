PVR_ORIGINAL_SQL = """-- Period Variance Report SQL Template
-- Please replace the dates below with actual reporting dates
-- reporting_date_a (last month): {last_month_date}
-- reporting_date_b (prior month): {prior_month_date}
SELECT
    *
FROM
    `datahub.mif_period_variance_report`
WHERE 
    PVRR.reporting_date = '{last_month_date}'
    AND
    PVRR.reporting_date = '{prior_month_date}'"""

EXTRACT_TABLE_NAME_SQL = """SELECT...
    FROM XXX
    WHERE provider_country_code = "{radar_country_code}"
    AND
    reporting_date = "{reporting_date}"
    AND
    group_sys_id = "{radar_group_sys_id}"
    AND
    file_type like 'mif_{column_name_letter}%'"""

GET_BALANCE_SQL = """SELECT CAST(sum({column_name}) AS NUMERIC) FROM DATAHUB.{table_name}"""

GET_EXCEP_BALANCE_SQL = """SELECT count(*) FROM DATAHUB.{table_name}"""

PVR_COL_MAPPINGS = {
    "book_value_in_functional_currency": "G_L_REP_BK_VALUE",
    "clean_economic_value_in_functional_currency": "G_L_REP_PSMRK_MRKT_AMT",
    "accrued_interest_amount_in_functional_currency": "F_L_REP_ACRD_INT", 
    "gross_gl_balance_in_functional_currency": "F_L_REP_EOP_BAL",
    "undrawn_balance_in_functional_currency": "E_L_REP_UNWGHTD_UNDRN_CMMT"
}