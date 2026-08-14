from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# 1. Load raw event data
# ---------------------------------------------------------

def load_events() -> pd.DataFrame:
    project_root = Path(__file__).resolve().parents[2]
    events_path = project_root / "data" / "raw" / "events.csv"

    events_df = pd.read_csv(
        events_path,
        parse_dates=["event_timestamp"],
    )

    return events_df


# ---------------------------------------------------------
# 2. Count core entities/events
# ---------------------------------------------------------

def calculate_basic_counts(events_df: pd.DataFrame) -> dict:

    metrics = {
        "total_users": events_df["user_id"].nunique(),
        "total_sessions": events_df["session_id"].nunique(),
        "total_searches": (events_df["event_name"] == "search").sum(),
        "total_clicks": (events_df["event_name"] == "click").sum(),
        "total_add_to_carts": (
            events_df["event_name"] == "add_to_cart"
        ).sum(),
        "total_purchases": (
            events_df["event_name"] == "purchase"
        ).sum(),
    }

    return metrics


# ---------------------------------------------------------
# 3. Search → Click CTR
# ---------------------------------------------------------

def calculate_ctr(events_df: pd.DataFrame) -> float:

    searches = (events_df["event_name"] == "search").sum()
    clicks = (events_df["event_name"] == "click").sum()

    if searches == 0:
        return 0.0

    return clicks / searches


# ---------------------------------------------------------
# 4. User-level conversion rate
# ---------------------------------------------------------

def calculate_user_conversion(events_df: pd.DataFrame) -> float:

    user_purchase = (
        events_df.assign(
            is_purchase=(
                events_df["event_name"] == "purchase"
            ).astype(int)
        )
        .groupby("user_id")["is_purchase"]
        .max()
    )

    if len(user_purchase) == 0:
        return 0.0

    return user_purchase.mean()


# ---------------------------------------------------------
# 5. Funnel metrics
# ---------------------------------------------------------

def calculate_funnel(events_df: pd.DataFrame) -> pd.DataFrame:

    funnel_order = [
        "app_open",
        "search",
        "click",
        "add_to_cart",
        "purchase",
    ]

    rows = []

    total_sessions = events_df["session_id"].nunique()

    for event_name in funnel_order:

        event_sessions = events_df.loc[
            events_df["event_name"] == event_name,
            "session_id",
        ].nunique()

        rate_from_start = (
            event_sessions / total_sessions
            if total_sessions > 0
            else 0.0
        )

        rows.append(
            {
                "funnel_step": event_name,
                "sessions": event_sessions,
                "rate_from_start": rate_from_start,
            }
        )

    funnel_df = pd.DataFrame(rows)

    funnel_df["step_conversion_rate"] = (
        funnel_df["sessions"]
        / funnel_df["sessions"].shift(1)
    )

    funnel_df.loc[
        0,
        "step_conversion_rate",
    ] = 1.0

    funnel_df["drop_off_rate"] = (
        1 - funnel_df["step_conversion_rate"]
    )

    return funnel_df


# ---------------------------------------------------------
# 6. Revenue metrics
# ---------------------------------------------------------

def calculate_revenue_metrics(events_df: pd.DataFrame) -> dict:

    purchases = events_df[
        events_df["event_name"] == "purchase"
    ].copy()

    if purchases.empty:
        return {
            "revenue": 0.0,
            "orders": 0,
            "average_order_value": 0.0,
        }

    purchases["revenue"] = (
        purchases["quantity"]
        * purchases["unit_price"]
    )

    total_revenue = purchases["revenue"].sum()

    total_orders = purchases["order_id"].nunique()

    average_order_value = (
        total_revenue / total_orders
        if total_orders > 0
        else 0.0
    )

    return {
        "revenue": total_revenue,
        "orders": total_orders,
        "average_order_value": average_order_value,
    }


# ---------------------------------------------------------
# 7. Experiment-group metrics
# ---------------------------------------------------------

def calculate_experiment_metrics(
    events_df: pd.DataFrame,
) -> pd.DataFrame:

    rows = []

    for experiment_group, group_df in events_df.groupby(
        "experiment_group"
    ):

        basic_counts = calculate_basic_counts(group_df)

        ctr = calculate_ctr(group_df)

        conversion_rate = calculate_user_conversion(group_df)

        revenue_metrics = calculate_revenue_metrics(group_df)

        rows.append(
            {
                "experiment_group": experiment_group,
                "users": basic_counts["total_users"],
                "sessions": basic_counts["total_sessions"],
                "ctr": ctr,
                "user_conversion_rate": conversion_rate,
                "revenue": revenue_metrics["revenue"],
                "orders": revenue_metrics["orders"],
                "average_order_value": (
                    revenue_metrics["average_order_value"]
                ),
            }
        )

    return pd.DataFrame(rows)

# ---------------------------------------------------------
# 8. Segment-level metrics
# ---------------------------------------------------------

def calculate_segment_metrics(
    events_df: pd.DataFrame,
    segment_column: str,
) -> pd.DataFrame:

    rows = []

    for segment_value, segment_df in events_df.groupby(segment_column):

        basic_counts = calculate_basic_counts(segment_df)
        ctr = calculate_ctr(segment_df)
        conversion_rate = calculate_user_conversion(segment_df)
        revenue_metrics = calculate_revenue_metrics(segment_df)

        rows.append(
            {
                segment_column: segment_value,
                "users": basic_counts["total_users"],
                "sessions": basic_counts["total_sessions"],
                "ctr": ctr,
                "user_conversion_rate": conversion_rate,
                "revenue": revenue_metrics["revenue"],
                "orders": revenue_metrics["orders"],
                "average_order_value": (
                    revenue_metrics["average_order_value"]
                ),
            }
        )

    return pd.DataFrame(rows)

# ---------------------------------------------------------
# 9. Save analytical outputs
# ---------------------------------------------------------

def save_outputs(
    basic_counts: dict,
    funnel_df: pd.DataFrame,
    experiment_df: pd.DataFrame,
    segment_dfs: dict,
) -> None:

    project_root = Path(__file__).resolve().parents[2]

    output_directory = project_root / "data" / "processed"

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    core_metrics_df = pd.DataFrame(
        [basic_counts]
    )

    core_metrics_df.to_csv(
        output_directory / "core_metrics.csv",
        index=False,
    )

    funnel_df.to_csv(
        output_directory / "funnel_metrics.csv",
        index=False,
    )

    experiment_df.to_csv(
        output_directory / "experiment_metrics.csv",
        index=False,
    )

    for segment_name, segment_df in segment_dfs.items():

        segment_df.to_csv(
            output_directory / f"{segment_name}_metrics.csv",
            index=False,
        )

# ---------------------------------------------------------
# 10. Run analytics
# ---------------------------------------------------------

def main():

    events_df = load_events()

    print(f"Loaded {len(events_df):,} raw events.")
    print()

    basic_counts = calculate_basic_counts(events_df)

    print("CORE COUNTS")
    print("-" * 40)

    for metric, value in basic_counts.items():
        print(f"{metric}: {value:,}")

    print()

    ctr = calculate_ctr(events_df)
    conversion_rate = calculate_user_conversion(events_df)

    print("CORE PRODUCT METRICS")
    print("-" * 40)
    print(f"Search-to-click CTR: {ctr:.2%}")
    print(f"User conversion rate: {conversion_rate:.2%}")

    print()

    revenue_metrics = calculate_revenue_metrics(events_df)

    print("REVENUE METRICS")
    print("-" * 40)
    print(f"Revenue: {revenue_metrics['revenue']:,.2f}")
    print(f"Orders: {revenue_metrics['orders']:,}")
    print(
        "Average order value: "
        f"{revenue_metrics['average_order_value']:,.2f}"
    )

    print()

    funnel_df = calculate_funnel(events_df)

    print("SESSION FUNNEL")
    print("-" * 40)
    print(funnel_df.to_string(index=False))

    print()

    experiment_df = calculate_experiment_metrics(events_df)

    print("EXPERIMENT GROUP METRICS")
    print("-" * 40)
    print(experiment_df.to_string(index=False))

    print()

    segment_columns = [
        "country",
        "platform",
        "device_type",
        "app_version",
    ]

    segment_dfs = {}

    for segment_column in segment_columns:

        segment_df = calculate_segment_metrics(
            events_df,
            segment_column,
        )

        segment_dfs[segment_column] = segment_df

        print(
            f"{segment_column.upper()} METRICS"
        )
        print("-" * 40)
        print(
            segment_df.to_string(
                index=False
            )
        )
        print()

    save_outputs(
        basic_counts=basic_counts,
        funnel_df=funnel_df,
        experiment_df=experiment_df,
        segment_dfs=segment_dfs,
    )

    print(
        "Analytical outputs saved to data/processed/"
    )

if __name__ == "__main__":
    main()