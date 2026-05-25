import streamlit as st
import pandas as pd
import plotly.express as px

from fpdf import FPDF
from datetime import datetime

from services.customer_service import get_customers, add_customer
from services.product_service import get_products, add_product, update_stock, restock_product
from services.order_service import get_orders, add_order

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

st.set_page_config(
    page_title="OperaFlow",
    page_icon="🚀",
    layout="wide"
)

st.markdown(
    """
    <style>
    .stApp { background-color: #0f1117; color: white; }
    section[data-testid="stSidebar"] { background-color: #151924; }
    div[data-testid="metric-container"] {
        background-color: #1c2230;
        border: 1px solid #2d3748;
        padding: 15px;
        border-radius: 12px;
    }
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        height: 45px;
        border: none;
        background-color: #3b82f6;
        color: white;
        font-weight: bold;
    }
    .stButton > button:hover { background-color: #2563eb; }
    </style>
    """,
    unsafe_allow_html=True
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "cart" not in st.session_state:
    st.session_state.cart = []

if "last_transaction" not in st.session_state:
    st.session_state.last_transaction = {}

def login():
    if (
        st.session_state.username == ADMIN_USERNAME
        and st.session_state.password == ADMIN_PASSWORD
    ):
        st.session_state.logged_in = True
        st.session_state.login_error = False
    else:
        st.session_state.login_error = True

def generate_receipt_pdf(trx):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "OperaFlow Receipt", ln=True, align="C")

    pdf.ln(10)
    pdf.set_font("Arial", "", 12)

    pdf.cell(0, 10, f"Date: {datetime.now().strftime('%d-%m-%Y %H:%M')}", ln=True)
    pdf.cell(0, 10, f"Customer: {trx.get('customer_name', '-')}", ln=True)
    pdf.cell(0, 10, f"Total Items: {trx.get('total_items', 1)}", ln=True)
    pdf.cell(0, 10, f"Total Payment: Rp {trx.get('total_price', 0):,.0f}", ln=True)

    pdf.ln(10)
    pdf.cell(0, 10, "Thank you for shopping!", ln=True)

    pdf_output = pdf.output(dest="S")

    if isinstance(pdf_output, str):
        return pdf_output.encode("latin-1")

    return bytes(pdf_output)

if not st.session_state.logged_in:
    st.title("🚀 OperaFlow Login")
    st.caption("Cloud Retail Management Dashboard")
    st.subheader("Retail Management System")

    if "login_error" not in st.session_state:
        st.session_state.login_error = False

    st.text_input("Username", key="username")

    st.text_input(
        "Password",
        type="password",
        key="password",
        on_change=login
    )

    st.button("Login", on_click=login)

    if st.session_state.login_error:
        st.error("Invalid username or password")

    if st.session_state.logged_in:
        st.success("Login successful!")
        st.rerun()

    st.stop()

customers = get_customers()
products = get_products()
orders = get_orders()

customer_df = pd.DataFrame(customers)
product_df = pd.DataFrame(products)
order_df = pd.DataFrame(orders)

total_customers = len(customer_df)
total_products = len(product_df)
total_orders = len(order_df)

total_stock = product_df["stock"].sum() if not product_df.empty else 0
total_revenue = order_df["total_amount"].sum() if not order_df.empty else 0

st.sidebar.markdown(
    """
    # 🚀 OperaFlow
    ### Retail Operating System
    """
)

st.sidebar.divider()
st.sidebar.info("Cloud Retail Management System")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Customers",
        "Products",
        "Orders",
        "POS",
        "Reports"
    ]
)

if menu == "Dashboard":

    st.markdown(
        """
        # 🚀 OperaFlow Dashboard

        Welcome back, Admin.  
        Here's your retail business overview today.
        """
    )

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

    st.divider()
    st.subheader("Revenue Trend")

    if not order_df.empty:
        order_df["created_at"] = pd.to_datetime(order_df["created_at"])
        order_df["order_date"] = order_df["created_at"].dt.date

        revenue_trend = order_df.groupby(
            "order_date",
            as_index=False
        )["total_amount"].sum()

        revenue_chart = px.line(
            revenue_trend,
            x="order_date",
            y="total_amount",
            markers=True,
            title="Revenue Timeline"
        )

        st.plotly_chart(revenue_chart, use_container_width=True)

    else:
        st.info("No revenue data available.")

    st.divider()
    st.subheader("Low Stock Alert")

    if not product_df.empty:
        low_stock_df = product_df[product_df["stock"] < 25]

        if len(low_stock_df) > 0:
            st.warning(f"{len(low_stock_df)} products have low stock!")
            st.dataframe(low_stock_df, use_container_width=True)
        else:
            st.success("Inventory stock levels are healthy.")
    else:
        st.info("No product inventory data available.")

elif menu == "Customers":

    st.title("Customer Database")

    with st.form("customer_form"):
        name = st.text_input("Customer Name")
        phone = st.text_input("Phone Number")
        email = st.text_input("Email")
        city = st.text_input("City")

        submitted = st.form_submit_button("Add Customer")

        if submitted:
            add_customer(name, phone, email, city)
            st.success("Customer added successfully!")
            st.rerun()

    st.divider()
    st.dataframe(customer_df, use_container_width=True)

elif menu == "Products":

    st.title("Product Inventory")

    with st.form("product_form"):
        name = st.text_input("Product Name")

        category = st.selectbox(
            "Category",
            [
                "Beverage",
                "Bakery",
                "Ingredient",
                "Frozen Food",
                "Snack",
                "Healthy"
            ]
        )

        stock = st.number_input("Stock", min_value=0, step=1)
        price = st.number_input("Price", min_value=0, step=1000)

        submitted = st.form_submit_button("Add Product")

        if submitted:
            add_product(name, category, int(stock), int(price))
            st.success("Product added successfully!")
            st.rerun()

    st.divider()

    display_products = product_df.copy()

    if not display_products.empty:
        display_products["price"] = display_products["price"].apply(
            lambda x: f"Rp {x:,.0f}"
        )

    st.dataframe(display_products, use_container_width=True)

elif menu == "Orders":

    st.title("Order Management")

    if not order_df.empty:
        display_orders = order_df.copy()

        display_orders["total_amount"] = display_orders["total_amount"].apply(
            lambda x: f"Rp {x:,.0f}"
        )

        st.dataframe(display_orders, use_container_width=True)

    else:
        st.info("No order data available.")

elif menu == "POS":

    st.title("Point of Sales")
    st.subheader("Cashier Mode")

    if product_df.empty:
        st.warning("No products available.")

    else:
        product_names = product_df["name"].tolist()

        col1, col2 = st.columns(2)

        with col1:
            selected_product = st.selectbox("Select Product", product_names)

        product_data = product_df[product_df["name"] == selected_product]

        product_price = int(product_data.iloc[0]["price"])
        current_stock = int(product_data.iloc[0]["stock"])

        with col2:
            quantity = st.number_input("Quantity", min_value=1, step=1)

        st.info(f"Stock Available: {current_stock}")

        total_price = product_price * quantity

        st.metric("Item Total", f"Rp {total_price:,.0f}")

        if st.button("Add to Cart"):
            if quantity > current_stock:
                st.error("Not enough stock.")
            else:
                cart_item = {
                    "product_name": selected_product,
                    "quantity": int(quantity),
                    "price": int(product_price),
                    "total": int(total_price)
                }

                st.session_state.cart.append(cart_item)
                st.success("Item added to cart!")
                st.rerun()

        st.divider()
        st.subheader("Shopping Cart")

        if len(st.session_state.cart) == 0:
            st.info("Cart is empty.")

        else:
            header1, header2, header3, header4, header5 = st.columns(
                [3, 1, 2, 2, 1]
            )

            with header1:
                st.markdown("**Product**")

            with header2:
                st.markdown("**Qty**")

            with header3:
                st.markdown("**Price**")

            with header4:
                st.markdown("**Total**")

            with header5:
                st.markdown("**Delete**")

            st.divider()

            for index, item in enumerate(st.session_state.cart):
                col1, col2, col3, col4, col5 = st.columns([3, 1, 2, 2, 1])

                with col1:
                    st.write(item["product_name"])

                with col2:
                    st.write(item["quantity"])

                with col3:
                    st.write(f"Rp {item['price']:,.0f}")

                with col4:
                    st.write(f"Rp {item['total']:,.0f}")

                with col5:
                    if st.button("❌", key=f"remove_{index}"):
                        st.session_state.cart.pop(index)
                        st.rerun()

            st.divider()

            grand_total = sum(item["total"] for item in st.session_state.cart)

            st.metric("Grand Total", f"Rp {grand_total:,.0f}")

            customer_name = st.text_input("Customer Name")

            if st.button("Checkout All"):
                if customer_name == "":
                    st.warning("Please input customer name.")

                else:
                    for item in st.session_state.cart:
                        add_order(
                            customer_name,
                            item["product_name"],
                            int(item["quantity"]),
                            int(item["total"]),
                            "Completed"
                        )

                        update_stock(
                            item["product_name"],
                            int(item["quantity"])
                        )

                    st.session_state.last_transaction = {
                        "customer_name": customer_name,
                        "total_price": int(grand_total),
                        "total_items": len(st.session_state.cart)
                    }

                    st.session_state.cart = []

                    st.success("Transaction completed!")
                    st.balloons()
                    st.rerun()

            if st.button("Clear Cart"):
                st.session_state.cart = []
                st.warning("Cart cleared.")
                st.rerun()

    if st.session_state.last_transaction:
        trx = st.session_state.last_transaction

        st.divider()
        st.subheader("Transaction Receipt")

        receipt_html = f"""
        <div style="
            padding:20px;
            border-radius:10px;
            border:1px solid #444;
            background-color:#111;
        ">
            <h3>OperaFlow Receipt</h3>
            <hr>
            <p><b>Customer:</b> {trx.get('customer_name', '-')}</p>
            <p><b>Total Items:</b> {trx.get('total_items', 1)}</p>
            <p><b>Total Payment:</b> Rp {trx.get('total_price', 0):,.0f}</p>
            <hr>
            <p>Thank you for shopping!</p>
        </div>
        """

        st.markdown(receipt_html, unsafe_allow_html=True)

        pdf_receipt = generate_receipt_pdf(trx)

        st.download_button(
            label="Download Receipt PDF",
            data=pdf_receipt,
            file_name="operaflow_receipt.pdf",
            mime="application/pdf"
        )

elif menu == "Reports":

    st.title("Sales Reports")

    if order_df.empty:
        st.warning("No sales data available.")

    else:
        total_sales = order_df["total_amount"].sum()
        total_transactions = len(order_df)
        avg_order = total_sales / total_transactions

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Revenue", f"Rp {total_sales:,.0f}")

        with col2:
            st.metric("Total Transactions", total_transactions)

        with col3:
            st.metric("Average Order", f"Rp {avg_order:,.0f}")

        st.divider()

        st.subheader("Sales by Product")

        product_sales = order_df.groupby(
            "product_name",
            as_index=False
        )["total_amount"].sum()

        product_chart = px.bar(
            product_sales,
            x="product_name",
            y="total_amount",
            title="Revenue by Product"
        )

        st.plotly_chart(product_chart, use_container_width=True)

        st.divider()

        st.subheader("Top Selling Products")

        top_products = order_df.groupby(
            "product_name",
            as_index=False
        )["quantity"].sum()

        top_products = top_products.sort_values(
            by="quantity",
            ascending=False
        )

        st.dataframe(top_products, use_container_width=True)

        st.divider()

        st.subheader("Transaction History")

        display_orders = order_df.copy()

        display_orders["total_amount"] = display_orders["total_amount"].apply(
            lambda x: f"Rp {x:,.0f}"
        )

        st.dataframe(display_orders, use_container_width=True)

        csv_report = order_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download Sales Report CSV",
            data=csv_report,
            file_name="sales_report.csv",
            mime="text/csv"
        )