# ETLs

## Daily
Bootstrap data appended into snowflake.

### Process:
1. API fetches bootstrap data and saves to S3 as a compressed JSON
2. Snowflake reads S3 and inserts flattened JSON data to a staging bucket with date
3. Unflatten elements data in JSON data and insert into source players table
4. Source players data is inserted into transformed table (currenlty just a copy but will be transformed in some way for transfer algo)

### How to run
1. Run `etl/daily/extract.py`
1. Run `etl/daily/load.py`



## Weekly
Detailed player data overwrites current data

### Process:
1. API fetches bootstrap data and gets a list of current player id's
2. API fetched detailed player data using list of id's and saves each players hisotry and fixtures to S3 as compressed JSONs.
3. API fetches team and saves to S3 as a compressed JSON
4. API fetches fixtures and saves to S3 as a compressed JSON
5. Read fixtures, teams and each players fixtures and history from S3 into relevant source tables in snowflake
