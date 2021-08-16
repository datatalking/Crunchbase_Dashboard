CREATE EXTERNAL TABLE crunchbase_dashboard.crunchbase_organizations (
  `id` string,
  `uuid` string,
  `company_type` string,
  `founded_on_precision` string,
  `founded_on` string,
  `equity_funding_total` string,
  `equity_funding_total_dup` string,
  `identifier` string,
  `ipo_status` string,
  `category_groups` string,
  `short_description` string,
  `num_investors` string,
  `operating_status` string,
  `num_employees_enum` string,
  `funding_total` string,
  `num_funding_rounds` string,
  `last_equity_funding_type` string,
  `last_funding_type` string,
  `categories` string,
  `location_identifiers` string,
  `last_funding_at` string,
  `last_equity_funding_total` string,
  `funding_stage` string,
  `last_funding_total` string,
  `revenue_range` string,
  `exited_on_precision` string,
  `exited_on` string,
  `valuation` string,
  `investor_type` string,
  `listed_stock_symbol` string,
  `num_funds` string,
  `funds_total` string,
  `num_employees_range` string,
  `location_city` string 
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde' 
WITH SERDEPROPERTIES ("separatorChar" = ",", "quoteChar" = "\"")
STORED AS TEXTFILE 
LOCATION 's3://crunchbase-dashboard/datafile/'
TBLPROPERTIES ('has_encrypted_data'='false','skip.header.line.count'='1');
