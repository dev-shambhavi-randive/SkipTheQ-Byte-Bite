import os
import random
from datetime import datetime
import pandas as pd
import streamlit as st

DATA_FILE = "canteen_data.csv"


def load_data():
  """Loads canteen data from CSV."""
  if not os.path.exists(DATA_FILE):
    return pd.DataFrame(columns=["timestamp", "crowd_level", "menu_available"])
  try:
    df = pd.read_csv(DATA_FILE)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df
  except Exception as e:
    st.error(f"Error loading data: {e}")
    return pd.DataFrame(columns=["timestamp", "crowd_level", "menu_available"])


def save_report(crowd_level, menu_available):
  """Appends a new report to the CSV file."""
  now = datetime.now()
  new_data = pd.DataFrame(
      [{"timestamp": now, "crowd_level": crowd_level, "menu_available": menu_available}]
  )

  file_exists = os.path.isfile(DATA_FILE)
  new_data.to_csv(DATA_FILE, mode="a", index=False, header=not file_exists)
  return True


# --- UI Setup ---
st.set_page_config(
    page_title="Campus Canteen App", page_icon="🍔", layout="centered"
)
st.title("🍔 Smart Canteen & Ordering Hub")

tab1, tab2, tab3 = st.tabs(
    ["📊 Dashboard & Tracking", "🛒 Order Food", "👤 My Profile & Alerts"]
)

# --- TAB 1: Dashboard ---
with tab1:
  df = load_data()
  st.header("Live Canteen Status")

  if df.empty:
    st.info("No data available yet. Be the first to report!")
  else:
    latest_report = df.iloc[-1]
    last_time = latest_report["timestamp"]
    time_diff = datetime.now() - last_time
    minutes_ago = int(time_diff.total_seconds() / 60)

    if minutes_ago < 15:
      freshness = "🟢 High Confidence (Very Recent)"
    elif minutes_ago < 60:
      freshness = "🟡 Medium Confidence (Slightly Stale)"
    else:
      freshness = "🔴 Low Confidence (Old Data)"

    col1, col2, col3 = st.columns(3)
    col1.metric("Current Crowd", latest_report["crowd_level"])
    col2.metric("Snacks Available?", latest_report["menu_available"])
    col3.metric("Last Updated", f"{minutes_ago} mins ago")
    st.caption(f"Data Reliability: {freshness}")

  st.markdown("---")

  # Peak Hours Chart
  st.subheader("📈 Peak Hours Analysis")
  if not df.empty and len(df) > 2:
    df["hour"] = df["timestamp"].dt.hour
    crowd_mapping = {"Low": 1, "Medium": 2, "High": 3}
    df["crowd_score"] = df["crowd_level"].map(crowd_mapping).fillna(1)
    peak_data = df.groupby("hour")["crowd_score"].mean()
    st.bar_chart(peak_data)
    st.caption("1 = Low, 2 = Medium, 3 = High")
  else:
    st.info("Not enough data to show peak hours yet. Send in more reports!")

  # Events & Discounts
  st.markdown("---")
  st.subheader("🎉 Upcoming Events & Discounts")
  st.info("🔥 **Diwali Special:** Get 20% off on all Thalis next week!")
  st.success(
      "🎸 **College Fest Alert:** Extended canteen hours till 10 PM this"
      " Friday."
  )

  st.markdown("---")
  st.subheader("📝 Live Reporting")

  crowd_level = st.selectbox(
      "How crowded is it right now?",
      [
          "Low (Empty tables available)",
          "Medium (Getting full)",
          "High (No seats, long lines)",
      ],
  )
  save_crowd = crowd_level.split(" ")[0]
  menu_available = st.radio(
      "Are popular snacks available?", ["Yes", "No", "Not Sure"]
  )

  if st.button("Save Report"):
    if save_report(save_crowd, menu_available):
      st.success("✅ Thanks for reporting! The data has been updated.")
      st.rerun()

# --- TAB 2: Food Ordering ---
with tab2:
  st.header("🛒 Order Your Food")
  st.markdown("Skip the line! Order and pay online.")

  if "cart" not in st.session_state:
    st.session_state.cart = []

  menu = {
      "Samosa": 15,
      "Vada Pav": 20,
      "Masala Dosa": 50,
      "Veg Thali": 80,
      "Cold Coffee": 40,
  }

  for item, price in menu.items():
    col1, col2 = st.columns([3, 1])
    col1.write(f"**{item}** - ₹{price}")
    if col2.button(f"Add {item}"):
      st.session_state.cart.append({"item": item, "price": price})
      st.toast(f"Added {item} to cart!")

  st.markdown("---")
  st.subheader("🛍️ Your Cart")
  if not st.session_state.cart:
    st.write("Cart is empty.")
  else:
    total = 0
    for order_item in st.session_state.cart:
      st.write(f"- {order_item['item']}: ₹{order_item['price']}")
      total += order_item["price"]

    st.write(f"**Total Amount: ₹{total}**")

    if st.button("Proceed to Pay"):
      order_no = random.randint(1000, 9999)
      st.success(f"✅ Payment Successful! Your Order No. is **#{order_no}**.")
      st.info("Show this number at the counter to pick up your food.")
      st.session_state.cart = []

# --- TAB 3: Profile & Alerts ---
with tab3:
  st.header("👤 Personalization & Alerts")

  username = st.text_input("Enter your name to load profile:", "Student")

  if username:
    visit_time = (
        "1:00 PM - 2:00 PM"
        if len(username) % 2 == 0
        else "10:30 AM - 11:00 AM"
    )
    st.write(f"👋 Welcome back, **{username}**!")
    st.write(f"🕒 **Your usual visit time:** {visit_time}")

    if not df.empty:
      st.write(
          "Based on your usual time, the canteen is typically **Medium**"
          " crowded. Consider ordering ahead!"
      )

    st.markdown("---")
    st.subheader("📍 Location Alerts")
    st.write(
        "Enable background location to get alerts when you are near the"
        " canteen."
    )

    if st.button("Simulate walking near canteen"):
      st.toast(
          f"Hey {username}! You are near the canteen. Grab a quick snack!",
          icon="🔔",
      )