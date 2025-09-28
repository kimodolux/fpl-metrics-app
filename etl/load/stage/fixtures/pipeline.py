import sys
import os
from datetime import datetime
from zoneinfo import ZoneInfo

# Add the etl directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from load.stage.s3_to_snowflake_pipeline import load_s3_files_to_staging_pipeline

def run_fixtures_staging():
    now = datetime.now(ZoneInfo("Australia/Sydney"))
    return load_s3_files_to_staging_pipeline(
        staging_table_sql_file="load/stage/fixtures/create_fixtures_staging.sql",
        staging_table_name="STAGING_FIXTURES",
        s3_file_path=f"fpl-data/fixtures/fixtures_{now.strftime('%Y%m%d')}.json.gz",
        stage_name="fpl_s3_stage",
        bucket_name="fpl-stats-data-lake-dev"
    )

