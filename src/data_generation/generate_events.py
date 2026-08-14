from pathlib import Path
import hashlib

import numpy as np
import pandas as pd


# ---------------------------------------------------------
# 1. Reproducibility
# ---------------------------------------------------------

RANDOM_SEED = 42
rng = np.random.default_rng(RANDOM_SEED)


# ---------------------------------------------------------
# 2. Basic simulation configuration
# ---------------------------------------------------------

COUNTRIES = ["India", "UK", "Germany", "Australia"]

DEVICE_TYPES = ["mobile", "desktop", "tablet"]

PLATFORMS = ["android", "ios", "web"]

APP_VERSIONS = ["1.0", "1.1"]

SEARCH_QUERIES = [
    "running shoes",
    "sports shoes",
    "black tshirt",
    "sunscreen",
    "watch",
]

PRODUCT_IDS = [
    "P001",
    "P002",
    "P003",
    "P004",
    "P005",
    "P006",
]


# ---------------------------------------------------------
# 3. Deterministic experiment assignment
# ---------------------------------------------------------

def assign_experiment_group(user_id: str) -> str:
    """
    Assign the same user to the same experiment group every time.
    """

    hash_value = int(
        hashlib.md5(user_id.encode()).hexdigest(),
        16
    )

    return "treatment" if hash_value % 2 == 0 else "control"


# ---------------------------------------------------------
# 4. Generate synthetic users
# ---------------------------------------------------------

def generate_users(n_users: int = 1000) -> pd.DataFrame:

    users = []

    for i in range(1, n_users + 1):

        user_id = f"U{i:05d}"

        user = {
            "user_id": user_id,

            # Context
            "country": rng.choice(COUNTRIES),
            "device_type": rng.choice(DEVICE_TYPES),
            "platform": rng.choice(PLATFORMS),
            "app_version": rng.choice(APP_VERSIONS),

            # Continuous behavioral tendencies
            "budget_sensitivity": rng.uniform(0, 1),
            "quality_preference": rng.uniform(0, 1),
            "purchase_propensity": rng.uniform(0.05, 0.60),

            # Experiment information
            "experiment_id": "recommendation_v2_test",
            "experiment_group": assign_experiment_group(user_id),
        }

        users.append(user)

    return pd.DataFrame(users)


# ---------------------------------------------------------
# 5. Create one event row
# ---------------------------------------------------------

def create_event(
    event_id,
    event_name,
    user,
    session_id,
    timestamp,
    search_query=None,
    product_id=None,
    quantity=None,
    unit_price=None,
    order_id=None,
):

    return {
        "event_id": event_id,
        "event_name": event_name,
        "user_id": user["user_id"],
        "session_id": session_id,
        "event_timestamp": timestamp,

        "country": user["country"],
        "device_type": user["device_type"],
        "platform": user["platform"],
        "app_version": user["app_version"],

        "experiment_id": user["experiment_id"],
        "experiment_group": user["experiment_group"],

        "search_query": search_query,
        "product_id": product_id,
        "quantity": quantity,
        "unit_price": unit_price,
        "order_id": order_id,
    }


# ---------------------------------------------------------
# 6. Generate user-event journeys
# ---------------------------------------------------------

def generate_events(
    users_df: pd.DataFrame,
    start_date="2026-08-01",
    n_days=14,
) -> pd.DataFrame:

    events = []

    event_counter = 1
    session_counter = 1
    order_counter = 1

    start_date = pd.Timestamp(start_date)

    for _, user in users_df.iterrows():

        # Different users naturally have different numbers of sessions.
        number_of_sessions = max(
            1,
            rng.poisson(2)
        )

        for _ in range(number_of_sessions):

            session_id = f"S{session_counter:07d}"
            session_counter += 1

            random_day = rng.integers(0, n_days)
            random_minute = rng.integers(0, 24 * 60)

            timestamp = (
                start_date
                + pd.Timedelta(days=int(random_day))
                + pd.Timedelta(minutes=int(random_minute))
            )

            # -------------------------------------------------
            # APP OPEN
            # -------------------------------------------------

            events.append(
                create_event(
                    event_id=f"E{event_counter:08d}",
                    event_name="app_open",
                    user=user,
                    session_id=session_id,
                    timestamp=timestamp,
                )
            )

            event_counter += 1

            # Some sessions end immediately.
            if rng.random() < 0.10:
                continue

            # -------------------------------------------------
            # SEARCH
            # -------------------------------------------------

            search_query = rng.choice(SEARCH_QUERIES)

            timestamp += pd.Timedelta(
                seconds=int(rng.integers(5, 60))
            )

            events.append(
                create_event(
                    event_id=f"E{event_counter:08d}",
                    event_name="search",
                    user=user,
                    session_id=session_id,
                    timestamp=timestamp,
                    search_query=search_query,
                )
            )

            event_counter += 1

            # -------------------------------------------------
            # CLICK DECISION
            # -------------------------------------------------

            click_probability = 0.60

            # Treatment gives slightly better recommendations.
            if user["experiment_group"] == "treatment":
                click_probability += 0.05

            if rng.random() >= click_probability:
                continue

            product_id = rng.choice(PRODUCT_IDS)

            timestamp += pd.Timedelta(
                seconds=int(rng.integers(5, 120))
            )

            events.append(
                create_event(
                    event_id=f"E{event_counter:08d}",
                    event_name="click",
                    user=user,
                    session_id=session_id,
                    timestamp=timestamp,
                    search_query=search_query,
                    product_id=product_id,
                )
            )

            event_counter += 1

            # -------------------------------------------------
            # ADD TO CART DECISION
            # -------------------------------------------------

            cart_probability = (
                0.20
                + 0.25 * user["quality_preference"]
                + 0.10 * user["purchase_propensity"]
            )

            if rng.random() >= min(cart_probability, 0.90):
                continue

            unit_price = round(
                float(rng.uniform(500, 6000)),
                2
            )

            timestamp += pd.Timedelta(
                seconds=int(rng.integers(10, 180))
            )

            events.append(
                create_event(
                    event_id=f"E{event_counter:08d}",
                    event_name="add_to_cart",
                    user=user,
                    session_id=session_id,
                    timestamp=timestamp,
                    search_query=search_query,
                    product_id=product_id,
                    quantity=1,
                    unit_price=unit_price,
                )
            )

            event_counter += 1

            # -------------------------------------------------
            # PURCHASE DECISION
            # -------------------------------------------------

            purchase_probability = (
                user["purchase_propensity"]
                * (1 - 0.35 * user["budget_sensitivity"])
            )

            if user["experiment_group"] == "treatment":
                purchase_probability += 0.03

            if rng.random() >= np.clip(
                purchase_probability,
                0,
                0.95
            ):
                continue

            order_id = f"O{order_counter:07d}"
            order_counter += 1

            timestamp += pd.Timedelta(
                seconds=int(rng.integers(20, 300))
            )

            events.append(
                create_event(
                    event_id=f"E{event_counter:08d}",
                    event_name="purchase",
                    user=user,
                    session_id=session_id,
                    timestamp=timestamp,
                    search_query=search_query,
                    product_id=product_id,
                    quantity=1,
                    unit_price=unit_price,
                    order_id=order_id,
                )
            )

            event_counter += 1

    events_df = pd.DataFrame(events)

    return events_df


# ---------------------------------------------------------
# 7. Main pipeline
# ---------------------------------------------------------

def main():

    users_df = generate_users(
        n_users=1000
    )

    events_df = generate_events(
        users_df=users_df
    )

    project_root = Path(__file__).resolve().parents[2]

    output_directory = project_root / "data" / "raw"

    output_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    users_path = output_directory / "users.csv"
    events_path = output_directory / "events.csv"

    users_df.to_csv(
        users_path,
        index=False
    )

    events_df.to_csv(
        events_path,
        index=False
    )

    print("Data generation complete.")
    print(f"Users generated: {len(users_df):,}")
    print(f"Events generated: {len(events_df):,}")
    print()
    print("Event distribution:")
    print(events_df["event_name"].value_counts())
    print()
    print(f"Users saved to: {users_path}")
    print(f"Events saved to: {events_path}")


if __name__ == "__main__":
    main()