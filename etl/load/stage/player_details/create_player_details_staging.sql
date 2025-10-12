CREATE TABLE IF NOT EXISTS FPL_STATS.FPL_SCHEMA.STAGING_PLAYER_DETAILS (
    raw_data VARIANT,
    extraction_timestamp TIMESTAMP_NTZ,
    extraction_date DATE,
    s3_file_path STRING
)