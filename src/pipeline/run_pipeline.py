import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


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


def run_step(step_number, step_name, script_path):
    """
    Run one pipeline step.

    If the step fails, raise an exception so that
    downstream pipeline steps are not executed.
    """

    full_script_path = PROJECT_ROOT / script_path

    print()
    print("=" * 70)
    print(
        f"STEP {step_number}: {step_name}"
    )
    print("=" * 70)

    if not full_script_path.exists():
        raise FileNotFoundError(
            f"Pipeline script not found: {full_script_path}"
        )

    subprocess.run(
        [
            sys.executable,
            str(full_script_path),
        ],
        cwd=PROJECT_ROOT,
        check=True,
    )

    print(
        f"PASS: {step_name}"
    )


def main():
    print()
    print("=" * 70)
    print(
        "PRODUCT ANALYTICS & EXPERIMENTATION PIPELINE"
    )
    print("=" * 70)

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

        print()
        print("=" * 70)
        print("PIPELINE FAILED")
        print("=" * 70)

        print(
            f"A pipeline step exited with code "
            f"{error.returncode}."
        )

        print(
            "Downstream steps were not executed."
        )

        sys.exit(1)

    except Exception as error:

        print()
        print("=" * 70)
        print("PIPELINE FAILED")
        print("=" * 70)

        print(
            f"Error: {error}"
        )

        print(
            "Downstream steps were not executed."
        )

        sys.exit(1)

    print()
    print("=" * 70)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 70)

    print(
        "All generation, analytics, experimentation, "
        "diagnostic, insight, and validation steps passed."
    )


if __name__ == "__main__":
    main()