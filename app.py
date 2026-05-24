import streamlit as st
import pandas as pd

from services.customer_service import get_customers
from services.product_service import get_products

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
# CUSTOMER SECTION
# =========================
st.header("Customer Database")

customers = get_customers()

customer_df = pd.DataFrame(customers)

st.metric("Total Customers", len(customer_df))

st.dataframe(customer_df, use_container_width=True)

# =========================
# PRODUCT SECTION
# =========================
st.divider()

st.header("Product Inventory")

products = get_products()

product_df = pd.DataFrame(products)

col1, col2 = st.columns(2)

with col1:
    st.metric("Total Products", len(product_df))

with col2:
    total_stock = product_df["stock"].sum()
    st.metric("Total Inventory Stock", total_stock)

st.dataframe(product_df, use_container_width=True)