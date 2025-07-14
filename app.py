import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_folium import folium_static
import folium

# Load Data
df = pd.read_csv("retail_data.csv")

# Set Page Configuration
st.set_page_config(page_title="RetailRadar", layout="wide")
st.title("🛍️ RetailRadar - Smart Inventory & Delivery Dashboard")
st.markdown("#### Helping retailers forecast demand, prevent stockouts, and optimize last-mile delivery 🚚")

# KPI Metrics
total_products = df.shape[0]
low_stock_count = df[df["Current_Stock"] < 10].shape[0]
total_units = df["Current_Stock"].sum()

col1, col2, col3 = st.columns(3)
col1.metric("Total Products", total_products)
col2.metric("Low Stock Items", low_stock_count)
col3.metric("Total Units in Stock", total_units)

# 🔍 Product Checker
st.subheader("🔎 Check Product Status")
product_list = df["Product"].tolist()
selected_product = st.selectbox("Select a product to view details", product_list)

product_data = df[df["Product"] == selected_product].iloc[0]
st.info(f"🛒 **{selected_product}** - Category: {product_data['Category']}")
st.success(f"📦 Current Stock: {product_data['Current_Stock']} units")
st.warning(f"📉 7-Day Demand: {product_data['Avg_Daily_Sales']*7} units")
st.error(f"📊 Predicted Stock Left: {max(product_data['Current_Stock'] - product_data['Avg_Daily_Sales']*7, 0)} units")

# 📝 Feedback
st.subheader("💬 Feedback")
feedback = st.text_area("Is any product missing? Or facing delivery issues?")
if st.button("Submit Feedback"):
    st.success("✅ Thanks! We'll look into it.")

# 🚚 Delivery Request
st.subheader("📦 Place Delivery Request")
with st.form("delivery_form"):
    name = st.text_input("Your Name")
    address = st.text_area("Delivery Address")
    request_product = st.selectbox("Product", df["Product"].tolist())
    quantity = st.number_input("Quantity", min_value=1, step=1)
    submit = st.form_submit_button("Place Order")
    if submit:
        st.success(f"🎉 Delivery request placed for {quantity} units of {request_product}!")

# Forecast Calculations
df["Expected_7_Day_Demand"] = df["Avg_Daily_Sales"] * 7
df["Predicted_Stock_Left"] = df["Current_Stock"] - df["Expected_7_Day_Demand"]
df["Predicted_Stock_Left"] = df["Predicted_Stock_Left"].apply(lambda x: max(x, 0))

# 📊 Bar Chart
fig = px.bar(
    df.sort_values("Predicted_Stock_Left"),
    x="Product",
    y="Predicted_Stock_Left",
    color="Category",
    title="Predicted Stock Left After 7 Days",
    labels={"Predicted_Stock_Left": "Stock Left (After 7 Days)"}
)
st.plotly_chart(fig, use_container_width=True)

# ⚠️ Stock Alerts
low_stock = df[df["Predicted_Stock_Left"] < 5]
if not low_stock.empty:
    st.subheader("⚠️ Products At Risk of Stockout:")
    for index, row in low_stock.iterrows():
        st.warning(f"{row['Product']} may run out soon. Only {int(row['Predicted_Stock_Left'])} units will be left after 7 days.")
else:
    st.success("✅ All products are expected to stay in stock.")

# 🗺️ Interactive Map
st.subheader("🗺️ Interactive Delivery Route Map")
st.markdown("Zoom, drag, and click markers to explore warehouse and customer zones.")

m = folium.Map(location=[17.385044, 78.486671], zoom_start=12)
folium.Marker([17.385044, 78.486671], popup="🏢 Warehouse", icon=folium.Icon(color="blue")).add_to(m)
delivery_points = [
    ("Customer A", 17.4000, 78.4800),
    ("Customer B", 17.3950, 78.5000),
    ("Customer C", 17.3900, 78.4700)
]
for name, lat, lon in delivery_points:
    folium.Marker([lat, lon], popup=name, icon=folium.Icon(color="green", icon="truck", prefix="fa")).add_to(m)
    folium.PolyLine([(17.385044, 78.486671), (lat, lon)], color="orange").add_to(m)
folium_static(m)
