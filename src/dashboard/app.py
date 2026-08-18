from pathlib import Path

import pandas as pd
import streamlit as st


# ---------------------------------------------------------
# 1. Page configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="Product Analytics & Experimentation Dashboard",
    page_icon="📊",
    layout="wide",
)


# ---------------------------------------------------------
# 2. Paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"


# ---------------------------------------------------------
# 3. Load processed data
# ---------------------------------------------------------

@st.cache_data
def load_data():

    core_metrics = pd.read_csv(
        PROCESSED_DIR / "core_metrics.csv"
    )

    funnel_metrics = pd.read_csv(
        PROCESSED_DIR / "funnel_metrics.csv"
    )

    experiment_summary = pd.read_csv(
        PROCESSED_DIR / "experiment_summary.csv"
    )

    experiment_groups = pd.read_csv(
        PROCESSED_DIR / "experiment_group_statistics.csv"
    )

    guardrails = pd.read_csv(
        PROCESSED_DIR / "experiment_guardrails.csv"
    )

    country_metrics = pd.read_csv(
        PROCESSED_DIR / "country_metrics.csv"
    )

    platform_metrics = pd.read_csv(
        PROCESSED_DIR / "platform_metrics.csv"
    )

    device_metrics = pd.read_csv(
        PROCESSED_DIR / "device_type_metrics.csv"
    )

    product_insights = pd.read_csv(
        PROCESSED_DIR / "product_insights.csv"
    )

    return {
        "core": core_metrics,
        "funnel": funnel_metrics,
        "experiment_summary": experiment_summary,
        "experiment_groups": experiment_groups,
        "guardrails": guardrails,
        "country": country_metrics,
        "platform": platform_metrics,
        "device": device_metrics,
        "insights": product_insights,
    }


data = load_data()


# ---------------------------------------------------------
# 4. Helper functions
# ---------------------------------------------------------

def format_percentage(value):
    return f"{value:.2%}"


def format_number(value):
    return f"{value:,.0f}"


def format_currency(value):
    return f"₹{value:,.2f}"


# ---------------------------------------------------------
# 5. Header
# ---------------------------------------------------------

st.title("📊 Product Analytics & Experimentation Platform")

st.caption(
    "Behavior-driven product analytics, experimentation, "
    "diagnostics, and decision support."
)

st.divider()


# ---------------------------------------------------------
# 6. Product overview
# ---------------------------------------------------------

st.header("1. Product Overview")

core = data["core"].iloc[0]

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Users",
    format_number(core["total_users"]),
)

col2.metric(
    "Sessions",
    format_number(core["total_sessions"]),
)

col3.metric(
    "Searches",
    format_number(core["total_searches"]),
)

col4.metric(
    "Purchases",
    format_number(core["total_purchases"]),
)

col5, col6, col7, col8 = st.columns(4)

col5.metric(
    "Clicks",
    format_number(core["total_clicks"]),
)

col6.metric(
    "Add to Carts",
    format_number(core["total_add_to_carts"]),
)

overall_ctr = (
    core["total_clicks"] / core["total_searches"]
    if core["total_searches"] > 0
    else 0.0
)

overall_purchase_rate = (
    core["total_purchases"] / core["total_users"]
    if core["total_users"] > 0
    else 0.0
)

col7.metric(
    "Search → Click CTR",
    format_percentage(overall_ctr),
)

col8.metric(
    "Purchases per User",
    format_percentage(overall_purchase_rate),
)


# ---------------------------------------------------------
# 7. Funnel
# ---------------------------------------------------------

st.divider()
st.header("2. Product Funnel")

funnel_df = data["funnel"].copy()

display_funnel = funnel_df[
    [
        "funnel_step",
        "sessions",
        "rate_from_start",
        "step_conversion_rate",
        "drop_off_rate",
    ]
].copy()

display_funnel["rate_from_start"] = (
    display_funnel["rate_from_start"]
    .map(format_percentage)
)

display_funnel["step_conversion_rate"] = (
    display_funnel["step_conversion_rate"]
    .map(format_percentage)
)

display_funnel["drop_off_rate"] = (
    display_funnel["drop_off_rate"]
    .map(format_percentage)
)

st.dataframe(
    display_funnel,
    use_container_width=True,
    hide_index=True,
)

funnel_figure = FIGURES_DIR / "product_funnel.png"

if funnel_figure.exists():
    st.image(
        str(funnel_figure),
        caption="Session-level product funnel",
        use_container_width=True,
    )


# ---------------------------------------------------------
# 8. Experiment results
# ---------------------------------------------------------

st.divider()
st.header("3. Experiment Results")

summary = data["experiment_summary"].iloc[0]

control_conversion = summary[
    "control_conversion_rate"
]

treatment_conversion = summary[
    "treatment_conversion_rate"
]

absolute_lift = summary[
    "absolute_lift"
]

relative_lift = summary[
    "relative_lift"
]

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Control Conversion",
    format_percentage(control_conversion),
)

col2.metric(
    "Treatment Conversion",
    format_percentage(treatment_conversion),
)

col3.metric(
    "Absolute Lift",
    format_percentage(absolute_lift),
)

col4.metric(
    "Relative Lift",
    format_percentage(relative_lift),
)

st.subheader("Statistical Evidence")

col1, col2, col3 = st.columns(3)

col1.metric(
    "P-value",
    f"{summary['p_value']:.4f}",
)

col2.metric(
    "95% CI Lower",
    format_percentage(summary["ci_lower_bound"]),
)

col3.metric(
    "95% CI Upper",
    format_percentage(summary["ci_upper_bound"]),
)

experiment_figure = (
    FIGURES_DIR
    / "experiment_conversion_comparison.png"
)

if experiment_figure.exists():
    st.image(
        str(experiment_figure),
        caption="Control vs treatment conversion",
        use_container_width=True,
    )


# ---------------------------------------------------------
# 9. Experiment health
# ---------------------------------------------------------

st.divider()
st.header("4. Experiment Health")

col1, col2, col3 = st.columns(3)

srm_detected = bool(summary["srm_detected"])
assignment_valid = bool(summary["assignment_valid"])
guardrail_failed = bool(summary["any_guardrail_failed"])

col1.metric(
    "SRM Detected",
    "Yes" if srm_detected else "No",
)

col2.metric(
    "Assignment Valid",
    "Yes" if assignment_valid else "No",
)

col3.metric(
    "Guardrail Failure",
    "Yes" if guardrail_failed else "No",
)

st.caption(
    f"SRM p-value: {summary['srm_p_value']:.4f}"
)


# ---------------------------------------------------------
# 10. Guardrails
# ---------------------------------------------------------

st.subheader("Guardrail Comparison")

guardrail_df = data["guardrails"].copy()

guardrail_display = guardrail_df.copy()

guardrail_display["relative_change"] = (
    guardrail_display["relative_change"]
    .map(format_percentage)
)

st.dataframe(
    guardrail_display,
    use_container_width=True,
    hide_index=True,
)

guardrail_ctr_figure = (
    FIGURES_DIR / "guardrail_ctr.png"
)

guardrail_aov_figure = (
    FIGURES_DIR
    / "guardrail_average_order_value.png"
)

col1, col2 = st.columns(2)

with col1:
    if guardrail_ctr_figure.exists():
        st.image(
            str(guardrail_ctr_figure),
            caption="CTR guardrail",
            use_container_width=True,
        )

with col2:
    if guardrail_aov_figure.exists():
        st.image(
            str(guardrail_aov_figure),
            caption="AOV guardrail",
            use_container_width=True,
        )


# ---------------------------------------------------------
# 11. Segment diagnostics
# ---------------------------------------------------------

st.divider()
st.header("5. Segment Diagnostics")

segment_type = st.selectbox(
    "Select a segment",
    [
        "Country",
        "Platform",
        "Device Type",
    ],
)

if segment_type == "Country":
    segment_df = data["country"]
    segment_column = "country"

elif segment_type == "Platform":
    segment_df = data["platform"]
    segment_column = "platform"

else:
    segment_df = data["device"]
    segment_column = "device_type"


segment_display = segment_df[
    [
        segment_column,
        "users",
        "sessions",
        "ctr",
        "user_conversion_rate",
        "revenue",
        "orders",
        "average_order_value",
    ]
].copy()

segment_display["ctr"] = (
    segment_display["ctr"]
    .map(format_percentage)
)

segment_display["user_conversion_rate"] = (
    segment_display["user_conversion_rate"]
    .map(format_percentage)
)

segment_display["revenue"] = (
    segment_display["revenue"]
    .map(format_currency)
)

segment_display["average_order_value"] = (
    segment_display["average_order_value"]
    .map(format_currency)
)

st.dataframe(
    segment_display,
    use_container_width=True,
    hide_index=True,
)


# ---------------------------------------------------------
# 12. Diagnostics visuals
# ---------------------------------------------------------

st.divider()
st.header("6. Product Diagnostics")

diagnostic_figures = [
    (
        "Daily Event Volume",
        "daily_event_volume.png",
    ),
    (
        "Daily Conversion Rate",
        "daily_conversion_rate.png",
    ),
    (
        "Conversion by Country",
        "conversion_by_country.png",
    ),
    (
        "Conversion by Platform",
        "conversion_by_platform.png",
    ),
    (
        "CTR by Device",
        "ctr_by_device.png",
    ),
]

for title, filename in diagnostic_figures:

    figure_path = FIGURES_DIR / filename

    if figure_path.exists():

        st.subheader(title)

        st.image(
            str(figure_path),
            use_container_width=True,
        )


# ---------------------------------------------------------
# 13. Behavior-driven insights
# ---------------------------------------------------------

st.divider()
st.header("7. Behavior-Driven Insights")

st.caption(
    "Prioritized analytical signals and recommended "
    "investigation paths. These are not causal conclusions."
)

insights_df = data["insights"].copy()

insights_df = insights_df.sort_values(
    "rank"
)

for _, insight_row in insights_df.iterrows():

    rank = int(
        insight_row["rank"]
    )

    priority = insight_row[
        "priority"
    ]

    finding = insight_row[
        "insight"
    ]

    recommendation = insight_row[
        "recommended_investigation"
    ]

    if priority == "HIGH":

        st.error(
            f"Rank {rank} | HIGH PRIORITY"
        )

    elif priority == "MEDIUM":

        st.warning(
            f"Rank {rank} | MEDIUM PRIORITY"
        )

    else:

        st.info(
            f"Rank {rank} | LOW PRIORITY"
        )

    st.markdown(
        f"**Finding:** {finding}"
    )

    st.markdown(
        f"**Recommended investigation:** {recommendation}"
    )

    st.divider()


# ---------------------------------------------------------
# 14. Final decision layer
# ---------------------------------------------------------

st.header("8. Experiment Decision")

statistically_significant = (
    summary["p_value"] < 0.05
)

positive_lift = (
    summary["absolute_lift"] > 0
)

if srm_detected:

    st.error(
        "Do not trust the experiment result. "
        "Sample Ratio Mismatch was detected."
    )

elif not assignment_valid:

    st.error(
        "Do not trust the experiment result. "
        "Experiment assignment is invalid."
    )

elif guardrail_failed:

    st.warning(
        "The primary metric improved, but at least "
        "one guardrail failed. Investigate before rollout."
    )

elif statistically_significant and positive_lift:

    st.success(
        "Treatment shows a statistically significant "
        "positive lift with no V1 experiment-health "
        "or guardrail failure."
    )

elif statistically_significant and not positive_lift:

    st.error(
        "Treatment shows a statistically significant "
        "negative effect."
    )

else:

    st.info(
        "No statistically significant difference "
        "was detected."
    )


# ---------------------------------------------------------
# 15. Footer
# ---------------------------------------------------------

st.divider()

st.caption(
    "V1 Product Analytics & Experimentation Platform"
)