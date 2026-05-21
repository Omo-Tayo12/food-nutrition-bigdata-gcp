"""
03_pubsub_streaming.py
======================
Simulates a real-time streaming ingestion pipeline using Google Cloud Pub/Sub.
Publishes food product update events (e.g., from an IoT nutritional scanner or
POS system) to a Pub/Sub topic for downstream Dataflow processing.

Usage:
    # Terminal 1 — Start the publisher (simulates IoT/POS data feed)
    python ingestion/03_pubsub_streaming.py --mode publish

    # Terminal 2 — Start the subscriber (consumes messages)
    python ingestion/03_pubsub_streaming.py --mode subscribe

Requirements:
    - pip install google-cloud-pubsub
    - Pub/Sub API enabled in your GCP project
"""

import argparse
import json
import time
import random
import datetime
from google.cloud import pubsub_v1

# ─── Configuration ────────────────────────────────────────────────────────────
PROJECT_ID     = "your-gcp-project-id"
TOPIC_ID       = "food-nutrition-updates"
SUBSCRIPTION_ID = "food-nutrition-updates-sub"

# Sample food categories for simulation
FOOD_CATEGORIES = [
    "Dairy and Egg Products", "Spices and Herbs", "Baby Foods",
    "Fats and Oils", "Poultry Products", "Soups, Sauces and Gravies",
    "Sausages and Luncheon Meats", "Breakfast Cereals", "Fruits and Fruit Juices",
    "Pork Products", "Vegetables and Vegetable Products", "Nut and Seed Products",
    "Beef Products", "Beverages", "Finfish and Shellfish Products",
    "Legumes and Legume Products", "Lamb, Veal and Game Products",
    "Baked Products", "Snacks", "Sweets", "Cereal Grains and Pasta",
]

FOOD_SAMPLE_NAMES = [
    "Whole Milk", "Greek Yoghurt", "Cheddar Cheese", "Boiled Egg",
    "Grilled Chicken Breast", "Salmon Fillet", "Brown Rice", "Quinoa",
    "Broccoli", "Spinach", "Sweet Potato", "Avocado",
    "Almonds", "Walnuts", "Black Beans", "Lentils",
    "Oatmeal", "Whole Wheat Bread", "Banana", "Apple",
]


def generate_nutrition_event() -> dict:
    """Generate a simulated nutritional product update event."""
    return {
        "event_id": f"evt_{random.randint(100000, 999999)}",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "food_name": random.choice(FOOD_SAMPLE_NAMES),
        "food_category": random.choice(FOOD_CATEGORIES),
        "barcode": f"{random.randint(1000000000000, 9999999999999)}",
        "source": random.choice(["IoT_Scanner", "POS_System", "API_Feed", "Manual_Entry"]),
        "nutrients": {
            "calories_per_100g": round(random.uniform(10, 900), 1),
            "protein_g":         round(random.uniform(0, 40), 2),
            "fat_g":             round(random.uniform(0, 50), 2),
            "saturated_fat_g":   round(random.uniform(0, 25), 2),
            "carbohydrates_g":   round(random.uniform(0, 80), 2),
            "fibre_g":           round(random.uniform(0, 15), 2),
            "sugars_g":          round(random.uniform(0, 60), 2),
            "sodium_mg":         round(random.uniform(0, 2000), 1),
            "vitamin_c_mg":      round(random.uniform(0, 100), 2),
            "calcium_mg":        round(random.uniform(0, 500), 1),
            "iron_mg":           round(random.uniform(0, 20), 2),
        },
        "serving_size_g": random.choice([28, 30, 50, 100, 150, 200]),
        "country_of_origin": random.choice(["GB", "US", "DE", "FR", "IT", "NG", "IN"]),
    }


# ─── Publisher ────────────────────────────────────────────────────────────────
def publish_messages(num_messages: int = 50, interval_seconds: float = 0.5):
    """Publish simulated nutrition events to Pub/Sub topic."""
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

    # Create topic if it does not exist
    try:
        publisher.create_topic(request={"name": topic_path})
        print(f"  Topic created: {topic_path}")
    except Exception:
        print(f"  Topic already exists: {topic_path}")

    print(f"\n  Publishing {num_messages} nutrition update events...")
    print(f"  Topic: {topic_path}\n")

    futures = []
    for i in range(1, num_messages + 1):
        event = generate_nutrition_event()
        message_bytes = json.dumps(event).encode("utf-8")

        # Publish with ordering key (by food category)
        future = publisher.publish(
            topic_path,
            data=message_bytes,
            ordering_key=event["food_category"],
            source=event["source"],
        )
        futures.append((i, future, event["food_name"]))

        print(f"  [{i:03d}/{num_messages}] Publishing: {event['food_name']} "
              f"({event['food_category']}) — {event['nutrients']['calories_per_100g']} kcal")
        time.sleep(interval_seconds)

    # Confirm all published
    success, failed = 0, 0
    for i, future, name in futures:
        try:
            msg_id = future.result(timeout=10)
            success += 1
        except Exception as e:
            print(f"  ERROR publishing message {i} ({name}): {e}")
            failed += 1

    print(f"\n  Published {success} messages successfully, {failed} failed.")


# ─── Subscriber ───────────────────────────────────────────────────────────────
def subscribe_messages(timeout: float = 60.0):
    """Subscribe to and process nutrition update messages from Pub/Sub."""
    subscriber = pubsub_v1.SubscriberClient()
    topic_path = f"projects/{PROJECT_ID}/topics/{TOPIC_ID}"
    subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)

    # Create subscription if needed
    try:
        subscriber.create_subscription(
            request={"name": subscription_path, "topic": topic_path}
        )
        print(f"  Subscription created: {subscription_path}")
    except Exception:
        print(f"  Subscription exists: {subscription_path}")

    received_count = [0]

    def callback(message: pubsub_v1.subscriber.message.Message) -> None:
        """Process each received Pub/Sub message."""
        try:
            event = json.loads(message.data.decode("utf-8"))
            received_count[0] += 1
            print(
                f"  [MSG {received_count[0]:03d}] Received: {event['food_name']} | "
                f"Category: {event['food_category']} | "
                f"Calories: {event['nutrients']['calories_per_100g']} kcal/100g | "
                f"Source: {event['source']}"
            )
            # In production: write to Bigtable, trigger Dataflow job, etc.
            message.ack()
        except Exception as e:
            print(f"  Error processing message: {e}")
            message.nack()

    print(f"\n  Listening for messages on {subscription_path} (timeout: {timeout}s)...")
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)

    try:
        streaming_pull_future.result(timeout=timeout)
    except Exception:
        streaming_pull_future.cancel()
        print(f"\n  Subscription ended. Received {received_count[0]} messages total.")


# ─── Main ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Food Nutrition Pub/Sub Streaming")
    parser.add_argument(
        "--mode",
        choices=["publish", "subscribe"],
        default="publish",
        help="Run as publisher or subscriber",
    )
    parser.add_argument("--messages", type=int, default=50, help="Number of messages to publish")
    parser.add_argument("--interval", type=float, default=0.5, help="Seconds between publishes")
    parser.add_argument("--timeout", type=float, default=60.0, help="Subscriber timeout (seconds)")
    args = parser.parse_args()

    print("=" * 60)
    print(f"  Pub/Sub Streaming — Mode: {args.mode.upper()}")
    print("=" * 60)

    if args.mode == "publish":
        publish_messages(num_messages=args.messages, interval_seconds=args.interval)
    else:
        subscribe_messages(timeout=args.timeout)
