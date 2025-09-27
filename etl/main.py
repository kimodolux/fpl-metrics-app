#!/usr/bin/env python3
import os
import sys
import argparse
import logging
import json
from typing import Dict, Any, Optional

# Add the etl directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import pipeline functions
from extract.run_daily_extract import run_daily_extract_pipelines
from extract.run_weekly_extract import run_weekly_extract_pipelines
from load.run_daily_source_load import run_daily_load_pipelines as run_daily_source_load
from load.run_weekly_source_load import run_weekly_load_pipelines as run_weekly_source_load
from load.run_daily_stage_load import run_daily_load_pipelines as run_daily_stage_load
from load.run_weekly_stage_load import run_weekly_load_pipelines as run_weekly_stage_load


def setup_logging(log_level: str) -> None:
    """Configure logging for the application."""
    level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def run_extract_phase(schedule: str) -> Dict[str, Any]:
    """Run the extract phase for the specified schedule."""
    logger = logging.getLogger(__name__)
    logger.info(f"[PHASE_START] {schedule.upper()} EXTRACT PHASE - Starting")
    
    try:
        if schedule == "daily":
            run_daily_extract_pipelines()
            logger.info(f"[PHASE_COMPLETE] {schedule.upper()} EXTRACT PHASE - Completed successfully")
            return {"success": True, "phase": "extract", "schedule": "daily"}
        elif schedule == "weekly":
            run_weekly_extract_pipelines()
            logger.info(f"[PHASE_COMPLETE] {schedule.upper()} EXTRACT PHASE - Completed successfully")
            return {"success": True, "phase": "extract", "schedule": "weekly"}
        else:
            raise ValueError(f"Unknown schedule: {schedule}")
    except Exception as e:
        logger.error(f"[PHASE_FAILED] {schedule.upper()} EXTRACT PHASE - {str(e)}")
        return {"success": False, "error": str(e), "phase": "extract", "schedule": schedule}


def run_source_phase(schedule: str) -> Dict[str, Any]:
    """Run the source load phase for the specified schedule."""
    logger = logging.getLogger(__name__)
    logger.info(f"[PHASE_START] {schedule.upper()} SOURCE PHASE - Starting")
    
    try:
        if schedule == "daily":
            run_daily_source_load()
            logger.info(f"[PHASE_COMPLETE] {schedule.upper()} SOURCE PHASE - Completed successfully")
            return {"success": True, "phase": "source", "schedule": "daily"}
        elif schedule == "weekly":
            run_weekly_source_load()
            logger.info(f"[PHASE_COMPLETE] {schedule.upper()} SOURCE PHASE - Completed successfully")
            return {"success": True, "phase": "source", "schedule": "weekly"}
        else:
            raise ValueError(f"Unknown schedule: {schedule}")
    except Exception as e:
        logger.error(f"[PHASE_FAILED] {schedule.upper()} SOURCE PHASE - {str(e)}")
        return {"success": False, "error": str(e), "phase": "source", "schedule": schedule}


def run_stage_phase(schedule: str) -> Dict[str, Any]:
    """Run the stage load phase for the specified schedule."""
    logger = logging.getLogger(__name__)
    logger.info(f"[PHASE_START] {schedule.upper()} STAGE PHASE - Starting")
    
    try:
        if schedule == "daily":
            run_daily_stage_load()
            logger.info(f"[PHASE_COMPLETE] {schedule.upper()} STAGE PHASE - Completed successfully")
            return {"success": True, "phase": "stage", "schedule": "daily"}
        elif schedule == "weekly":
            run_weekly_stage_load()
            logger.info(f"[PHASE_COMPLETE] {schedule.upper()} STAGE PHASE - Completed successfully")
            return {"success": True, "phase": "stage", "schedule": "weekly"}
        else:
            raise ValueError(f"Unknown schedule: {schedule}")
    except Exception as e:
        logger.error(f"[PHASE_FAILED] {schedule.upper()} STAGE PHASE - {str(e)}")
        return {"success": False, "error": str(e), "phase": "stage", "schedule": schedule}


def run_pipeline(schedule: str, phase: str) -> int:
    """Run the specified pipeline phase(s) for the given schedule."""
    logger = logging.getLogger(__name__)
    
    phases_to_run = []
    if phase == "all":
        phases_to_run = ["extract", "stage", "source"]
    else:
        phases_to_run = [phase]
    
    results = []
    
    for current_phase in phases_to_run:
        logger.info(f"[PIPELINE_START] {current_phase.upper()} - Starting for {schedule} schedule")
        
        if current_phase == "extract":
            result = run_extract_phase(schedule)
        elif current_phase == "source":
            result = run_source_phase(schedule)
        elif current_phase == "stage":
            result = run_stage_phase(schedule)
        else:
            logger.error(f"Unknown phase: {current_phase}")
            return 1
        
        results.append(result)
        
        if not result.get("success", False):
            logger.error(f"[PIPELINE_FAILED] {current_phase.upper()} - Failed, stopping pipeline")
            return 1

        logger.info(f"[PIPELINE_COMPLETE] {current_phase.upper()} - Completed successfully")
    
    logger.info(f"[PIPELINE_COMPLETE] ALL PHASES - Completed successfully for {schedule.upper()} schedule")
    return 0


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for EventBridge scheduled events.
    
    Expected event structure from EventBridge:
    {
        "detail": {
            "schedule": "daily" | "weekly",
            "phase": "extract" | "source" | "stage" | "all"
        }
    }
    """
    # Setup logging for Lambda
    setup_logging("INFO")
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Lambda handler invoked with event: {json.dumps(event, indent=2)}")
        
        # Extract parameters from EventBridge event
        detail = event.get("detail", {})
        schedule = detail.get("schedule")
        phase = detail.get("phase", "all")
        
        if not schedule:
            error_msg = "Missing 'schedule' parameter in event detail"
            logger.error(error_msg)
            return {
                "statusCode": 400,
                "success": False,
                "error": error_msg
            }
        
        if schedule not in ["daily", "weekly"]:
            error_msg = f"Invalid schedule '{schedule}'. Must be 'daily' or 'weekly'"
            logger.error(error_msg)
            return {
                "statusCode": 400,
                "success": False,
                "error": error_msg
            }
        
        if phase not in ["extract", "source", "stage", "all"]:
            error_msg = f"Invalid phase '{phase}'. Must be one of: extract, source, stage, all"
            logger.error(error_msg)
            return {
                "statusCode": 400,
                "success": False,
                "error": error_msg
            }
        
        logger.info(f"[PIPELINE_START] FPL ETL LAMBDA - Schedule: {schedule.upper()}, Phase: {phase.upper()}")
        
        # Run the pipeline
        exit_code = run_pipeline(schedule, phase)

        if exit_code == 0:
            logger.info(f"[PIPELINE_COMPLETE] FPL ETL LAMBDA - Completed successfully")
            return {
                "statusCode": 200,
                "success": True,
                "message": f"Pipeline completed successfully for schedule '{schedule}' and phase '{phase}'"
            }
        else:
            logger.error(f"[PIPELINE_FAILED] FPL ETL LAMBDA - Pipeline failed")
            return {
                "statusCode": 500,
                "success": False,
                "error": f"Pipeline failed for schedule '{schedule}' and phase '{phase}'"
            }
            
    except Exception as e:
        error_msg = f"Lambda handler error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "statusCode": 500,
            "success": False,
            "error": error_msg
        }


def main() -> int:
    """Main entry point for the ETL pipeline."""
    parser = argparse.ArgumentParser(
        description="FPL Stats ETL Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --schedule daily                    # Run daily pipeline (all phases)
  %(prog)s --schedule weekly --phase extract   # Run weekly extract only
  %(prog)s --schedule daily --phase source     # Run daily source load only
  %(prog)s --schedule weekly --log-level DEBUG # Run weekly pipeline with debug logging
        """
    )
    
    parser.add_argument(
        "--schedule",
        choices=["daily", "weekly"],
        required=True,
        help="Pipeline schedule to run"
    )
    
    parser.add_argument(
        "--phase",
        choices=["extract", "source", "stage", "all"],
        default="all",
        help="Pipeline phase to run (default: all)"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    
    logger = logging.getLogger(__name__)
    logger.info(f"[PIPELINE_START] FPL ETL - Schedule: {args.schedule.upper()}, Phase: {args.phase.upper()}")
    
    try:
        exit_code = run_pipeline(args.schedule, args.phase)
        if exit_code == 0:
            logger.info(f"[PIPELINE_COMPLETE] FPL ETL - Completed successfully")
        else:
            logger.error(f"[PIPELINE_FAILED] FPL ETL - Pipeline failed")
        return exit_code
        
    except KeyboardInterrupt:
        logger.warning("[PIPELINE_INTERRUPTED] FPL ETL - Pipeline interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"[PIPELINE_FAILED] FPL ETL - Unexpected error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())