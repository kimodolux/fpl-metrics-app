CREATE TABLE IF NOT EXISTS fpl_bootstrap_staging (
    raw_data VARIANT,
    extraction_timestamp TIMESTAMP_NTZ,
    extraction_date DATE,
    s3_file_path STRING
)