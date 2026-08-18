from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm, chisquare

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from config.settings import ALPHA

# ---------------------------------------------------------
# 1. Load raw events
# ---------------------------------------------------------

def load_events() -> pd.DataFrame:
    project_root = Path(__file__).resolve().parents[2]
    events_path = project_root / "data" / "raw" / "events.csv"

    return pd.read_csv(
        events_path,
        parse_dates=["event_timestamp"],
    )


# ---------------------------------------------------------
# 2. Build user-level experiment table
# ---------------------------------------------------------

def build_user_experiment_table(
    events_df: pd.DataFrame,
) -> pd.DataFrame:

    user_table = (
        events_df.assign(
            converted=(
                events_df["event_name"] == "purchase"
            ).astype(int)
        )
        .groupby(
            ["user_id", "experiment_group"],
            as_index=False,
        )
        .agg(
            converted=("converted", "max"),
        )
    )

    return user_table


# ---------------------------------------------------------
# 3. Calculate group statistics
# ---------------------------------------------------------

def calculate_group_statistics(
    user_table: pd.DataFrame,
) -> pd.DataFrame:

    group_stats = (
        user_table
        .groupby(
            "experiment_group",
            as_index=False,
        )
        .agg(
            users=("user_id", "nunique"),
            conversions=("converted", "sum"),
            conversion_rate=("converted", "mean"),
        )
    )

    return group_stats


# ---------------------------------------------------------
# 4. Calculate treatment effect
# ---------------------------------------------------------

def calculate_treatment_effect(
    group_stats: pd.DataFrame,
) -> dict:

    control = group_stats[
        group_stats["experiment_group"] == "control"
    ].iloc[0]

    treatment = group_stats[
        group_stats["experiment_group"] == "treatment"
    ].iloc[0]

    control_rate = control["conversion_rate"]
    treatment_rate = treatment["conversion_rate"]

    absolute_lift = treatment_rate - control_rate

    relative_lift = (
        absolute_lift / control_rate
        if control_rate > 0
        else np.nan
    )

    return {
        "control_rate": control_rate,
        "treatment_rate": treatment_rate,
        "absolute_lift": absolute_lift,
        "relative_lift": relative_lift,
    }


# ---------------------------------------------------------
# 5. Two-proportion z-test
# ---------------------------------------------------------

def run_proportion_z_test(
    group_stats: pd.DataFrame,
) -> dict:

    control = group_stats[
        group_stats["experiment_group"] == "control"
    ].iloc[0]

    treatment = group_stats[
        group_stats["experiment_group"] == "treatment"
    ].iloc[0]

    x_control = control["conversions"]
    n_control = control["users"]

    x_treatment = treatment["conversions"]
    n_treatment = treatment["users"]

    p_control = x_control / n_control
    p_treatment = x_treatment / n_treatment

    pooled_probability = (
        (x_control + x_treatment)
        / (n_control + n_treatment)
    )

    standard_error = np.sqrt(
        pooled_probability
        * (1 - pooled_probability)
        * (
            (1 / n_control)
            + (1 / n_treatment)
        )
    )

    if standard_error == 0:
        return {
            "z_statistic": 0.0,
            "p_value": 1.0,
        }

    z_statistic = (
        p_treatment - p_control
    ) / standard_error

    p_value = 2 * (
        1 - norm.cdf(abs(z_statistic))
    )

    return {
        "z_statistic": z_statistic,
        "p_value": p_value,
    }


# ---------------------------------------------------------
# 6. Confidence interval for treatment effect
# ---------------------------------------------------------

def calculate_lift_confidence_interval(
    group_stats: pd.DataFrame,
    confidence_level: float = 0.95,
) -> dict:

    control = group_stats[
        group_stats["experiment_group"] == "control"
    ].iloc[0]

    treatment = group_stats[
        group_stats["experiment_group"] == "treatment"
    ].iloc[0]

    p_control = control["conversion_rate"]
    p_treatment = treatment["conversion_rate"]

    n_control = control["users"]
    n_treatment = treatment["users"]

    lift = p_treatment - p_control

    standard_error = np.sqrt(
        (p_control * (1 - p_control) / n_control)
        +
        (p_treatment * (1 - p_treatment) / n_treatment)
    )

    alpha = 1 - confidence_level

    critical_value = norm.ppf(
        1 - alpha / 2
    )

    margin_of_error = (
        critical_value * standard_error
    )

    lower_bound = lift - margin_of_error
    upper_bound = lift + margin_of_error

    return {
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
    }


# ---------------------------------------------------------
# 7. Sample Ratio Mismatch (SRM)
# ---------------------------------------------------------

def check_sample_ratio_mismatch(
    user_table: pd.DataFrame,
    expected_control_share: float = 0.50,
) -> dict:

    group_counts = (
        user_table["experiment_group"]
        .value_counts()
    )

    control_count = group_counts.get(
        "control",
        0,
    )

    treatment_count = group_counts.get(
        "treatment",
        0,
    )

    total_users = (
        control_count
        + treatment_count
    )

    expected_counts = [
        total_users * expected_control_share,
        total_users * (1 - expected_control_share),
    ]

    observed_counts = [
        control_count,
        treatment_count,
    ]

    chi_square_statistic, p_value = chisquare(
        f_obs=observed_counts,
        f_exp=expected_counts,
    )

    return {
        "control_users": control_count,
        "treatment_users": treatment_count,
        "chi_square_statistic": chi_square_statistic,
        "p_value": p_value,
        "srm_detected": p_value < 0.01,
    }


# ---------------------------------------------------------
# 8. Basic experiment validity checks
# ---------------------------------------------------------

def validate_experiment_assignment(
    events_df: pd.DataFrame,
) -> dict:

    missing_group_users = (
        events_df.loc[
            events_df["experiment_group"].isna(),
            "user_id",
        ]
        .nunique()
    )

    user_group_counts = (
        events_df[
            [
                "user_id",
                "experiment_group",
            ]
        ]
        .drop_duplicates()
        .groupby("user_id")[
            "experiment_group"
        ]
        .nunique()
    )

    users_in_multiple_groups = (
        user_group_counts > 1
    ).sum()

    valid = (
        missing_group_users == 0
        and users_in_multiple_groups == 0
    )

    return {
        "missing_group_users": (
            missing_group_users
        ),
        "users_in_multiple_groups": (
            users_in_multiple_groups
        ),
        "valid_assignment": valid,
    }


# ---------------------------------------------------------
# 9. Guardrail metrics
# ---------------------------------------------------------

def calculate_guardrail_metrics(
    events_df: pd.DataFrame,
) -> dict:

    results = {}

    for group_name in ["control", "treatment"]:

        group_df = events_df[
            events_df["experiment_group"] == group_name
        ]

        searches = (
            group_df["event_name"] == "search"
        ).sum()

        clicks = (
            group_df["event_name"] == "click"
        ).sum()

        ctr = (
            clicks / searches
            if searches > 0
            else 0.0
        )

        purchases = group_df[
            group_df["event_name"] == "purchase"
        ].copy()

        if purchases.empty:
            average_order_value = 0.0

        else:
            purchases["revenue"] = (
                purchases["quantity"]
                * purchases["unit_price"]
            )

            total_revenue = purchases[
                "revenue"
            ].sum()

            total_orders = purchases[
                "order_id"
            ].nunique()

            average_order_value = (
                total_revenue / total_orders
                if total_orders > 0
                else 0.0
            )

        results[group_name] = {
            "ctr": ctr,
            "average_order_value": average_order_value,
        }

    return results


# ---------------------------------------------------------
# 10. Guardrail comparison
# ---------------------------------------------------------

def evaluate_guardrails(
    guardrail_metrics: dict,
    max_allowed_relative_decline: float = 0.05,
) -> dict:

    control = guardrail_metrics["control"]
    treatment = guardrail_metrics["treatment"]

    ctr_relative_change = (
        (
            treatment["ctr"] - control["ctr"]
        )
        / control["ctr"]
        if control["ctr"] > 0
        else 0.0
    )

    aov_relative_change = (
        (
            treatment["average_order_value"]
            - control["average_order_value"]
        )
        / control["average_order_value"]
        if control["average_order_value"] > 0
        else 0.0
    )

    ctr_guardrail_failed = (
        ctr_relative_change
        < -max_allowed_relative_decline
    )

    aov_guardrail_failed = (
        aov_relative_change
        < -max_allowed_relative_decline
    )

    any_guardrail_failed = (
        ctr_guardrail_failed
        or aov_guardrail_failed
    )

    return {
        "ctr_relative_change": ctr_relative_change,
        "aov_relative_change": aov_relative_change,
        "ctr_guardrail_failed": ctr_guardrail_failed,
        "aov_guardrail_failed": aov_guardrail_failed,
        "any_guardrail_failed": any_guardrail_failed,
    }


# ---------------------------------------------------------
# 11. Experiment decision
# ---------------------------------------------------------

def make_experiment_decision(
    treatment_effect: dict,
    z_test: dict,
    srm_result: dict,
    assignment_validation: dict,
    guardrail_result: dict,
    alpha: float = ALPHA,
) -> str:

    if srm_result["srm_detected"]:
        return (
            "Do not trust experiment result: "
            "sample ratio mismatch detected."
        )

    if not assignment_validation["valid_assignment"]:
        return (
            "Do not trust experiment result: "
            "experiment assignment is invalid."
        )

    if guardrail_result["any_guardrail_failed"]:
        return (
            "Treatment improves the primary metric, "
            "but at least one guardrail metric failed. "
            "Investigate before rollout."
        )

    if (
        z_test["p_value"] < alpha
        and treatment_effect["absolute_lift"] > 0
    ):
        return (
            "Treatment shows a statistically significant "
            "positive lift with no V1 guardrail failure."
        )

    if (
        z_test["p_value"] < alpha
        and treatment_effect["absolute_lift"] < 0
    ):
        return (
            "Treatment shows a statistically significant "
            "negative effect."
        )

    return (
        "No statistically significant difference detected."
    )


# ---------------------------------------------------------
# 12. Save experiment outputs
# ---------------------------------------------------------

def save_experiment_outputs(
    group_stats: pd.DataFrame,
    treatment_effect: dict,
    z_test: dict,
    confidence_interval: dict,
    srm_result: dict,
    assignment_validation: dict,
    guardrail_metrics: dict,
    guardrail_result: dict,
) -> None:

    project_root = Path(__file__).resolve().parents[2]
    output_directory = project_root / "data" / "processed"

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Group-level experiment statistics
    group_stats.to_csv(
        output_directory / "experiment_group_statistics.csv",
        index=False,
    )

    # One-row experiment summary
    experiment_summary = pd.DataFrame(
        [
            {
                "control_conversion_rate": treatment_effect[
                    "control_rate"
                ],
                "treatment_conversion_rate": treatment_effect[
                    "treatment_rate"
                ],
                "absolute_lift": treatment_effect[
                    "absolute_lift"
                ],
                "relative_lift": treatment_effect[
                    "relative_lift"
                ],
                "z_statistic": z_test[
                    "z_statistic"
                ],
                "p_value": z_test[
                    "p_value"
                ],
                "ci_lower_bound": confidence_interval[
                    "lower_bound"
                ],
                "ci_upper_bound": confidence_interval[
                    "upper_bound"
                ],
                "srm_detected": srm_result[
                    "srm_detected"
                ],
                "srm_p_value": srm_result[
                    "p_value"
                ],
                "assignment_valid": assignment_validation[
                    "valid_assignment"
                ],
                "any_guardrail_failed": guardrail_result[
                    "any_guardrail_failed"
                ],
            }
        ]
    )

    experiment_summary.to_csv(
        output_directory / "experiment_summary.csv",
        index=False,
    )

    # Guardrail comparison table
    guardrail_df = pd.DataFrame(
        [
            {
                "metric": "ctr",
                "control_value": guardrail_metrics[
                    "control"
                ]["ctr"],
                "treatment_value": guardrail_metrics[
                    "treatment"
                ]["ctr"],
                "relative_change": guardrail_result[
                    "ctr_relative_change"
                ],
                "guardrail_failed": guardrail_result[
                    "ctr_guardrail_failed"
                ],
            },
            {
                "metric": "average_order_value",
                "control_value": guardrail_metrics[
                    "control"
                ]["average_order_value"],
                "treatment_value": guardrail_metrics[
                    "treatment"
                ]["average_order_value"],
                "relative_change": guardrail_result[
                    "aov_relative_change"
                ],
                "guardrail_failed": guardrail_result[
                    "aov_guardrail_failed"
                ],
            },
        ]
    )

    guardrail_df.to_csv(
        output_directory / "experiment_guardrails.csv",
        index=False,
    )


# ---------------------------------------------------------
# 13. Main pipeline
# ---------------------------------------------------------

def main():

    events_df = load_events()

    user_table = build_user_experiment_table(
        events_df
    )

    group_stats = calculate_group_statistics(
        user_table
    )

    treatment_effect = calculate_treatment_effect(
        group_stats
    )

    z_test = run_proportion_z_test(
        group_stats
    )

    confidence_interval = (
        calculate_lift_confidence_interval(
            group_stats
        )
    )

    srm_result = check_sample_ratio_mismatch(
        user_table
    )

    assignment_validation = (
        validate_experiment_assignment(
            events_df
        )
    )

    guardrail_metrics = calculate_guardrail_metrics(
        events_df
    )

    guardrail_result = evaluate_guardrails(
        guardrail_metrics
    )

    decision = make_experiment_decision(
        treatment_effect=treatment_effect,
        z_test=z_test,
        srm_result=srm_result,
        assignment_validation=assignment_validation,
        guardrail_result=guardrail_result,
    )

    save_experiment_outputs(
        group_stats=group_stats,
        treatment_effect=treatment_effect,
        z_test=z_test,
        confidence_interval=confidence_interval,
        srm_result=srm_result,
        assignment_validation=assignment_validation,
        guardrail_metrics=guardrail_metrics,
        guardrail_result=guardrail_result,
    )

    print("EXPERIMENT GROUP STATISTICS")
    print("-" * 50)
    print(group_stats.to_string(index=False))

    print()

    print("TREATMENT EFFECT")
    print("-" * 50)

    print(
        "Control conversion: "
        f"{treatment_effect['control_rate']:.2%}"
    )

    print(
        "Treatment conversion: "
        f"{treatment_effect['treatment_rate']:.2%}"
    )

    print(
        "Absolute lift: "
        f"{treatment_effect['absolute_lift']:.2%}"
    )

    print(
        "Relative lift: "
        f"{treatment_effect['relative_lift']:.2%}"
    )

    print()

    print("STATISTICAL TEST")
    print("-" * 50)

    print(
        f"Z-statistic: {z_test['z_statistic']:.4f}"
    )

    print(
        f"P-value: {z_test['p_value']:.4f}"
    )

    print()

    print("95% CONFIDENCE INTERVAL FOR ABSOLUTE LIFT")
    print("-" * 50)

    print(
        f"[{confidence_interval['lower_bound']:.2%}, "
        f"{confidence_interval['upper_bound']:.2%}]"
    )

    print()
    print()

    print("SAMPLE RATIO MISMATCH CHECK")
    print("-" * 50)

    print(
        "Control users: "
        f"{srm_result['control_users']}"
    )

    print(
        "Treatment users: "
        f"{srm_result['treatment_users']}"
    )

    print(
        "SRM chi-square statistic: "
        f"{srm_result['chi_square_statistic']:.4f}"
    )

    print(
        "SRM p-value: "
        f"{srm_result['p_value']:.4f}"
    )

    print(
        "SRM detected: "
        f"{srm_result['srm_detected']}"
    )

    print()

    print("EXPERIMENT ASSIGNMENT VALIDATION")
    print("-" * 50)

    print(
        "Users missing experiment group: "
        f"{assignment_validation['missing_group_users']}"
    )

    print(
        "Users appearing in multiple groups: "
        f"{assignment_validation['users_in_multiple_groups']}"
    )

    print(
        "Assignment valid: "
        f"{assignment_validation['valid_assignment']}"
    )

    print()

    print("GUARDRAIL METRICS")
    print("-" * 50)

    print(
        "Control CTR: "
        f"{guardrail_metrics['control']['ctr']:.2%}"
    )

    print(
        "Treatment CTR: "
        f"{guardrail_metrics['treatment']['ctr']:.2%}"
    )

    print(
        "CTR relative change: "
        f"{guardrail_result['ctr_relative_change']:.2%}"
    )

    print(
        "CTR guardrail failed: "
        f"{guardrail_result['ctr_guardrail_failed']}"
    )

    print()

    print(
        "Control AOV: "
        f"{guardrail_metrics['control']['average_order_value']:,.2f}"
    )

    print(
        "Treatment AOV: "
        f"{guardrail_metrics['treatment']['average_order_value']:,.2f}"
    )

    print(
        "AOV relative change: "
        f"{guardrail_result['aov_relative_change']:.2%}"
    )

    print(
        "AOV guardrail failed: "
        f"{guardrail_result['aov_guardrail_failed']}"
    )

    print()

    print(
        "Any guardrail failed: "
        f"{guardrail_result['any_guardrail_failed']}"
    )

    print()

    print("EXPERIMENT DECISION")
    print("-" * 50)
    print(decision)

    print()
    print(
        "Experiment outputs saved to data/processed/"
    )


if __name__ == "__main__":
    main()