#!/usr/bin/env python
# coding: utf-8

# # Crunchbase API: Companies in Orange County

# Sources:
# - https://medium.com/priyanshumadan/extract-data-from-crunchbase-api-using-python-8e99ed6bc73e
# - https://app.swaggerhub.com/apis-docs/Crunchbase/crunchbase-enterprise_api/1.0.3#/
# - https://data.crunchbase.com/docs/examples-autocomplete-api 

# ### Setup

# In[1]:


import requests
import pandas as pd
import boto3
import sys
import json
import csv
import getopt
from pandas.io.json import json_normalize 
from operator import itemgetter
from datetime import datetime, date, time

# Parse input arguements

#def main(argv):
 #  arg_aws_access_key_id = str(sys.argv[1])
 #  arg_aws_secret_access_key = str(sys.argv[2])
 #  arg_region_name = str(sys.argv[3])

   
def get_date():
    now = datetime.now()
    date = str(now.strftime('%Y-%m-%d'))
    return date 

def csv_to_list(file_path,column_names,col_name):
    # Read in CSV file with city names and their corresponding UUIDs
    df = pd.read_csv(file_path, names=column_names)
    # Make a list of the column of interest and remove the first string, which is the column name
    transformed_list = df[col_name].to_list()
    transformed_list.pop(0)
    return transformed_list

# Create lists of cities and category groups (organization industries) to use as a filter in query
city_uuids = csv_to_list('cities_uuids.csv',["City", "UUID"],"UUID")
city_names = csv_to_list('cities_uuids.csv',["City", "UUID"],"City")
categories_uuids = csv_to_list('categories_uuids_new.csv',["Category", "UUID"],"UUID")
categories_names = csv_to_list('categories_uuids_new.csv',["Category", "UUID"],"Category")


# ### Define keys/URLs

# In[2]:


funding_url = str(sys.argv[1])
orgs_url = str(sys.argv[2])
userkey = {'user_key': str(sys.argv[3])}


# ### Queries

# In[3]:


def query_function(last_uuid,queryType):
    if queryType == "orgs":
        query = {
            "field_ids": [
            "identifier",
            "entity_def_id",
            "location_identifiers",
            "short_description",
            "company_type",
            "categories",
            "category_groups",
            "equity_funding_total",
            "exited_on",
            "founded_on",
            "funding_stage",
            "funding_total",
            "funds_total",
            "investor_stage", # this will tell us the stage of investments made by this organization
            "investor_type", # describes the type of investor this organization
            "ipo_status",
            "last_equity_funding_total",
            "last_equity_funding_type",
            "last_funding_at",
            "last_funding_total",
            "last_funding_type",
            "listed_stock_symbol",
            "location_group_identifiers",
            "location_identifiers", # where the organization is headquartered. value and location_type of interest in identifier
            "num_employees_enum",
            "num_funding_rounds",
            "num_funds",
            "num_investors",
            "operating_status",
            "revenue_range",
            "valuation",
            "operating_status",
            "uuid"
            ],
            "query": [
                {"type": "predicate",
                "field_id": "location_identifiers",
                "operator_id": "includes",
                "values": city_uuids
                },
                {"type": "predicate",
                "field_id": "facet_ids",
                "operator_id": "includes",
                "values": ["company"]
                },
                {"type": "predicate",
                "field_id": "category_groups",
                "operator_id": "includes",
                "values": categories_uuids}
                ],
            'limit': 1000
            }
    elif queryType == "funding":
        print("...")
        query = {
            "field_ids": [
                "identifier",
                "entity_def_id",
                "announced_on",
                "closed_on",
                "created_at"
                "funded_organization_categories",
                "funded_organization_description",
                "funded_organization_funding_stage",
                "funded_organization_funding_total",
                "funded_organization_identifier",
                "funded_organization_location",
                "funded_organization_revenue_range",
                "investment_stage",
                "investment_type",
                "investor_identifiers",
                "is_equity",
                "lead_investor_identifiers"
                "money_raised",
                "name",
                "num_investors",
                "num_partners",
                "post_money_valuation",
                "pre_money_valuation",
                "rank_funding_round",
                "short_description",
                "target_money_raised",
                "uuid"
                ],
            "query": [
                {"type": "predicate",
                "field_id": "funded_organization_location",
                "operator_id": "includes",
                "values": city_uuids,
                 }
                # this can be updated to filter by 
#                 {"type": "predicate",
#                 "field_id": "funded_organization_categories",
#                 "operator_id": "includes",
#                 "values": categories_uuids
#                 "values": ["software",]}
                ],
            "limit": 1000
            }  
    else:
        return None
    return query

def df_creator(query,url):
    resp = requests.post(url, params = userkey, json = query)
    ans = resp.json()
    df_ans = pd.json_normalize(ans['entities'])
    return df_ans

def count_creator(query,url):
    resp = requests.post(url, params = userkey, json = query)
    ans = resp.json()
    count = int(ans['count'])
    return count

def pull_data(url,queryType):
    last_uuid = ''
    master_df = None
    uuid_count = 0
    total_count = 0

    while uuid_count <= total_count:
        df_ans = df_creator(query_function(last_uuid,queryType),url)

        if master_df is None:
            master_df = df_ans
            total_count = count_creator(query_function(last_uuid,queryType),url)

        else:
            master_df = master_df.append(df_ans)

        last_uuid = df_ans['uuid'].tolist()[-1]
        length_uuid = len(df_ans['uuid'])
        uuid_count += length_uuid

#         print(uuid_count)
    
    return master_df

raw_data_orgs = pull_data(orgs_url,"orgs")
master_clean_orgs = pd.DataFrame()
master_clean_orgs = raw_data_orgs

# Querying funding rounds: problem with filtering by category vs category groups
###### 

# import time

# start = time.process_time()
# raw_data_funding = pull_data(funding_url,"funding")
# master_clean_funding = pd.DataFrame()
# master_clean_funding = raw_data_funding
# end = time.time()
# print("Elapsed time:")
# print(time.process_time() - start)


# ### Cleaning Prep

# In[4]:


revenue_ranges = {
"r_00000000": "Less than $1M",
"r_00001000": "$1M to $10M",
"r_00010000": "$10M to $50M",
"r_00050000": "$50M to $100M",
"r_00100000": "$100M to $500M",
"r_00500000": "$500M to $1B",
"r_01000000": "$1B to $10B",
"r_10000000": "$10B+"}

employee_ranges = {
"c_00001_00010": "1-10",
"c_00011_00050": "11-50",#nov 50th 18568
"c_00051_00100": "51-100", #jan 10th 44206
"c_00101_00250": "101-250",
"c_00251_00500": "251-500",
"c_00501_01000": "501-1000",
"c_01001_05000": "1001-5000",
"c_05001_10000": "5001-10000",
"c_10001_max": "10001+"}


# ### Cleaning Organizations

# In[6]:


# Drop columns we don't need
cols_to_drop_orgs = ["properties.location_group_identifiers",
                    "properties.equity_funding_total.currency",
                    "properties.identifier.permalink",
                    "properties.identifier.image_id",
                    "properties.identifier.uuid",
                    "properties.identifier.entity_def_id",
                    "properties.uuid",
                    "properties.valuation.currency",
                    "properties.valuation.value",
                    "properties.funding_total.currency",
                    "properties.funding_total.value",
                    "properties.last_equity_funding_total.currency",
                    "properties.last_equity_funding_total.value",
                    "properties.entity_def_id",
                    "properties.last_funding_total.currency",
                    "properties.last_funding_total.value",
                    "properties.funds_total.currency",
                    "properties.funds_total.value"]

master_clean_orgs.drop(cols_to_drop_orgs, axis=1, inplace=True)

# Remove prefixes/suffixes from the beginning of column names
master_clean_orgs.columns = master_clean_orgs.columns.str.replace('properties.','')
master_clean_orgs.columns = master_clean_orgs.columns.str.replace('.value','')
master_clean_orgs.columns = master_clean_orgs.columns.str.replace('_usd','')

master_clean_orgs["revenue_range"] = master_clean_orgs["revenue_range"].map(revenue_ranges).astype(str)
master_clean_orgs["category_groups"] = master_clean_orgs["category_groups"].apply(lambda x: list(map(itemgetter('value'), x)if isinstance(x, list) else ["Not found"])).apply(lambda x : ",".join(map(str, x)))
master_clean_orgs["num_employees_range"] = master_clean_orgs["num_employees_enum"].map(employee_ranges).astype(str)
master_clean_orgs["categories"] = master_clean_orgs["categories"].apply(lambda x: list(map(itemgetter('value'), x)if isinstance(x, list) else ["Not found"])).apply(lambda x : ",".join(map(str, x)))
master_clean_orgs["location_city"] = master_clean_orgs["location_identifiers"].apply(lambda x: list(map(itemgetter('value'), x)if isinstance(x, list) else ["Not found"])).apply(lambda x : ",".join(map(str, x))) 


# ### Cleaning Funding Rounds (needs updating)

# In[7]:


# Drop columns we don't need

# Update after query is working
#cols_to_drop_orgs = ["properties."]

#master_clean_funding.columns = master_clean_funding.columns.str.replace('properties.','')
#master_clean_funding.columns = master_clean_funding.columns.str.replace('.value','')
#master_clean_funding.columns = master_clean_funding.columns.str.replace('_usd','')

#master_clean_funding["revenue_range"] = master_clean_funding["revenue_range"].map(revenue_ranges).astype(str)
#master_clean_funding["num_employees_range"] = master_clean_funding["num_employees_enum"].map(employee_ranges).astype(str)
#master_clean_funding["categories"] = master_clean_funding["categories"].apply(lambda x: list(map(itemgetter('value'), x)if #isinstance(x, list) else ["Not found"])).apply(lambda x : ",".join(map(str, x))) # WHICH IS RIGHT?? THIS OR CATEGORY GROUPS?
#master_clean_funding["location_city"] = master_clean_funding["location_identifiers"].apply(lambda x: #list(map(itemgetter('value'), x)if isinstance(x, list) else ["Not found"])).apply(lambda x : ",".join(map(str, x))) # WHICH IS #RIGHT?? THIS OR CATEGORY GROUPS?


# ### Save Data

# In[8]:


# Inspect the data
# master_clean_orgs.info()

# Generates a name (including the date) for the file
# fileNameFunding = "crunchbase_funding_rounds_" + get_date() + ".csv"
# master_clean_funding.to_csv(fileNameFunding)
#fileNameOrgs = "crunchbase_organizations_" + get_date() + ".csv"
fileNameOrgs = "/datafile/crunchbase_organizations.csv"
master_clean_orgs.to_csv(fileNameOrgs)


# Write to Amazon S3

arg_aws_access_key_id = str(sys.argv[4])
arg_aws_secret_access_key = str(sys.argv[5])
arg_region_name = str(sys.argv[6])
s3_bucket_name = str(sys.argv[7])
print(arg_aws_access_key_id)
s3 = boto3.resource(
    service_name='s3',
    region_name=arg_region_name,
    aws_access_key_id=arg_aws_access_key_id,
    aws_secret_access_key=arg_aws_secret_access_key
)

# Upload files to S3 bucket
s3.Bucket(s3_bucket_name).upload_file(Filename=fileNameOrgs, Key=fileNameOrgs)

# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:


# OLD CODE:

# def company_count(query,url):
#     r = requests.post(url, params = userkey , json = query)
#     result = json.loads(r.text)
#     total_companies = result["count"]
#     return total_companies

# def url_extraction(query,url):
#     raw = pd.DataFrame()
#     r = requests.post(url, params = userkey , json = query)
#     result = json.loads(r.text)
#     normalized_raw = json_normalize(result['entities'])
#     return normalized_raw

# def pull_data(query,url):
#     raw = pd.DataFrame()
#     comp_count = company_count(query,url)
#     data_acq = 0
#     while data_acq < comp_count:
#         if data_acq != 0:
#             last_uuid = raw.uuid[len(raw.uuid)-1]
#             query["after_id"] = last_uuid
#             data_to_add = url_extraction(query,url)
#             raw = raw.append(data_to_add,ignore_index=True)
#             data_acq = len(raw.uuid)
#         else:
#             if "after_id" in query:
#                 query = query.pop("after_id")
#                 data_to_add = url_extraction(query,url)
#                 raw = raw.append(data_to_add,ignore_index=True)
#                 data_acq = len(raw.uuid)
#             else:
#                 data_to_add = url_extraction(query,url)
#                 raw = raw.append(data_to_add,ignore_index=True)
#                 data_acq = len(raw.uuid)
#     return raw

# raw_data_orgs = pull_data(query_orgs,orgs_url)
# master_clean_orgs = pd.DataFrame()
# master_clean_orgs = raw_data_orgs

# raw_data_funding = pull_data(query_funding,funding_url)
# master_clean_funding = pd.DataFrame()
# master_clean_funding = raw_data_funding

# def query_function_funding(last_uuid):
#     query = {
#         "field_ids": [
#             "identifier",
#             "entity_def_id",
#             "announced_on",
#             "closed_on",
#             "created_at"
#             "funded_organization_categories",
#             "funded_organization_description",
#             "funded_organization_funding_stage",
#             "funded_organization_funding_total",
#             "funded_organization_identifier",
#             "funded_organization_location",
#             "funded_organization_revenue_range",
#             "investment_stage",
#             "investment_type",
#             "investor_identifiers",
#             "is_equity",
#             "lead_investor_identifiers"
#             "money_raised",
#             "name",
#             "num_investors",
#             "num_partners",
#             "post_money_valuation",
#             "pre_money_valuation",
#             "rank_funding_round",
#             "short_description",
#             "target_money_raised",
#             "uuid"
#             ],
#         "query": [
#             {"type": "predicate",
#             "field_id": "funded_organization_location",
#             "operator_id": "includes",
#             "values": city_uuids
#             },
#             {"type": "predicate",
#             "field_id": "funded_organization_categories",
#             "operator_id": "includes",
#             "values": categories_uuids}
#             ],
#         "limit": 1000
#         }
#     return query

# def query_function_org(last_uuid):
#     query = {
#         "field_ids": [
#         "identifier",
#         "entity_def_id",
#         "location_identifiers",
#         "short_description",
#         "company_type",
#         "categories",
#         "category_groups",
#         "equity_funding_total",
#         "exited_on",
#         "founded_on",
#         "funding_stage",
#         "funding_total",
#         "funds_total",
#         "investor_stage", # this will tell us the stage of investments made by this organization
#         "investor_type", # describes the type of investor this organization
#         "ipo_status",
#         "last_equity_funding_total",
#         "last_equity_funding_type",
#         "last_funding_at",
#         "last_funding_total",
#         "last_funding_type",
#         "listed_stock_symbol",
#         "location_group_identifiers",
#         "location_identifiers", # where the organization is headquartered. value and location_type of interest in identifier
#         "num_employees_enum",
#         "num_funding_rounds",
#         "num_funds",
#         "num_investors",
#         "operating_status", # we can remove closed companies
#         "revenue_range",
#         "valuation",
#         "operating_status",
#         "uuid"
#         ],
#         "query": [
#             {"type": "predicate",
#             "field_id": "location_identifiers",
#             "operator_id": "includes",
#             "values": city_uuids
#             },
#             {"type": "predicate",
#             "field_id": "facet_ids",
#             "operator_id": "includes",
#             "values": ["company"]
#             },
#             {"type": "predicate",
#             "field_id": "category_groups",
#             "operator_id": "includes",
#             "values": categories_uuids}
#             ],
#         "limit": 1000
#         }
#     return query

