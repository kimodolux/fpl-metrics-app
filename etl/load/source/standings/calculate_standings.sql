INSERT INTO FPL_STATS.FPL_SCHEMA.DIM_STANDINGS (
    team_id,
    code,
    draw,
    form,
    loss,
    name,
    played,
    points,
    position,
    short_name,
    strength,
    team_division,
    unavailable,
    win,
    strength_overall_home,
    strength_overall_away,
    strength_attack_home,
    strength_attack_away,
    strength_defence_home,
    strength_defence_away,
    pulse_id,
    extraction_timestamp,
    extraction_date
)
WITH team_stats AS (
    -- Calculate stats for home games
    SELECT
        team_h as team_id,
        COUNT(*) as home_played,
        SUM(CASE WHEN team_h_score > team_a_score THEN 1 ELSE 0 END) as home_wins,
        SUM(CASE WHEN team_h_score = team_a_score THEN 1 ELSE 0 END) as home_draws,
        SUM(CASE WHEN team_h_score < team_a_score THEN 1 ELSE 0 END) as home_losses
    FROM FPL_STATS.FPL_SCHEMA.SOURCE_FIXTURES
    WHERE finished = TRUE
    GROUP BY team_h

    UNION ALL

    -- Calculate stats for away games
    SELECT
        team_a as team_id,
        COUNT(*) as away_played,
        SUM(CASE WHEN team_a_score > team_h_score THEN 1 ELSE 0 END) as away_wins,
        SUM(CASE WHEN team_a_score = team_h_score THEN 1 ELSE 0 END) as away_draws,
        SUM(CASE WHEN team_a_score < team_h_score THEN 1 ELSE 0 END) as away_losses
    FROM FPL_STATS.FPL_SCHEMA.SOURCE_FIXTURES
    WHERE finished = TRUE
    GROUP BY team_a
),
aggregated_stats AS (
    SELECT
        team_id,
        SUM(home_played) as played,
        SUM(home_wins) as wins,
        SUM(home_draws) as draws,
        SUM(home_losses) as losses,
        (SUM(home_wins) * 3) + (SUM(home_draws) * 1) as total_points
    FROM team_stats
    GROUP BY team_id
),
ranked_teams AS (
    SELECT
        t.team_id,
        t.code,
        COALESCE(s.draws, 0) as draw,
        t.form,
        COALESCE(s.losses, 0) as loss,
        t.name,
        COALESCE(s.played, 0) as played,
        COALESCE(s.total_points, 0) as points,
        t.short_name,
        t.strength,
        t.team_division,
        t.unavailable,
        COALESCE(s.wins, 0) as win,
        t.strength_overall_home,
        t.strength_overall_away,
        t.strength_attack_home,
        t.strength_attack_away,
        t.strength_defence_home,
        t.strength_defence_away,
        t.pulse_id,
        t.extraction_timestamp,
        t.extraction_date,
        ROW_NUMBER() OVER (ORDER BY COALESCE(s.total_points, 0) DESC, t.name ASC) as position
    FROM FPL_STATS.FPL_SCHEMA.SOURCE_TEAMS t
    LEFT JOIN aggregated_stats s ON t.team_id = s.team_id
)
SELECT
    team_id,
    code,
    draw,
    form,
    loss,
    name,
    played,
    points,
    position,
    short_name,
    strength,
    team_division,
    unavailable,
    win,
    strength_overall_home,
    strength_overall_away,
    strength_attack_home,
    strength_attack_away,
    strength_defence_home,
    strength_defence_away,
    pulse_id,
    extraction_timestamp,
    extraction_date
FROM ranked_teams;
