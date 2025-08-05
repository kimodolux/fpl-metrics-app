INSERT INTO fpl_bootstrap_raw (
    extraction_timestamp, extraction_date, s3_file_path,
    player_id, code, web_name, first_name, second_name, team, team_code, element_type,
    total_points, points_per_game, minutes, goals_scored, assists, clean_sheets, goals_conceded,
    now_cost, selected_by_percent, transfers_in, transfers_out, transfers_in_event, transfers_out_event,
    influence, creativity, threat, ict_index, expected_goals, expected_assists, 
    expected_goal_involvements, expected_goals_conceded,
    status, chance_of_playing_next_round, chance_of_playing_this_round, in_dreamteam, dreamteam_count,
    form, event_points, value_form, value_season,
    news, news_added, photo,
    cost_change_event, cost_change_start, cost_change_event_fall, cost_change_start_fall
)
SELECT 
    extraction_timestamp,
    extraction_date,
    s3_file_path,
    -- Flatten the elements array to get individual player records
    player.value:id::INTEGER,
    player.value:code::INTEGER,
    player.value:web_name::STRING,
    player.value:first_name::STRING,
    player.value:second_name::STRING,
    player.value:team::INTEGER,
    player.value:team_code::INTEGER,
    player.value:element_type::INTEGER,
    -- Performance metrics
    player.value:total_points::INTEGER,
    player.value:points_per_game::FLOAT,
    player.value:minutes::INTEGER,
    player.value:goals_scored::INTEGER,
    player.value:assists::INTEGER,
    player.value:clean_sheets::INTEGER,
    player.value:goals_conceded::INTEGER,
    -- Cost and ownership
    player.value:now_cost::INTEGER,
    player.value:selected_by_percent::FLOAT,
    player.value:transfers_in::INTEGER,
    player.value:transfers_out::INTEGER,
    player.value:transfers_in_event::INTEGER,
    player.value:transfers_out_event::INTEGER,
    -- Advanced stats
    player.value:influence::FLOAT,
    player.value:creativity::FLOAT,
    player.value:threat::FLOAT,
    player.value:ict_index::FLOAT,
    player.value:expected_goals::FLOAT,
    player.value:expected_assists::FLOAT,
    player.value:expected_goal_involvements::FLOAT,
    player.value:expected_goals_conceded::FLOAT,
    -- Status and availability
    player.value:status::STRING,
    player.value:chance_of_playing_next_round::INTEGER,
    player.value:chance_of_playing_this_round::INTEGER,
    player.value:in_dreamteam::BOOLEAN,
    player.value:dreamteam_count::INTEGER,
    -- Performance indicators
    player.value:form::FLOAT,
    player.value:event_points::INTEGER,
    player.value:value_form::FLOAT,
    player.value:value_season::FLOAT,
    -- Additional metadata
    player.value:news::STRING,
    TRY_TO_TIMESTAMP(player.value:news_added::STRING),
    player.value:photo::STRING,
    -- Cost change indicators
    player.value:cost_change_event::INTEGER,
    player.value:cost_change_start::INTEGER,
    player.value:cost_change_event_fall::INTEGER,
    player.value:cost_change_start_fall::INTEGER
FROM fpl_bootstrap_staging,
LATERAL FLATTEN(input => raw_data:elements) as player
WHERE extraction_date = CURRENT_DATE();