from pathlib import Path

import pandas as pd


def load_processed_data():
    project_root = Path(__file__).resolve().parents[2]
    processed_dir = project_root / "data" / "processed"

    core_metrics = pd.read_csv(
        processed_dir / "core_metrics.csv"
    )

    funnel_metrics = pd.read_csv(
        processed_dir / "funnel_metrics.csv"
    )

    experiment_metrics = pd.read_csv(
        processed_dir / "experiment_metrics.csv"
    )

    return (
        core_metrics,
        funnel_metrics,
        experiment_metrics,
    )


def validate_rates(experiment_metrics: pd.DataFrame) -> None:
    rate_columns = [
        "ctr",
        "user_conversion_rate",
    ]

    for column in rate_columns:
        valid = experiment_metrics[column].between(0, 1).all()

        assert valid, (
            f"{column} contains values outside [0, 1]."
        )


def validate_non_negative_metrics(
    experiment_metrics: pd.DataFrame,
) -> None:

    columns = [
        "users",
        "sessions",
        "revenue",
        "orders",
        "average_order_value",
    ]

    for column in columns:
        valid = (experiment_metrics[column] >= 0).all()

        assert valid, (
            f"{column} contains negative values."
        )


def validate_funnel(funnel_metrics: pd.DataFrame) -> None:
    sessions = funnel_metrics["sessions"].tolist()

    for previous, current in zip(
        sessions,
        sessions[1:],
    ):
        assert current <= previous, (
            "Funnel count increased unexpectedly: "
            f"{previous} -> {current}"
        )

    rate_columns = [
        "rate_from_start",
        "step_conversion_rate",
        "drop_off_rate",
    ]

    for column in rate_columns:
        valid = funnel_metrics[column].between(0, 1).all()

        assert valid, (
            f"{column} contains values outside [0, 1]."
        )


def validate_experiment_totals(
    core_metrics: pd.DataFrame,
    experiment_metrics: pd.DataFrame,
) -> None:

    total_users = core_metrics.loc[
        0,
        "total_users",
    ]

    total_sessions = core_metrics.loc[
        0,
        "total_sessions",
    ]

    total_purchases = core_metrics.loc[
        0,
        "total_purchases",
    ]

    experiment_users = experiment_metrics[
        "users"
    ].sum()

    experiment_sessions = experiment_metrics[
        "sessions"
    ].sum()

    experiment_orders = experiment_metrics[
        "orders"
    ].sum()

    assert experiment_users == total_users, (
        "Experiment users do not match total users."
    )

    assert experiment_sessions == total_sessions, (
        "Experiment sessions do not match total sessions."
    )

    assert experiment_orders == total_purchases, (
        "Experiment orders do not match total purchases."
    )


def run_validations(
    core_metrics,
    funnel_metrics,
    experiment_metrics,
):

    checks = [
        (
            "Experiment rates",
            lambda: validate_rates(
                experiment_metrics
            ),
        ),
        (
            "Non-negative metrics",
            lambda: validate_non_negative_metrics(
                experiment_metrics
            ),
        ),
        (
            "Funnel structure",
            lambda: validate_funnel(
                funnel_metrics
            ),
        ),
        (
            "Experiment totals",
            lambda: validate_experiment_totals(
                core_metrics,
                experiment_metrics,
            ),
        ),
    ]

    for check_name, check_function in checks:
        check_function()
        print(f"PASS: {check_name}")


def main():
    (
        core_metrics,
        funnel_metrics,
        experiment_metrics,
    ) = load_processed_data()

    run_validations(
        core_metrics,
        funnel_metrics,
        experiment_metrics,
    )

    print()
    print("All metric validations passed.")


if __name__ == "__main__":
    main()