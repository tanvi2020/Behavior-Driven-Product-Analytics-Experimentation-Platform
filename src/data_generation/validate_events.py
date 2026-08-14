from pathlib import Path

import pandas as pd


VALID_EVENT_NAMES = {
    "app_open",
    "search",
    "click",
    "add_to_cart",
    "purchase",
}

VALID_EXPERIMENT_GROUPS = {
    "control",
    "treatment",
}


def load_events() -> pd.DataFrame:
    project_root = Path(__file__).resolve().parents[2]
    events_path = project_root / "data" / "raw" / "events.csv"

    events_df = pd.read_csv(
        events_path,
        parse_dates=["event_timestamp"],
    )

    return events_df


def validate_required_columns(events_df: pd.DataFrame) -> None:
    required_columns = {
        "event_id",
        "event_name",
        "user_id",
        "session_id",
        "event_timestamp",
        "experiment_id",
        "experiment_group",
    }

    missing_columns = required_columns - set(events_df.columns)

    assert not missing_columns, (
        f"Missing required columns: {missing_columns}"
    )


def validate_required_values(events_df: pd.DataFrame) -> None:
    required_columns = [
        "event_id",
        "event_name",
        "user_id",
        "session_id",
        "event_timestamp",
    ]

    for column in required_columns:
        missing_count = events_df[column].isna().sum()

        assert missing_count == 0, (
            f"{column} contains {missing_count} missing values."
        )


def validate_unique_event_ids(events_df: pd.DataFrame) -> None:
    duplicate_count = events_df["event_id"].duplicated().sum()

    assert duplicate_count == 0, (
        f"Found {duplicate_count} duplicate event_id values."
    )


def validate_event_names(events_df: pd.DataFrame) -> None:
    invalid_events = (
        set(events_df["event_name"].unique())
        - VALID_EVENT_NAMES
    )

    assert not invalid_events, (
        f"Invalid event names found: {invalid_events}"
    )


def validate_experiment_groups(events_df: pd.DataFrame) -> None:
    invalid_groups = (
        set(events_df["experiment_group"].dropna().unique())
        - VALID_EXPERIMENT_GROUPS
    )

    assert not invalid_groups, (
        f"Invalid experiment groups found: {invalid_groups}"
    )


def validate_search_events(events_df: pd.DataFrame) -> None:
    search_events = events_df[
        events_df["event_name"] == "search"
    ]

    missing_queries = search_events["search_query"].isna().sum()

    assert missing_queries == 0, (
        f"Found {missing_queries} search events without search_query."
    )


def validate_click_events(events_df: pd.DataFrame) -> None:
    click_events = events_df[
        events_df["event_name"] == "click"
    ]

    missing_products = click_events["product_id"].isna().sum()

    assert missing_products == 0, (
        f"Found {missing_products} click events without product_id."
    )


def validate_purchase_events(events_df: pd.DataFrame) -> None:
    purchase_events = events_df[
        events_df["event_name"] == "purchase"
    ]

    required_purchase_columns = [
        "product_id",
        "quantity",
        "unit_price",
        "order_id",
    ]

    for column in required_purchase_columns:
        missing_count = purchase_events[column].isna().sum()

        assert missing_count == 0, (
            f"Found {missing_count} purchase events "
            f"without {column}."
        )


def validate_session_order(events_df: pd.DataFrame) -> None:
    event_order = {
        "app_open": 1,
        "search": 2,
        "click": 3,
        "add_to_cart": 4,
        "purchase": 5,
    }

    ordered_df = events_df.sort_values(
        ["session_id", "event_timestamp"]
    ).copy()

    ordered_df["event_order"] = (
        ordered_df["event_name"]
        .map(event_order)
    )

    for session_id, session_df in ordered_df.groupby("session_id"):
        orders = session_df["event_order"].tolist()

        if orders != sorted(orders):
            raise AssertionError(
                f"Invalid event sequence in session {session_id}: "
                f"{session_df['event_name'].tolist()}"
            )


def validate_purchase_has_cart(events_df: pd.DataFrame) -> None:
    sessions_with_purchase = set(
        events_df.loc[
            events_df["event_name"] == "purchase",
            "session_id",
        ]
    )

    sessions_with_cart = set(
        events_df.loc[
            events_df["event_name"] == "add_to_cart",
            "session_id",
        ]
    )

    invalid_sessions = (
        sessions_with_purchase
        - sessions_with_cart
    )

    assert not invalid_sessions, (
        "Purchase found without add_to_cart in sessions: "
        f"{list(invalid_sessions)[:10]}"
    )


def run_validations(events_df: pd.DataFrame) -> None:
    checks = [
        ("Required columns", validate_required_columns),
        ("Required values", validate_required_values),
        ("Unique event IDs", validate_unique_event_ids),
        ("Event names", validate_event_names),
        ("Experiment groups", validate_experiment_groups),
        ("Search events", validate_search_events),
        ("Click events", validate_click_events),
        ("Purchase events", validate_purchase_events),
        ("Session event order", validate_session_order),
        ("Purchase requires cart", validate_purchase_has_cart),
    ]

    for check_name, check_function in checks:
        check_function(events_df)
        print(f"PASS: {check_name}")


def main():
    events_df = load_events()

    print(f"Loaded {len(events_df):,} events.")
    print()

    run_validations(events_df)

    print()
    print("All event validations passed.")


if __name__ == "__main__":
    main()