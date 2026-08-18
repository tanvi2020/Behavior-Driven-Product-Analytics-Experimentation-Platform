from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INSIGHTS_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "product_insights.csv"
)


def load_insights():
    """
    Load generated behavior-driven insights.
    """

    if not INSIGHTS_PATH.exists():
        raise FileNotFoundError(
            f"Insights file not found: {INSIGHTS_PATH}"
        )

    return pd.read_csv(
        INSIGHTS_PATH
    )


def validate_not_empty(insights_df):
    """
    Ensure the insight engine produced insights.
    """

    assert not insights_df.empty, (
        "No insights were generated."
    )


def validate_required_columns(insights_df):
    """
    Ensure every expected output field exists.
    """

    required_columns = {
        "priority",
        "insight",
        "recommended_investigation",
        "priority_score",
        "impact_score",
        "rank",
    }

    missing_columns = (
        required_columns
        - set(insights_df.columns)
    )

    assert not missing_columns, (
        f"Missing columns: {missing_columns}"
    )


def validate_priorities(insights_df):
    """
    Ensure only supported priority levels appear.
    """

    valid_priorities = {
        "HIGH",
        "MEDIUM",
        "LOW",
    }

    invalid_priorities = set(
        insights_df["priority"]
    ) - valid_priorities

    assert not invalid_priorities, (
        f"Invalid priorities: {invalid_priorities}"
    )


def validate_ranks(insights_df):
    """
    Ensure ranks are consecutive and unique.
    """

    ranks = (
        insights_df["rank"]
        .astype(int)
        .tolist()
    )

    expected_ranks = list(
        range(
            1,
            len(insights_df) + 1,
        )
    )

    assert ranks == expected_ranks, (
        f"Invalid ranking. "
        f"Expected {expected_ranks}, "
        f"got {ranks}"
    )


def validate_priority_order(insights_df):
    """
    Ensure higher-priority insights appear
    before lower-priority insights.
    """

    scores = (
        insights_df["priority_score"]
        .tolist()
    )

    expected_scores = sorted(
        scores,
        reverse=True,
    )

    assert scores == expected_scores, (
        "Insights are not sorted by "
        "priority_score."
    )


def validate_text_fields(insights_df):
    """
    Ensure generated insight and investigation
    text are populated.
    """

    for column in [
        "insight",
        "recommended_investigation",
    ]:

        assert (
            insights_df[column]
            .notna()
            .all()
        ), (
            f"Missing values found in {column}."
        )

        assert (
            insights_df[column]
            .astype(str)
            .str.strip()
            .ne("")
            .all()
        ), (
            f"Empty text found in {column}."
        )


def main():

    insights_df = load_insights()

    checks = [
        (
            "Insights generated",
            validate_not_empty,
        ),
        (
            "Required columns",
            validate_required_columns,
        ),
        (
            "Priority values",
            validate_priorities,
        ),
        (
            "Insight ranks",
            validate_ranks,
        ),
        (
            "Priority ordering",
            validate_priority_order,
        ),
        (
            "Insight text",
            validate_text_fields,
        ),
    ]

    for check_name, check_function in checks:

        check_function(
            insights_df
        )

        print(
            f"PASS: {check_name}"
        )

    print()
    print(
        "All insight validations passed."
    )


if __name__ == "__main__":
    main()