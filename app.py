import streamlit as st
import pandas as pd

from services.customer_service import get_customers
from services.product_service import get_products
from services.order_service import get_orders

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="OperaFlow",
    layout="wide"
)

# =========================
# HEADER
# =========================
st.title("OperaFlow")
st.subheader("Retail Business Operating System")

st.divider()

# =========================
# LOAD DATA
# =========================
customers = get_customers()
products = get_products()
orders = get_orders()

customer_df = pd.DataFrame(customers)
product_df = pd.DataFrame(products)
order_df = pd.DataFrame(orders)

# =========================
# KPI SECTION
# =========================
total_customers = len(customer_df)
total_products = len(product_df)
total_orders = len(order_df)
total_stock = product_df["stock"].sum()
total_revenue = order_df["total_amount"].sum()

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Customers", total_customers)

with col2:
    st.metric("Products", total_products)

with col3:
    st.metric("Orders", total_orders)

with col4:
    st.metric("Inventory Stock", total_stock)

with col5:
    st.metric("Revenue", f"Rp {total_revenue:,.0f}")

# =========================
# CUSTOMER SECTION
# =========================
st.divider()

st.header("Customer Database")

st.dataframe(customer_df, use_container_width=True)

# =========================
# PRODUCT SECTION
# =========================
st.divider()

st.header("Product Inventory")

st.dataframe(product_df, use_container_width=True)

# =========================
# ORDER SECTION
# =========================
st.divider()

st.header("Order Management")

st.dataframe(order_df, use_container_width=True)