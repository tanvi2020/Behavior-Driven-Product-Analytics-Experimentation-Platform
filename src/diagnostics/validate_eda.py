from pathlib import Path


EXPECTED_FIGURES = {
    "daily_event_volume.png",
    "product_funnel.png",
    "experiment_conversion_comparison.png",
    "conversion_by_country.png",
    "conversion_by_platform.png",
    "ctr_by_device.png",
    "guardrail_ctr.png",
    "guardrail_average_order_value.png",
    "daily_conversion_rate.png",
}


def get_figures_directory() -> Path:
    project_root = Path(__file__).resolve().parents[2]

    return (
        project_root
        / "outputs"
        / "figures"
    )


def validate_expected_figures() -> None:
    figures_directory = get_figures_directory()

    assert figures_directory.exists(), (
        "Figures directory does not exist."
    )

    actual_figures = {
        file.name
        for file in figures_directory.iterdir()
        if file.is_file()
    }

    missing_figures = (
        EXPECTED_FIGURES
        - actual_figures
    )

    assert not missing_figures, (
        f"Missing expected figures: {missing_figures}"
    )


def validate_non_empty_figures() -> None:
    figures_directory = get_figures_directory()

    for figure_name in EXPECTED_FIGURES:

        figure_path = (
            figures_directory
            / figure_name
        )

        assert figure_path.stat().st_size > 0, (
            f"{figure_name} is empty."
        )


def main():

    checks = [
        (
            "Expected figures",
            validate_expected_figures,
        ),
        (
            "Non-empty figure files",
            validate_non_empty_figures,
        ),
    ]

    for check_name, check_function in checks:
        check_function()
        print(f"PASS: {check_name}")

    print()
    print("All EDA validations passed.")


if __name__ == "__main__":
    main()