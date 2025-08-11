CREATE TABLE IF NOT EXISTS STAGING_PLAYER_DETAILS (
    raw_data VARIANT,
    extraction_timestamp TIMESTAMP_NTZ,
    extraction_date DATE,
    s3_file_path STRING
)