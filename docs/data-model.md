# Fantasy Premier League Data Model

## Overview

This document defines a star schema data model for Fantasy Premier League (FPL) data sourced from the official FPL API endpoints. The schema is designed for analytical workloads in Snowflake, optimizing for player performance analytics, fixture analysis, and historical trend reporting.

## API Endpoints

- **Bootstrap Static**: `https://fantasy.premierleague.com/api/bootstrap-static/`
- **Fixtures**: `https://fantasy.premierleague.com/api/fixtures/`
- **Element Summary**: `https://fantasy.premierleague.com/api/element-summary/{player_id}/`

## Star Schema Design

### Fact Tables

#### 1. `fact_player_performance`
Central fact table containing player performance metrics by gameweek.

| Column | Data Type | Description | Source |
|--------|-----------|-------------|---------|
| player_id | INTEGER | Player identifier | element-summary.history.element |
| gameweek_id | INTEGER | Gameweek identifier | element-summary.history.round |
| fixture_id | INTEGER | Fixture identifier | element-summary.history.fixture |
| opponent_team_id | INTEGER | Opponent team identifier | element-summary.history.opponent_team |
| was_home | BOOLEAN | Whether playing at home | element-summary.history.was_home |
| total_points | INTEGER | Total FPL points scored | element-summary.history.total_points |
| minutes | INTEGER | Minutes played | element-summary.history.minutes |
| goals_scored | INTEGER | Goals scored | element-summary.history.goals_scored |
| assists | INTEGER | Assists made | element-summary.history.assists |
| clean_sheets | INTEGER | Clean sheets achieved | element-summary.history.clean_sheets |
| goals_conceded | INTEGER | Goals conceded | element-summary.history.goals_conceded |
| own_goals | INTEGER | Own goals scored | element-summary.history.own_goals |
| penalties_saved | INTEGER | Penalties saved | element-summary.history.penalties_saved |
| penalties_missed | INTEGER | Penalties missed | element-summary.history.penalties_missed |
| yellow_cards | INTEGER | Yellow cards received | element-summary.history.yellow_cards |
| red_cards | INTEGER | Red cards received | element-summary.history.red_cards |
| saves | INTEGER | Saves made | element-summary.history.saves |
| bonus | INTEGER | Bonus points | element-summary.history.bonus |
| bps | INTEGER | Bonus points system score | element-summary.history.bps |
| influence | DECIMAL(5,1) | Influence rating | element-summary.history.influence |
| creativity | DECIMAL(5,1) | Creativity rating | element-summary.history.creativity |
| threat | DECIMAL(5,1) | Threat rating | element-summary.history.threat |
| ict_index | DECIMAL(5,1) | ICT (Influence, Creativity, Threat) index | element-summary.history.ict_index |
| starts | INTEGER | Number of starts | element-summary.history.starts |
| expected_goals | DECIMAL(4,2) | Expected goals | element-summary.history.expected_goals |
| expected_assists | DECIMAL(4,2) | Expected assists | element-summary.history.expected_assists |
| expected_goal_involvements | DECIMAL(4,2) | Expected goal involvements | element-summary.history.expected_goal_involvements |
| expected_goals_conceded | DECIMAL(4,2) | Expected goals conceded | element-summary.history.expected_goals_conceded |
| value | INTEGER | Player value in millions | element-summary.history.value |
| transfers_balance | INTEGER | Net transfers in/out | element-summary.history.transfers_balance |
| selected | INTEGER | Number of teams selected by | element-summary.history.selected |
| transfers_in | INTEGER | Transfers in | element-summary.history.transfers_in |
| transfers_out | INTEGER | Transfers out | element-summary.history.transfers_out |

#### 2. `fact_fixtures`
Fact table containing fixture-level information and results.

| Column | Data Type | Description | Source |
|--------|-----------|-------------|---------|
| fixture_id | INTEGER | Unique fixture identifier | fixtures.id |
| code | BIGINT | Alternative fixture code | fixtures.code |
| gameweek_id | INTEGER | Gameweek identifier | fixtures.event |
| home_team_id | INTEGER | Home team identifier | fixtures.team_h |
| away_team_id | INTEGER | Away team identifier | fixtures.team_a |
| kickoff_time | TIMESTAMP | Match kickoff time | fixtures.kickoff_time |
| home_team_score | INTEGER | Home team final score | fixtures.team_h_score |
| away_team_score | INTEGER | Away team final score | fixtures.team_a_score |
| finished | BOOLEAN | Whether fixture is finished | fixtures.finished |
| provisional_start_time | BOOLEAN | Whether start time is provisional | fixtures.provisional_start_time |
| finished_provisional | BOOLEAN | Whether finish status is provisional | fixtures.finished_provisional |
| minutes | INTEGER | Minutes played | fixtures.minutes |
| started | BOOLEAN | Whether fixture has started | fixtures.started |
| home_team_difficulty | INTEGER | Difficulty rating for home team | fixtures.team_h_difficulty |
| away_team_difficulty | INTEGER | Difficulty rating for away team | fixtures.team_a_difficulty |
| pulse_id | INTEGER | Pulse identifier | fixtures.pulse_id |

### Dimension Tables

#### 1. `dim_players`
Player dimension containing static and slowly changing player attributes.

| Column | Data Type | Description | Source |
|--------|-----------|-------------|---------|
| player_id | INTEGER | Unique player identifier | bootstrap-static.elements.id |
| code | INTEGER | Player code | bootstrap-static.elements.code |
| first_name | VARCHAR(50) | Player first name | bootstrap-static.elements.first_name |
| second_name | VARCHAR(50) | Player surname | bootstrap-static.elements.second_name |
| web_name | VARCHAR(50) | Display name | bootstrap-static.elements.web_name |
| team_id | INTEGER | Current team identifier | bootstrap-static.elements.team |
| position_id | INTEGER | Position identifier | bootstrap-static.elements.element_type |
| status | VARCHAR(1) | Availability status | bootstrap-static.elements.status |
| current_cost | INTEGER | Current cost in millions | bootstrap-static.elements.now_cost |
| cost_change_start | INTEGER | Cost change from season start | bootstrap-static.elements.cost_change_start |
| cost_change_event | INTEGER | Cost change from last gameweek | bootstrap-static.elements.cost_change_event |
| cost_change_start_fall | INTEGER | Total cost decreases from season start | bootstrap-static.elements.cost_change_start_fall |
| cost_change_event_fall | INTEGER | Cost decrease from last gameweek | bootstrap-static.elements.cost_change_event_fall |
| in_dreamteam | BOOLEAN | In current gameweek dream team | bootstrap-static.elements.in_dreamteam |
| dreamteam_count | INTEGER | Number of times in dream team | bootstrap-static.elements.dreamteam_count |
| selected_by_percent | DECIMAL(4,1) | Percentage of teams selecting player | bootstrap-static.elements.selected_by_percent |
| form | DECIMAL(3,1) | Recent form rating | bootstrap-static.elements.form |
| transfers_out | INTEGER | Transfers out this gameweek | bootstrap-static.elements.transfers_out |
| transfers_in | INTEGER | Transfers in this gameweek | bootstrap-static.elements.transfers_in |
| transfers_out_event | INTEGER | Transfers out this event | bootstrap-static.elements.transfers_out_event |
| transfers_in_event | INTEGER | Transfers in this event | bootstrap-static.elements.transfers_in_event |
| loans_in | INTEGER | Loans in | bootstrap-static.elements.loans_in |
| loans_out | INTEGER | Loans out | bootstrap-static.elements.loans_out |
| loaned_in | INTEGER | Currently loaned in | bootstrap-static.elements.loaned_in |
| loaned_out | INTEGER | Currently loaned out | bootstrap-static.elements.loaned_out |
| total_points | INTEGER | Total points this season | bootstrap-static.elements.total_points |
| event_points | INTEGER | Points from last gameweek | bootstrap-static.elements.event_points |
| points_per_game | DECIMAL(3,1) | Average points per game | bootstrap-static.elements.points_per_game |
| ep_this | DECIMAL(3,1) | Expected points this gameweek | bootstrap-static.elements.ep_this |
| ep_next | DECIMAL(3,1) | Expected points next gameweek | bootstrap-static.elements.ep_next |
| special | BOOLEAN | Special status | bootstrap-static.elements.special |
| minutes | INTEGER | Total minutes played | bootstrap-static.elements.minutes |
| goals_scored | INTEGER | Total goals scored | bootstrap-static.elements.goals_scored |
| assists | INTEGER | Total assists | bootstrap-static.elements.assists |
| clean_sheets | INTEGER | Total clean sheets | bootstrap-static.elements.clean_sheets |
| goals_conceded | INTEGER | Total goals conceded | bootstrap-static.elements.goals_conceded |
| own_goals | INTEGER | Total own goals | bootstrap-static.elements.own_goals |
| penalties_saved | INTEGER | Total penalties saved | bootstrap-static.elements.penalties_saved |
| penalties_missed | INTEGER | Total penalties missed | bootstrap-static.elements.penalties_missed |
| yellow_cards | INTEGER | Total yellow cards | bootstrap-static.elements.yellow_cards |
| red_cards | INTEGER | Total red cards | bootstrap-static.elements.red_cards |
| saves | INTEGER | Total saves | bootstrap-static.elements.saves |
| bonus | INTEGER | Total bonus points | bootstrap-static.elements.bonus |
| bps | INTEGER | Total BPS | bootstrap-static.elements.bps |
| influence | DECIMAL(5,1) | Total influence | bootstrap-static.elements.influence |
| creativity | DECIMAL(5,1) | Total creativity | bootstrap-static.elements.creativity |
| threat | DECIMAL(5,1) | Total threat | bootstrap-static.elements.threat |
| ict_index | DECIMAL(5,1) | Total ICT index | bootstrap-static.elements.ict_index |
| starts | INTEGER | Total starts | bootstrap-static.elements.starts |
| expected_goals | DECIMAL(5,2) | Total expected goals | bootstrap-static.elements.expected_goals |
| expected_assists | DECIMAL(5,2) | Total expected assists | bootstrap-static.elements.expected_assists |
| expected_goal_involvements | DECIMAL(5,2) | Total expected goal involvements | bootstrap-static.elements.expected_goal_involvements |
| expected_goals_conceded | DECIMAL(5,2) | Total expected goals conceded | bootstrap-static.elements.expected_goals_conceded |
| influence_rank | INTEGER | Influence rank | bootstrap-static.elements.influence_rank |
| influence_rank_type | INTEGER | Influence rank within position | bootstrap-static.elements.influence_rank_type |
| creativity_rank | INTEGER | Creativity rank | bootstrap-static.elements.creativity_rank |
| creativity_rank_type | INTEGER | Creativity rank within position | bootstrap-static.elements.creativity_rank_type |
| threat_rank | INTEGER | Threat rank | bootstrap-static.elements.threat_rank |
| threat_rank_type | INTEGER | Threat rank within position | bootstrap-static.elements.threat_rank_type |
| ict_index_rank | INTEGER | ICT index rank | bootstrap-static.elements.ict_index_rank |
| ict_index_rank_type | INTEGER | ICT index rank within position | bootstrap-static.elements.ict_index_rank_type |
| corners_and_indirect_freekicks_order | INTEGER | Set piece order | bootstrap-static.elements.corners_and_indirect_freekicks_order |
| corners_and_indirect_freekicks_text | VARCHAR(100) | Set piece description | bootstrap-static.elements.corners_and_indirect_freekicks_text |
| direct_freekicks_order | INTEGER | Direct free kick order | bootstrap-static.elements.direct_freekicks_order |
| direct_freekicks_text | VARCHAR(100) | Direct free kick description | bootstrap-static.elements.direct_freekicks_text |
| penalties_order | INTEGER | Penalty taking order | bootstrap-static.elements.penalties_order |
| penalties_text | VARCHAR(100) | Penalty taking description | bootstrap-static.elements.penalties_text |
| expected_goals_per_90 | DECIMAL(4,2) | Expected goals per 90 minutes | bootstrap-static.elements.expected_goals_per_90 |
| saves_per_90 | DECIMAL(4,2) | Saves per 90 minutes | bootstrap-static.elements.saves_per_90 |
| expected_assists_per_90 | DECIMAL(4,2) | Expected assists per 90 minutes | bootstrap-static.elements.expected_assists_per_90 |
| expected_goal_involvements_per_90 | DECIMAL(4,2) | Expected goal involvements per 90 minutes | bootstrap-static.elements.expected_goal_involvements_per_90 |
| expected_goals_conceded_per_90 | DECIMAL(4,2) | Expected goals conceded per 90 minutes | bootstrap-static.elements.expected_goals_conceded_per_90 |
| goals_conceded_per_90 | DECIMAL(4,2) | Goals conceded per 90 minutes | bootstrap-static.elements.goals_conceded_per_90 |
| now_cost_rank | INTEGER | Current cost rank | bootstrap-static.elements.now_cost_rank |
| now_cost_rank_type | INTEGER | Current cost rank within position | bootstrap-static.elements.now_cost_rank_type |
| form_rank | INTEGER | Form rank | bootstrap-static.elements.form_rank |
| form_rank_type | INTEGER | Form rank within position | bootstrap-static.elements.form_rank_type |
| points_per_game_rank | INTEGER | Points per game rank | bootstrap-static.elements.points_per_game_rank |
| points_per_game_rank_type | INTEGER | Points per game rank within position | bootstrap-static.elements.points_per_game_rank_type |
| selected_rank | INTEGER | Selection rank | bootstrap-static.elements.selected_rank |
| selected_rank_type | INTEGER | Selection rank within position | bootstrap-static.elements.selected_rank_type |
| starts_per_90 | DECIMAL(4,2) | Starts per 90 minutes | bootstrap-static.elements.starts_per_90 |
| clean_sheets_per_90 | DECIMAL(4,2) | Clean sheets per 90 minutes | bootstrap-static.elements.clean_sheets_per_90 |

#### 2. `dim_teams`
Team dimension containing team information and attributes.

| Column | Data Type | Description | Source |
|--------|-----------|-------------|---------|
| team_id | INTEGER | Unique team identifier | bootstrap-static.teams.id |
| name | VARCHAR(100) | Full team name | bootstrap-static.teams.name |
| short_name | VARCHAR(10) | Short team name | bootstrap-static.teams.short_name |
| code | INTEGER | Team code | bootstrap-static.teams.code |
| draw | INTEGER | Number of draws | bootstrap-static.teams.draw |
| form | VARCHAR(10) | Recent form | bootstrap-static.teams.form |
| loss | INTEGER | Number of losses | bootstrap-static.teams.loss |
| played | INTEGER | Number of games played | bootstrap-static.teams.played |
| points | INTEGER | League points | bootstrap-static.teams.points |
| position | INTEGER | League position | bootstrap-static.teams.position |
| strength | INTEGER | Overall strength rating | bootstrap-static.teams.strength |
| strength_overall_home | INTEGER | Home strength rating | bootstrap-static.teams.strength_overall_home |
| strength_overall_away | INTEGER | Away strength rating | bootstrap-static.teams.strength_overall_away |
| strength_attack_home | INTEGER | Home attack strength | bootstrap-static.teams.strength_attack_home |
| strength_attack_away | INTEGER | Away attack strength | bootstrap-static.teams.strength_attack_away |
| strength_defence_home | INTEGER | Home defence strength | bootstrap-static.teams.strength_defence_home |
| strength_defence_away | INTEGER | Away defence strength | bootstrap-static.teams.strength_defence_away |
| team_division | INTEGER | Division/League | bootstrap-static.teams.team_division |
| unavailable | BOOLEAN | Team availability | bootstrap-static.teams.unavailable |
| win | INTEGER | Number of wins | bootstrap-static.teams.win |
| pulse_id | INTEGER | Pulse identifier | bootstrap-static.teams.pulse_id |

#### 3. `dim_positions`
Position dimension containing player position information.

| Column | Data Type | Description | Source |
|--------|-----------|-------------|---------|
| position_id | INTEGER | Unique position identifier | bootstrap-static.element_types.id |
| position_name | VARCHAR(20) | Position name | bootstrap-static.element_types.plural_name |
| position_name_short | VARCHAR(10) | Short position name | bootstrap-static.element_types.plural_name_short |
| squad_select | INTEGER | Number to select in squad | bootstrap-static.element_types.squad_select |
| squad_min_play | INTEGER | Minimum number to play | bootstrap-static.element_types.squad_min_play |
| squad_max_play | INTEGER | Maximum number to play | bootstrap-static.element_types.squad_max_play |
| ui_shirt_specific | BOOLEAN | UI shirt specific flag | bootstrap-static.element_types.ui_shirt_specific |
| sub_positions_locked | ARRAY | Sub-positions locked | bootstrap-static.element_types.sub_positions_locked |
| element_count | INTEGER | Number of players in position | bootstrap-static.element_types.element_count |

#### 4. `dim_gameweeks`
Gameweek dimension containing gameweek/event information.

| Column | Data Type | Description | Source |
|--------|-----------|-------------|---------|
| gameweek_id | INTEGER | Unique gameweek identifier | bootstrap-static.events.id |
| name | VARCHAR(50) | Gameweek name | bootstrap-static.events.name |
| deadline_time | TIMESTAMP | Transfer deadline | bootstrap-static.events.deadline_time |
| average_entry_score | INTEGER | Average score for gameweek | bootstrap-static.events.average_entry_score |
| finished | BOOLEAN | Whether gameweek is finished | bootstrap-static.events.finished |
| data_checked | BOOLEAN | Whether data is checked | bootstrap-static.events.data_checked |
| highest_scoring_entry | INTEGER | Highest scoring entry ID | bootstrap-static.events.highest_scoring_entry |
| deadline_time_epoch | BIGINT | Deadline time epoch | bootstrap-static.events.deadline_time_epoch |
| deadline_time_game_offset | INTEGER | Game offset for deadline | bootstrap-static.events.deadline_time_game_offset |
| highest_score | INTEGER | Highest score achieved | bootstrap-static.events.highest_score |
| is_previous | BOOLEAN | Is previous gameweek | bootstrap-static.events.is_previous |
| is_current | BOOLEAN | Is current gameweek | bootstrap-static.events.is_current |
| is_next | BOOLEAN | Is next gameweek | bootstrap-static.events.is_next |
| cup_leagues_created | BOOLEAN | Cup leagues created | bootstrap-static.events.cup_leagues_created |
| h2h_ko_matches_created | BOOLEAN | Head-to-head matches created | bootstrap-static.events.h2h_ko_matches_created |
| ranked_count | INTEGER | Number of ranked entries | bootstrap-static.events.ranked_count |
| chip_plays | ARRAY | Chip plays this gameweek | bootstrap-static.events.chip_plays |
| most_selected | INTEGER | Most selected player ID | bootstrap-static.events.most_selected |
| most_transferred_in | INTEGER | Most transferred in player ID | bootstrap-static.events.most_transferred_in |
| top_element | INTEGER | Top performing player ID | bootstrap-static.events.top_element |
| most_captained | INTEGER | Most captained player ID | bootstrap-static.events.most_captained |
| most_vice_captained | INTEGER | Most vice-captained player ID | bootstrap-static.events.most_vice_captained |

#### 5. `dim_player_season_history`
Historical season-level performance for players.

| Column | Data Type | Description | Source |
|--------|-----------|-------------|---------|
| player_id | INTEGER | Player identifier | element-summary.history_past.element_code |
| season_name | VARCHAR(10) | Season name (e.g., "2023/24") | element-summary.history_past.season_name |
| start_cost | INTEGER | Starting cost for season | element-summary.history_past.start_cost |
| end_cost | INTEGER | Ending cost for season | element-summary.history_past.end_cost |
| total_points | INTEGER | Total points for season | element-summary.history_past.total_points |
| minutes | INTEGER | Total minutes played | element-summary.history_past.minutes |
| goals_scored | INTEGER | Total goals scored | element-summary.history_past.goals_scored |
| assists | INTEGER | Total assists | element-summary.history_past.assists |
| clean_sheets | INTEGER | Total clean sheets | element-summary.history_past.clean_sheets |
| goals_conceded | INTEGER | Total goals conceded | element-summary.history_past.goals_conceded |
| own_goals | INTEGER | Total own goals | element-summary.history_past.own_goals |
| penalties_saved | INTEGER | Total penalties saved | element-summary.history_past.penalties_saved |
| penalties_missed | INTEGER | Total penalties missed | element-summary.history_past.penalties_missed |
| yellow_cards | INTEGER | Total yellow cards | element-summary.history_past.yellow_cards |
| red_cards | INTEGER | Total red cards | element-summary.history_past.red_cards |
| saves | INTEGER | Total saves | element-summary.history_past.saves |
| bonus | INTEGER | Total bonus points | element-summary.history_past.bonus |
| bps | INTEGER | Total BPS | element-summary.history_past.bps |
| influence | DECIMAL(5,1) | Total influence | element-summary.history_past.influence |
| creativity | DECIMAL(5,1) | Total creativity | element-summary.history_past.creativity |
| threat | DECIMAL(5,1) | Total threat | element-summary.history_past.threat |
| ict_index | DECIMAL(5,1) | Total ICT index | element-summary.history_past.ict_index |
| starts | INTEGER | Total starts | element-summary.history_past.starts |
| expected_goals | DECIMAL(5,2) | Total expected goals | element-summary.history_past.expected_goals |
| expected_assists | DECIMAL(5,2) | Total expected assists | element-summary.history_past.expected_assists |
| expected_goal_involvements | DECIMAL(5,2) | Total expected goal involvements | element-summary.history_past.expected_goal_involvements |
| expected_goals_conceded | DECIMAL(5,2) | Total expected goals conceded | element-summary.history_past.expected_goals_conceded |


## Relationships

### Primary Keys
- `fact_player_performance`: (`player_id`, `gameweek_id`, `fixture_id`)
- `fact_fixtures`: (`fixture_id`)
- `dim_players`: (`player_id`)
- `dim_teams`: (`team_id`)
- `dim_positions`: (`position_id`)
- `dim_gameweeks`: (`gameweek_id`)
- `dim_player_season_history`: (`player_id`, `season_name`)

### Foreign Key Relationships

#### `fact_player_performance`
- `player_id` → `dim_players.player_id`
- `gameweek_id` → `dim_gameweeks.gameweek_id`
- `fixture_id` → `fact_fixtures.fixture_id`
- `opponent_team_id` → `dim_teams.team_id`

#### `fact_fixtures`
- `gameweek_id` → `dim_gameweeks.gameweek_id`
- `home_team_id` → `dim_teams.team_id`
- `away_team_id` → `dim_teams.team_id`

#### `dim_players`
- `team_id` → `dim_teams.team_id`
- `position_id` → `dim_positions.position_id`

#### `dim_player_season_history`
- `player_id` → `dim_players.player_id`

## Data Refresh Strategy

### Full Refresh Tables
- `dim_players` - Updated weekly to capture current season statistics
- `dim_teams` - Updated weekly for league positions and form
- `dim_gameweeks` - Updated when new gameweeks are released

### Incremental Tables
- `fact_player_performance` - New records added after each gameweek
- `fact_fixtures` - New fixtures added when released, existing updated with results

### Static Tables
- `dim_positions` - Rarely changes, updated manually when position rules change
- `dim_player_season_history` - Historical data, only new seasons added

## Analytics Use Cases

This star schema supports various analytical use cases:

1. **Player Performance Analysis**
   - Season-over-season player comparison
   - Form analysis over recent gameweeks
   - Position-based performance benchmarking

2. **Team Analysis**
   - Team strength analysis home vs away
   - Team form and trend analysis
   - Fixture difficulty assessment

3. **Fixture Analysis**
   - Historical head-to-head performance
   - Home advantage analysis
   - Goal scoring trends

4. **Transfer Analysis**
   - Player ownership trends
   - Price change analysis
   - Transfer recommendations

5. **Predictive Modeling**
   - Expected vs actual performance
   - Player injury impact analysis
   - Fixture difficulty modeling

## Data Quality Considerations

1. **Null Handling**: Some performance metrics may be null for players who didn't play
2. **Data Consistency**: Ensure team IDs are consistent across all tables
3. **Historical Data**: Some metrics (like xG) may not be available for older seasons
4. **Update Timing**: Data should be refreshed after official gameweek conclusion
5. **Data Validation**: Implement checks for reasonable ranges on all numeric fields

## Implementation Notes

1. **Partitioning**: Consider partitioning fact tables by season or gameweek for performance
2. **Indexing**: Create indexes on commonly joined columns (player_id, team_id, gameweek_id)
3. **Data Types**: Use appropriate precision for decimal fields based on API response precision
4. **Constraints**: Implement foreign key constraints to maintain referential integrity
5. **Views**: Consider creating views for common analytical queries