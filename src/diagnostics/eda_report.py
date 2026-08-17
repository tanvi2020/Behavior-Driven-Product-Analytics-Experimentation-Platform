from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


# ---------------------------------------------------------
# 1. Load data
# ---------------------------------------------------------

def load_data():
    project_root = Path(__file__).resolve().parents[2]

    raw_events_path = (
        project_root / "data" / "raw" / "events.csv"
    )

    processed_dir = (
        project_root / "data" / "processed"
    )

    events_df = pd.read_csv(
        raw_events_path,
        parse_dates=["event_timestamp"],
    )

    funnel_df = pd.read_csv(
        processed_dir / "funnel_metrics.csv"
    )

    experiment_df = pd.read_csv(
        processed_dir / "experiment_group_statistics.csv"
    )

    country_df = pd.read_csv(
        processed_dir / "country_metrics.csv"
    )

    platform_df = pd.read_csv(
        processed_dir / "platform_metrics.csv"
    )

    device_df = pd.read_csv(
        processed_dir / "device_type_metrics.csv"
    )

    guardrail_df = pd.read_csv(
        processed_dir / "experiment_guardrails.csv"
    )

    return (
        events_df,
        funnel_df,
        experiment_df,
        country_df,
        platform_df,
        device_df,
        guardrail_df,
    )


# ---------------------------------------------------------
# 2. Create output directory
# ---------------------------------------------------------

def get_output_directory():
    project_root = Path(__file__).resolve().parents[2]

    output_directory = (
        project_root / "outputs" / "figures"
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    return output_directory


# ---------------------------------------------------------
# 3. Daily event trend
# ---------------------------------------------------------

def plot_daily_event_trend(
    events_df: pd.DataFrame,
    output_directory: Path,
):
    daily_events = (
        events_df
        .assign(
            event_date=events_df[
                "event_timestamp"
            ].dt.date
        )
        .groupby("event_date")
        .size()
        .reset_index(name="event_count")
    )

    plt.figure(figsize=(10, 5))

    plt.plot(
        daily_events["event_date"],
        daily_events["event_count"],
        marker="o",
    )

    plt.title("Daily Event Volume")
    plt.xlabel("Date")
    plt.ylabel("Number of Events")
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig(
        output_directory / "daily_event_volume.png"
    )

    plt.close()


# ---------------------------------------------------------
# 4. Funnel visualization
# ---------------------------------------------------------

def plot_funnel(
    funnel_df: pd.DataFrame,
    output_directory: Path,
):
    plt.figure(figsize=(8, 5))

    plt.bar(
        funnel_df["funnel_step"],
        funnel_df["sessions"],
    )

    plt.title("Product Funnel")
    plt.xlabel("Funnel Step")
    plt.ylabel("Sessions")
    plt.xticks(rotation=30)
    plt.tight_layout()

    plt.savefig(
        output_directory / "product_funnel.png"
    )

    plt.close()


# ---------------------------------------------------------
# 5. Experiment conversion comparison
# ---------------------------------------------------------

def plot_experiment_conversion(
    experiment_df: pd.DataFrame,
    output_directory: Path,
):
    plt.figure(figsize=(7, 5))

    plt.bar(
        experiment_df["experiment_group"],
        experiment_df["conversion_rate"],
    )

    plt.title("Control vs Treatment Conversion")
    plt.xlabel("Experiment Group")
    plt.ylabel("Conversion Rate")
    plt.tight_layout()

    plt.savefig(
        output_directory
        / "experiment_conversion_comparison.png"
    )

    plt.close()


# ---------------------------------------------------------
# 6. Country conversion comparison
# ---------------------------------------------------------

def plot_country_conversion(
    country_df: pd.DataFrame,
    output_directory: Path,
):
    country_df = country_df.sort_values(
        "user_conversion_rate",
        ascending=False,
    )

    plt.figure(figsize=(8, 5))

    plt.bar(
        country_df["country"],
        country_df["user_conversion_rate"],
    )

    plt.title("Conversion Rate by Country")
    plt.xlabel("Country")
    plt.ylabel("User Conversion Rate")
    plt.tight_layout()

    plt.savefig(
        output_directory / "conversion_by_country.png"
    )

    plt.close()


# ---------------------------------------------------------
# 7. Platform conversion comparison
# ---------------------------------------------------------

def plot_platform_conversion(
    platform_df: pd.DataFrame,
    output_directory: Path,
):
    platform_df = platform_df.sort_values(
        "user_conversion_rate",
        ascending=False,
    )

    plt.figure(figsize=(8, 5))

    plt.bar(
        platform_df["platform"],
        platform_df["user_conversion_rate"],
    )

    plt.title("Conversion Rate by Platform")
    plt.xlabel("Platform")
    plt.ylabel("User Conversion Rate")
    plt.tight_layout()

    plt.savefig(
        output_directory / "conversion_by_platform.png"
    )

    plt.close()


# ---------------------------------------------------------
# 8. Device CTR comparison
# ---------------------------------------------------------

def plot_device_ctr(
    device_df: pd.DataFrame,
    output_directory: Path,
):
    device_df = device_df.sort_values(
        "ctr",
        ascending=False,
    )

    plt.figure(figsize=(8, 5))

    plt.bar(
        device_df["device_type"],
        device_df["ctr"],
    )

    plt.title("CTR by Device Type")
    plt.xlabel("Device Type")
    plt.ylabel("CTR")
    plt.tight_layout()

    plt.savefig(
        output_directory / "ctr_by_device.png"
    )

    plt.close()


# ---------------------------------------------------------
# 9. Guardrail comparison
# ---------------------------------------------------------

def plot_guardrails(
    guardrail_df: pd.DataFrame,
    output_directory: Path,
):
    for _, row in guardrail_df.iterrows():

        metric_name = row["metric"]

        values = [
            row["control_value"],
            row["treatment_value"],
        ]

        groups = [
            "control",
            "treatment",
        ]

        plt.figure(figsize=(7, 5))

        plt.bar(
            groups,
            values,
        )

        plt.title(
            f"Guardrail Comparison: {metric_name}"
        )

        plt.xlabel("Experiment Group")
        plt.ylabel(metric_name)
        plt.tight_layout()

        safe_metric_name = metric_name.replace(
            " ",
            "_",
        )

        plt.savefig(
            output_directory
            / f"guardrail_{safe_metric_name}.png"
        )

        plt.close()


# ---------------------------------------------------------
# 10. Daily conversion trend
# ---------------------------------------------------------

def plot_daily_conversion(
    events_df: pd.DataFrame,
    output_directory: Path,
):
    events_df = events_df.copy()

    events_df["event_date"] = (
        events_df["event_timestamp"].dt.date
    )

    user_daily = (
        events_df
        .assign(
            converted=(
                events_df["event_name"]
                == "purchase"
            ).astype(int)
        )
        .groupby(
            [
                "event_date",
                "user_id",
            ],
            as_index=False,
        )
        .agg(
            converted=("converted", "max")
        )
    )

    daily_conversion = (
        user_daily
        .groupby(
            "event_date",
            as_index=False,
        )
        .agg(
            conversion_rate=(
                "converted",
                "mean",
            )
        )
    )

    plt.figure(figsize=(10, 5))

    plt.plot(
        daily_conversion["event_date"],
        daily_conversion["conversion_rate"],
        marker="o",
    )

    plt.title("Daily User Conversion Rate")
    plt.xlabel("Date")
    plt.ylabel("Conversion Rate")
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig(
        output_directory
        / "daily_conversion_rate.png"
    )

    plt.close()


# ---------------------------------------------------------
# 11. Main EDA pipeline
# ---------------------------------------------------------

def main():

    (
        events_df,
        funnel_df,
        experiment_df,
        country_df,
        platform_df,
        device_df,
        guardrail_df,
    ) = load_data()

    output_directory = get_output_directory()

    plot_daily_event_trend(
        events_df,
        output_directory,
    )

    plot_funnel(
        funnel_df,
        output_directory,
    )

    plot_experiment_conversion(
        experiment_df,
        output_directory,
    )

    plot_country_conversion(
        country_df,
        output_directory,
    )

    plot_platform_conversion(
        platform_df,
        output_directory,
    )

    plot_device_ctr(
        device_df,
        output_directory,
    )

    plot_guardrails(
        guardrail_df,
        output_directory,
    )

    plot_daily_conversion(
        events_df,
        output_directory,
    )

    print("EDA report generation complete.")
    print(
        f"Figures saved to: {output_directory}"
    )


if __name__ == "__main__":
    main()