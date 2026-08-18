import logging
import subprocess
import sys
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | %(levelname)s | %(message)s"
    ),
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(
    "product_analytics_pipeline"
)


# ---------------------------------------------------------
# Pipeline definition
# ---------------------------------------------------------

PIPELINE_STEPS = [
    (
        "Generate synthetic event data",
        "src/data_generation/generate_events.py",
    ),
    (
        "Validate event data",
        "src/data_generation/validate_events.py",
    ),
    (
        "Compute product metrics",
        "src/analytics/product_metrics.py",
    ),
    (
        "Validate product metrics",
        "src/analytics/validate_metrics.py",
    ),
    (
        "Run experiment analysis",
        "src/experimentation/experiment_analysis.py",
    ),
    (
        "Validate experiment analysis",
        "src/experimentation/validate_experiment.py",
    ),
    (
        "Generate EDA diagnostics",
        "src/diagnostics/eda_report.py",
    ),
    (
        "Validate EDA diagnostics",
        "src/diagnostics/validate_eda.py",
    ),
    (
        "Generate behavior-driven insights",
        "src/insights/insight_engine.py",
    ),
    (
        "Validate behavior-driven insights",
        "src/insights/validate_insights.py",
    ),
]


# ---------------------------------------------------------
# Run one pipeline step
# ---------------------------------------------------------

def run_step(
    step_number,
    step_name,
    script_path,
):
    """
    Run one pipeline step.

    A failed step raises an exception so downstream
    pipeline steps are not executed.
    """

    full_script_path = (
        PROJECT_ROOT / script_path
    )

    if not full_script_path.exists():
        raise FileNotFoundError(
            f"Pipeline script not found: "
            f"{full_script_path}"
        )

    logger.info(
        "STEP %s/%s STARTED | %s",
        step_number,
        len(PIPELINE_STEPS),
        step_name,
    )

    start_time = time.perf_counter()

    subprocess.run(
        [
            sys.executable,
            str(full_script_path),
        ],
        cwd=PROJECT_ROOT,
        check=True,
    )

    duration = (
        time.perf_counter()
        - start_time
    )

    logger.info(
        "STEP %s/%s COMPLETED | %s | %.2f seconds",
        step_number,
        len(PIPELINE_STEPS),
        step_name,
        duration,
    )


# ---------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------

def main():

    pipeline_start_time = (
        time.perf_counter()
    )

    logger.info(
        "PRODUCT ANALYTICS & "
        "EXPERIMENTATION PIPELINE STARTED"
    )

    try:

        for step_number, (
            step_name,
            script_path,
        ) in enumerate(
            PIPELINE_STEPS,
            start=1,
        ):

            run_step(
                step_number,
                step_name,
                script_path,
            )

    except subprocess.CalledProcessError as error:

        logger.error(
            "PIPELINE FAILED | "
            "A pipeline step exited with code %s. "
            "Downstream steps were not executed.",
            error.returncode,
        )

        sys.exit(1)

    except Exception:

        logger.exception(
            "PIPELINE FAILED | "
            "Downstream steps were not executed."
        )

        sys.exit(1)

    total_duration = (
        time.perf_counter()
        - pipeline_start_time
    )

    logger.info(
        "PIPELINE COMPLETED SUCCESSFULLY | "
        "All validation gates passed | "
        "%.2f seconds",
        total_duration,
    )


if __name__ == "__main__":
    main()