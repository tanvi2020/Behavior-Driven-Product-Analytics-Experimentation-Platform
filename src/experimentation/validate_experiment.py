from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from experimentation.experiment_analysis import (
    load_events,
    build_user_experiment_table,
    calculate_group_statistics,
    calculate_treatment_effect,
    run_proportion_z_test,
    calculate_lift_confidence_interval,
    check_sample_ratio_mismatch,
    validate_experiment_assignment,
    calculate_guardrail_metrics,
    evaluate_guardrails,
)


def validate_group_statistics(group_stats: pd.DataFrame) -> None:
    expected_groups = {"control", "treatment"}
    actual_groups = set(group_stats["experiment_group"])

    assert actual_groups == expected_groups, (
        f"Unexpected experiment groups: {actual_groups}"
    )

    assert (group_stats["users"] > 0).all(), (
        "One or more groups contain zero users."
    )

    assert group_stats["conversion_rate"].between(0, 1).all(), (
        "Conversion rate outside [0, 1]."
    )


def validate_treatment_effect(
    treatment_effect: dict,
) -> None:
    assert 0 <= treatment_effect["control_rate"] <= 1
    assert 0 <= treatment_effect["treatment_rate"] <= 1

    expected_absolute_lift = (
        treatment_effect["treatment_rate"]
        - treatment_effect["control_rate"]
    )

    assert abs(
        treatment_effect["absolute_lift"]
        - expected_absolute_lift
    ) < 1e-12, (
        "Absolute lift calculation is inconsistent."
    )


def validate_statistical_test(
    z_test: dict,
) -> None:
    assert 0 <= z_test["p_value"] <= 1, (
        "P-value outside [0, 1]."
    )


def validate_confidence_interval(
    confidence_interval: dict,
) -> None:
    assert (
        confidence_interval["lower_bound"]
        <= confidence_interval["upper_bound"]
    ), (
        "Confidence interval bounds are reversed."
    )


def validate_srm(
    srm_result: dict,
) -> None:
    assert 0 <= srm_result["p_value"] <= 1

    total_users = (
        srm_result["control_users"]
        + srm_result["treatment_users"]
    )

    assert total_users > 0, (
        "Experiment has no users."
    )


def validate_assignment(
    assignment_validation: dict,
) -> None:
    assert (
        assignment_validation["missing_group_users"] >= 0
    )

    assert (
        assignment_validation["users_in_multiple_groups"] >= 0
    )


def validate_guardrails(
    guardrail_metrics: dict,
    guardrail_result: dict,
) -> None:
    for group_name in ["control", "treatment"]:

        assert (
            0
            <= guardrail_metrics[group_name]["ctr"]
            <= 1
        ), (
            f"{group_name} CTR outside [0, 1]."
        )

        assert (
            guardrail_metrics[group_name][
                "average_order_value"
            ]
            >= 0
        ), (
            f"{group_name} AOV is negative."
        )

    assert isinstance(
        guardrail_result["any_guardrail_failed"],
        (bool, type(pd.NA)),
    ) or str(
        guardrail_result["any_guardrail_failed"]
    ) in {"True", "False"}


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

    checks = [
        (
            "Group statistics",
            lambda: validate_group_statistics(
                group_stats
            ),
        ),
        (
            "Treatment effect",
            lambda: validate_treatment_effect(
                treatment_effect
            ),
        ),
        (
            "Statistical test",
            lambda: validate_statistical_test(
                z_test
            ),
        ),
        (
            "Confidence interval",
            lambda: validate_confidence_interval(
                confidence_interval
            ),
        ),
        (
            "Sample ratio mismatch",
            lambda: validate_srm(
                srm_result
            ),
        ),
        (
            "Experiment assignment",
            lambda: validate_assignment(
                assignment_validation
            ),
        ),
        (
            "Guardrail metrics",
            lambda: validate_guardrails(
                guardrail_metrics,
                guardrail_result,
            ),
        ),
    ]

    for check_name, check_function in checks:
        check_function()
        print(f"PASS: {check_name}")

    print()
    print("All experiment validations passed.")


if __name__ == "__main__":
    main()