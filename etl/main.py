#!/usr/bin/env python3
import os
import sys
import argparse
import logging
from typing import Dict, Any

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
    logger.info(f"Starting {schedule} extract phase...")
    
    try:
        if schedule == "daily":
            run_daily_extract_pipelines()
            return {"success": True, "phase": "extract", "schedule": "daily"}
        elif schedule == "weekly":
            run_weekly_extract_pipelines()
            return {"success": True, "phase": "extract", "schedule": "weekly"}
        else:
            raise ValueError(f"Unknown schedule: {schedule}")
    except Exception as e:
        logger.error(f"Extract phase failed: {str(e)}")
        return {"success": False, "error": str(e), "phase": "extract", "schedule": schedule}


def run_source_phase(schedule: str) -> Dict[str, Any]:
    """Run the source load phase for the specified schedule."""
    logger = logging.getLogger(__name__)
    logger.info(f"Starting {schedule} source load phase...")
    
    try:
        if schedule == "daily":
            run_daily_source_load()
            return {"success": True, "phase": "source", "schedule": "daily"}
        elif schedule == "weekly":
            run_weekly_source_load()
            return {"success": True, "phase": "source", "schedule": "weekly"}
        else:
            raise ValueError(f"Unknown schedule: {schedule}")
    except Exception as e:
        logger.error(f"Source load phase failed: {str(e)}")
        return {"success": False, "error": str(e), "phase": "source", "schedule": schedule}


def run_stage_phase(schedule: str) -> Dict[str, Any]:
    """Run the stage load phase for the specified schedule."""
    logger = logging.getLogger(__name__)
    logger.info(f"Starting {schedule} stage load phase...")
    
    try:
        if schedule == "daily":
            run_daily_stage_load()
            return {"success": True, "phase": "stage", "schedule": "daily"}
        elif schedule == "weekly":
            run_weekly_stage_load()
            return {"success": True, "phase": "stage", "schedule": "weekly"}
        else:
            raise ValueError(f"Unknown schedule: {schedule}")
    except Exception as e:
        logger.error(f"Stage load phase failed: {str(e)}")
        return {"success": False, "error": str(e), "phase": "stage", "schedule": schedule}


def run_pipeline(schedule: str, phase: str) -> int:
    """Run the specified pipeline phase(s) for the given schedule."""
    logger = logging.getLogger(__name__)
    
    phases_to_run = []
    if phase == "all":
        phases_to_run = ["extract", "source", "stage"]
    else:
        phases_to_run = [phase]
    
    results = []
    
    for current_phase in phases_to_run:
        logger.info(f"Executing {current_phase} phase for {schedule} schedule")
        
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
            logger.error(f"Phase {current_phase} failed, stopping pipeline")
            return 1
        
        logger.info(f"Phase {current_phase} completed successfully")
    
    logger.info(f"All phases completed successfully for {schedule} schedule")
    return 0


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
    logger.info(f"Starting FPL ETL Pipeline - Schedule: {args.schedule}, Phase: {args.phase}")
    
    try:
        exit_code = run_pipeline(args.schedule, args.phase)
        if exit_code == 0:
            logger.info("Pipeline completed successfully")
        else:
            logger.error("Pipeline failed")
        return exit_code
        
    except KeyboardInterrupt:
        logger.warning("Pipeline interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())