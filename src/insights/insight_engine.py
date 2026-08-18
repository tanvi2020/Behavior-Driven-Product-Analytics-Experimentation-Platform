from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_PATH = PROCESSED_DIR / "product_insights.csv"


def load_funnel_metrics():
    """
    Load previously calculated funnel metrics.
    """
    funnel_path = PROCESSED_DIR / "funnel_metrics.csv"

    if not funnel_path.exists():
        raise FileNotFoundError(
            f"Funnel metrics not found: {funnel_path}"
        )

    return pd.read_csv(funnel_path)


def detect_funnel_bottleneck(funnel_df):
    """
    Identify the funnel transition with the highest drop-off rate.
    """

    required_columns = {
        "funnel_step",
        "sessions",
        "drop_off_rate",
    }

    missing_columns = required_columns - set(funnel_df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required funnel columns: {missing_columns}"
        )

    # The first funnel step has no meaningful previous-step drop-off.
    comparable_steps = funnel_df.iloc[1:].copy()

    if comparable_steps.empty:
        raise ValueError(
            "Not enough funnel steps to detect a bottleneck."
        )

    bottleneck_index = comparable_steps["drop_off_rate"].idxmax()
    bottleneck = comparable_steps.loc[bottleneck_index]

    previous_index = funnel_df.index.get_loc(bottleneck_index) - 1
    previous_step = funnel_df.iloc[previous_index]["funnel_step"]

    insight = {
        "insight_type": "funnel_bottleneck",
        "priority": "HIGH",
        "segment": "overall",
        "metric": "drop_off_rate",
        "value": bottleneck["drop_off_rate"],
        "insight": (
            f"The largest funnel drop-off occurs between "
            f"{previous_step} and {bottleneck['funnel_step']}, "
            f"with a drop-off rate of "
            f"{bottleneck['drop_off_rate']:.2%}."
        ),
        "recommended_investigation": (
            f"Investigate user behavior and friction between "
            f"{previous_step} and {bottleneck['funnel_step']}."
        ),
    }

    return insight

def load_country_metrics():
    """
    Load country-level product metrics.
    """
    country_path = PROCESSED_DIR / "country_metrics.csv"

    if not country_path.exists():
        raise FileNotFoundError(
            f"Country metrics not found: {country_path}"
        )

    return pd.read_csv(country_path)


def detect_country_opportunities(
    country_df,
    low_gap_threshold=-0.02,
    high_gap_threshold=0.02,
):
    """
    Compare each country's conversion rate against
    the overall user-weighted benchmark.

    Returns a list of prioritized insights.
    """

    required_columns = {
        "country",
        "users",
        "user_conversion_rate",
    }

    missing_columns = required_columns - set(country_df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required country columns: {missing_columns}"
        )

    total_users = country_df["users"].sum()

    if total_users == 0:
        raise ValueError(
            "Country metrics contain zero total users."
        )

    overall_conversion = (
        (
            country_df["users"]
            * country_df["user_conversion_rate"]
        ).sum()
        / total_users
    )

    insights = []

    for _, row in country_df.iterrows():

        country = row["country"]
        conversion_rate = row["user_conversion_rate"]

        gap = conversion_rate - overall_conversion

        if gap <= low_gap_threshold:

            priority = (
                "HIGH"
                if gap <= -0.04
                else "MEDIUM"
            )

            insights.append(
                {
                    "insight_type": "segment_underperformance",
                    "priority": priority,
                    "segment": country,
                    "metric": "user_conversion_rate",
                    "value": conversion_rate,
                    "benchmark": overall_conversion,
                    "gap": gap,
                    "insight": (
                        f"{country} conversion is "
                        f"{conversion_rate:.2%}, which is "
                        f"{abs(gap):.2%} below the overall "
                        f"benchmark of {overall_conversion:.2%}."
                    ),
                    "recommended_investigation": (
                        f"Compare {country}'s funnel stages, "
                        f"device/platform mix, and checkout behavior "
                        f"with higher-performing countries."
                    ),
                }
            )

        elif gap >= high_gap_threshold:

            priority = (
                "HIGH"
                if gap >= 0.04
                else "MEDIUM"
            )

            insights.append(
                {
                    "insight_type": "segment_outperformance",
                    "priority": priority,
                    "segment": country,
                    "metric": "user_conversion_rate",
                    "value": conversion_rate,
                    "benchmark": overall_conversion,
                    "gap": gap,
                    "insight": (
                        f"{country} conversion is "
                        f"{conversion_rate:.2%}, which is "
                        f"{gap:.2%} above the overall "
                        f"benchmark of {overall_conversion:.2%}."
                    ),
                    "recommended_investigation": (
                        f"Investigate what differs in {country} "
                        f"across funnel progression, platform mix, "
                        f"and purchase behavior."
                    ),
                }
            )

    return insights
def load_experiment_summary():
    """
    Load persisted experiment summary.
    """
    summary_path = (
        PROCESSED_DIR / "experiment_summary.csv"
    )

    if not summary_path.exists():
        raise FileNotFoundError(
            f"Experiment summary not found: {summary_path}"
        )

    summary_df = pd.read_csv(summary_path)

    if summary_df.empty:
        raise ValueError(
            "Experiment summary is empty."
        )

    return summary_df


def interpret_experiment(
    experiment_summary_df,
    alpha=0.05,
):
    """
    Combine statistical evidence, experiment health,
    and guardrail status into one cautious interpretation.
    """

    required_columns = {
        "control_conversion_rate",
        "treatment_conversion_rate",
        "absolute_lift",
        "relative_lift",
        "p_value",
        "ci_lower_bound",
        "ci_upper_bound",
        "srm_detected",
        "assignment_valid",
        "any_guardrail_failed",
    }

    missing_columns = (
        required_columns
        - set(experiment_summary_df.columns)
    )

    if missing_columns:
        raise ValueError(
            f"Missing experiment summary columns: "
            f"{missing_columns}"
        )

    row = experiment_summary_df.iloc[0]

    control_rate = row[
        "control_conversion_rate"
    ]

    treatment_rate = row[
        "treatment_conversion_rate"
    ]

    absolute_lift = row[
        "absolute_lift"
    ]

    relative_lift = row[
        "relative_lift"
    ]

    p_value = row[
        "p_value"
    ]

    ci_lower = row[
        "ci_lower_bound"
    ]

    ci_upper = row[
        "ci_upper_bound"
    ]

    srm_detected = bool(
        row["srm_detected"]
    )

    assignment_valid = bool(
        row["assignment_valid"]
    )

    guardrail_failed = bool(
        row["any_guardrail_failed"]
    )

    statistically_significant = (
        p_value < alpha
    )

    positive_lift = (
        absolute_lift > 0
    )

    # -------------------------------------------------
    # Invalid / untrustworthy experiment
    # -------------------------------------------------

    if srm_detected:

        return {
            "insight_type": "experiment_health",
            "priority": "HIGH",
            "segment": "overall",
            "metric": "experiment_validity",
            "value": p_value,
            "insight": (
                "The experiment shows a sample ratio mismatch, "
                "so the treatment-effect estimate should not be "
                "trusted until assignment or logging issues are "
                "investigated."
            ),
            "recommended_investigation": (
                "Investigate randomization, exposure logging, "
                "eligibility rules, and control/treatment traffic."
            ),
        }

    if not assignment_valid:

        return {
            "insight_type": "experiment_health",
            "priority": "HIGH",
            "segment": "overall",
            "metric": "experiment_assignment",
            "value": absolute_lift,
            "insight": (
                "Experiment assignment validation failed, so the "
                "observed treatment effect should not be used for "
                "a product decision yet."
            ),
            "recommended_investigation": (
                "Investigate users with missing or conflicting "
                "experiment assignments."
            ),
        }

    # -------------------------------------------------
    # Guardrail issue
    # -------------------------------------------------

    if guardrail_failed:

        return {
            "insight_type": "experiment_guardrail",
            "priority": "HIGH",
            "segment": "overall",
            "metric": "guardrail_status",
            "value": absolute_lift,
            "insight": (
                f"Treatment conversion changed from "
                f"{control_rate:.2%} to {treatment_rate:.2%}, "
                f"but at least one guardrail deteriorated beyond "
                f"the V1 threshold."
            ),
            "recommended_investigation": (
                "Identify which guardrail failed and evaluate "
                "whether the primary-metric gain justifies the "
                "observed trade-off."
            ),
        }

    # -------------------------------------------------
    # Positive statistically significant result
    # -------------------------------------------------

    if (
        statistically_significant
        and positive_lift
    ):

        return {
            "insight_type": "experiment_positive_signal",
            "priority": "HIGH",
            "segment": "overall",
            "metric": "user_conversion_rate",
            "value": absolute_lift,
            "insight": (
                f"Treatment conversion increased from "
                f"{control_rate:.2%} to {treatment_rate:.2%}. "
                f"The absolute lift is {absolute_lift:.2%} "
                f"({relative_lift:.2%} relative), with "
                f"p={p_value:.4f} and a 95% confidence interval "
                f"of [{ci_lower:.2%}, {ci_upper:.2%}]. "
                f"No V1 SRM, assignment, or guardrail issue "
                f"was detected."
            ),
            "recommended_investigation": (
                "Consider treatment for rollout evaluation, while "
                "reviewing practical significance, implementation "
                "cost, segment-level effects, and longer-term risk."
            ),
        }

    # -------------------------------------------------
    # Significant negative result
    # -------------------------------------------------

    if (
        statistically_significant
        and not positive_lift
    ):

        return {
            "insight_type": "experiment_negative_signal",
            "priority": "HIGH",
            "segment": "overall",
            "metric": "user_conversion_rate",
            "value": absolute_lift,
            "insight": (
                f"Treatment produced a statistically significant "
                f"negative conversion effect of "
                f"{absolute_lift:.2%}."
            ),
            "recommended_investigation": (
                "Investigate treatment behavior and affected "
                "segments before considering any rollout."
            ),
        }

    # -------------------------------------------------
    # Inconclusive result
    # -------------------------------------------------

    return {
        "insight_type": "experiment_inconclusive",
        "priority": "MEDIUM",
        "segment": "overall",
        "metric": "user_conversion_rate",
        "value": absolute_lift,
        "insight": (
            f"Treatment conversion changed from "
            f"{control_rate:.2%} to {treatment_rate:.2%}, "
            f"but the evidence is not statistically conclusive "
            f"at alpha={alpha:.2f} "
            f"(p={p_value:.4f})."
        ),
        "recommended_investigation": (
            "Avoid declaring a treatment winner. Review sample "
            "size, experiment duration, minimum detectable effect, "
            "and whether more data is needed."
        ),
    }

def rank_insights(insights):
    """
    Add a simple priority score and sort insights so
    the most important findings appear first.
    """

    priority_map = {
        "HIGH": 3,
        "MEDIUM": 2,
        "LOW": 1,
    }

    ranked_insights = []

    for insight in insights:

        ranked_insight = insight.copy()

        priority_score = priority_map.get(
            ranked_insight.get("priority"),
            0,
        )

        # Use magnitude of gap/value only as a secondary signal.
        if "gap" in ranked_insight:
            impact_score = abs(
                ranked_insight["gap"]
            )

        elif "value" in ranked_insight:
            try:
                impact_score = abs(
                    float(ranked_insight["value"])
                )
            except (TypeError, ValueError):
                impact_score = 0.0

        else:
            impact_score = 0.0

        ranked_insight[
            "priority_score"
        ] = priority_score

        ranked_insight[
            "impact_score"
        ] = impact_score

        ranked_insights.append(
            ranked_insight
        )

    ranked_insights = sorted(
        ranked_insights,
        key=lambda x: (
            x["priority_score"],
            x["impact_score"],
        ),
        reverse=True,
    )

    for rank, insight in enumerate(
        ranked_insights,
        start=1,
    ):
        insight["rank"] = rank

    return ranked_insights


def main():

    all_insights = []

    # Funnel insight
    funnel_df = load_funnel_metrics()

    bottleneck_insight = detect_funnel_bottleneck(
        funnel_df
    )

    all_insights.append(
        bottleneck_insight
    )

    # Country insights
    country_df = load_country_metrics()

    country_insights = detect_country_opportunities(
        country_df
    )

    all_insights.extend(
        country_insights
    )

    # Experiment interpretation
    experiment_summary_df = (
        load_experiment_summary()
    )

    experiment_insight = interpret_experiment(
        experiment_summary_df
    )

    all_insights.append(
        experiment_insight
    )

    all_insights = rank_insights(
        all_insights
    )

    # Save all insights
    insights_df = pd.DataFrame(
        all_insights
    )

    insights_df.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print("BEHAVIOR-DRIVEN INSIGHTS")
    print("-" * 60)

    for insight in all_insights:

        print()

        print(
        f"Rank: {insight['rank']}"
        )
    
        print(
            f"Priority: {insight['priority']}"
        )

        print(
            insight["insight"]
        )

        print(
            "Recommended investigation:"
        )

        print(
            insight["recommended_investigation"]
        )

    print()
    print(
        f"Insights saved to {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()