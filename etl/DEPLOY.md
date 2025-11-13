# FPL ETL Lambda Deployment Guide

## Automated Deployment (GitHub Actions)

The recommended deployment method is via GitHub Actions, which automatically deploys on push to `master`.

### Setup
1. Configure GitHub Secrets (see `.github/SECRETS.md`)
2. Push to master branch
3. GitHub Actions will automatically build and deploy

The workflow also supports manual triggers from the Actions tab.

## Manual Deployment

### Prerequisites

- AWS CLI configured with appropriate credentials
- AWS SAM CLI installed (`brew install aws-sam-cli` or see [AWS docs](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html))
- Docker installed and running (for container builds)
- UV package manager installed

## Build and Deploy

### 1. Generate requirements.txt and build

```bash
uv pip compile pyproject.toml -o requirements.txt --python-version 3.13 && sam build --use-container
```

### 2. Deploy to AWS

**First time deployment (guided):**
```bash
sam deploy --guided
```

You'll be prompted for:
- Stack name (e.g., `fpl-etl`)
- AWS Region (e.g., `us-east-1`)
- S3BucketName (your data lake bucket)
- Snowflake credentials
- Confirm changes before deploy

**Subsequent deployments:**
```bash
sam deploy
```

## Lambda Functions

### Daily ETL
- **Function Name**: `fpl-etl-daily`
- **Schedule**: Daily at 2 AM UTC (`cron(0 2 * * ? *)`)
- **Phases**: Extract → Stage → Source
- **Memory**: 1024 MB
- **Timeout**: 15 minutes

### Weekly ETL
- **Function Name**: `fpl-etl-weekly`
- **Schedule**: Weekly on Sundays at 3 AM UTC (`cron(0 3 ? * SUN *)`)
- **Phases**: Extract → Stage → Source (includes player details)
- **Memory**: 2048 MB
- **Timeout**: 15 minutes

## Local Testing

Test daily function:
```bash
sam local invoke FPLETLDailyFunction -e lambda-event.json
```

Test weekly function:
```bash
sam local invoke FPLETLWeeklyFunction -e lambda-event-weekly.json
```

## View Logs

Tail daily logs:
```bash
sam logs -n FPLETLDailyFunction --stack-name fpl-etl --tail
```

Tail weekly logs:
```bash
sam logs -n FPLETLWeeklyFunction --stack-name fpl-etl --tail
```

Or use AWS Console: CloudWatch → Log Groups → `/aws/lambda/fpl-etl-daily` or `/aws/lambda/fpl-etl-weekly`

## Updating Schedules

Edit the cron expressions in `template.yaml`:
- Daily: Line 85
- Weekly: Line 127

Then redeploy with `sam deploy`

## Manual Invocation

Invoke from AWS Console:
1. Lambda → Functions → fpl-etl-daily (or weekly)
2. Test tab → Create test event
3. Use event from `lambda-event.json` or `lambda-event-weekly.json`
4. Click "Test"

Or via AWS CLI:
```bash
aws lambda invoke --function-name fpl-etl-daily --payload '{"detail":{"schedule":"daily","phase":"all"}}' response.json
```

## Cleanup

Remove all resources:
```bash
sam delete --stack-name fpl-etl
```
