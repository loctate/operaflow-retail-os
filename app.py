import streamlit as st
import pandas as pd

from services.customer_service import get_customers

st.set_page_config(
    page_title="OperaFlow",
    layout="wide"
)

st.title("OperaFlow")
st.subheader("Retail Business Operating System")

st.divider()

st.header("Customer Database")

customers = get_customers()

df = pd.DataFrame(customers)

st.dataframe(df, use_container_width=True)