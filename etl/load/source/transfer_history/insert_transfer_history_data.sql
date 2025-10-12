INSERT INTO FPL_STATS.FPL_SCHEMA.SOURCE_TRANSFER_HISTORY (
    player_id,
    date,
    now_cost,
    cost_change_event,
    cost_change_event_fall,
    cost_change_start,
    cost_change_start_fall,
    transfers_in,
    transfers_out,
    transfers_in_event,
    transfers_out_event,
    selected_by_percent,
    total_ownership,
    total_players,
    value_form,
    value_season,
    extraction_timestamp,
    extraction_date
)
SELECT 
    player.value:id::INTEGER as player_id,
    extraction_date as date,
    player.value:now_cost::INTEGER as now_cost,
    player.value:cost_change_event::INTEGER as cost_change_event,
    player.value:cost_change_event_fall::INTEGER as cost_change_event_fall,
    player.value:cost_change_start::INTEGER as cost_change_start,
    player.value:cost_change_start_fall::INTEGER as cost_change_start_fall,
    player.value:transfers_in::INTEGER as transfers_in,
    player.value:transfers_out::INTEGER as transfers_out,
    player.value:transfers_in_event::INTEGER as transfers_in_event,
    player.value:transfers_out_event::INTEGER as transfers_out_event,
    player.value:selected_by_percent::FLOAT as selected_by_percent,
    ROUND((player.value:selected_by_percent::FLOAT / 100.0) * raw_data:total_players::INTEGER) as total_ownership,
    raw_data:total_players::INTEGER as total_players,
    player.value:value_form::FLOAT as value_form,
    player.value:value_season::FLOAT as value_season,
    extraction_timestamp,
    extraction_date
FROM FPL_STATS.FPL_SCHEMA.STAGING_BOOTSTRAP,
LATERAL FLATTEN(input => raw_data:elements) as player
WHERE NOT EXISTS (
    SELECT 1 FROM FPL_STATS.FPL_SCHEMA.SOURCE_TRANSFER_HISTORY 
    WHERE player_id = player.value:id::INTEGER 
    AND extraction_date = FPL_STATS.FPL_SCHEMA.STAGING_BOOTSTRAP.extraction_date
);