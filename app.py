import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from services.customer_service import (
    get_customers,
    add_customer
)

from services.product_service import (
    get_products,
    add_product
)

from services.order_service import (
    get_orders,
    add_order
)

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="OperaFlow",
    page_icon="📦",
    layout="wide"
)

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
# SIDEBAR
# =========================
st.sidebar.title("OperaFlow")
st.sidebar.subheader("Retail OS")

menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Customers",
        "Products",
        "Orders"
    ]
)

# =========================
# KPI DATA
# =========================
total_customers = len(customer_df)
total_products = len(product_df)
total_orders = len(order_df)
total_stock = product_df["stock"].sum()
total_revenue = order_df["total_amount"].sum()

# =========================
# DASHBOARD PAGE
# =========================
if menu == "Dashboard":

    st.title("Retail Business Dashboard")

    # =========================
    # KPI CARDS
    # =========================
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

    # =========================
    # REVENUE TREND
    # =========================
    st.subheader("Revenue Trend")

    order_df["created_at"] = pd.to_datetime(
    order_df["created_at"]
        )

    order_df["order_date"] = order_df[
        "created_at"
        ].dt.date

    revenue_trend = order_df.groupby(
        "order_date",
        as_index=False
        )["total_amount"].sum()

    revenue_line = px.line(
        revenue_trend,
        x="order_date",
        y="total_amount",
        markers=True,
        title="Revenue Timeline"
    )

    st.plotly_chart(
        revenue_line,
        use_container_width=True
    )

    st.divider()

    # =========================
    # CHART SECTION
    # =========================
    col1, col2 = st.columns(2)

    with col1:

        revenue_chart = px.bar(
            order_df,
            x="product_name",
            y="total_amount",
            title="Revenue by Product"
        )

        st.plotly_chart(
            revenue_chart,
            use_container_width=True
        )

    with col2:

        status_chart = px.pie(
            order_df,
            names="status",
            title="Order Status Distribution"
        )

        st.plotly_chart(
            status_chart,
            use_container_width=True
        )

    st.divider()

    # =========================
    # TOP SELLING PRODUCTS
    # =========================
    st.subheader("Top Selling Products")

    top_products = order_df.groupby(
        "product_name",
        as_index=False
    )["quantity"].sum()

    top_products_chart = px.bar(
        top_products,
        x="product_name",
        y="quantity",
        title="Most Ordered Products"
    )

    st.plotly_chart(
        top_products_chart,
        use_container_width=True
    )

    st.divider()

    # =========================
    # LOW STOCK ALERT
    # =========================
    st.subheader("Low Stock Alert")

    low_stock_df = product_df[
        product_df["stock"] < 25
    ]

    st.dataframe(
        low_stock_df,
        use_container_width=True
    )

    st.divider()

    # =========================
    # RECENT ORDERS
    # =========================
    st.subheader("Recent Orders")

    recent_orders = order_df.sort_values(
        by="created_at",
        ascending=False
    )

    st.dataframe(
        recent_orders.head(5),
        use_container_width=True
    )

# =========================
# CUSTOMER PAGE
# =========================
elif menu == "Customers":

    st.title("Customer Database")

    st.subheader("Add New Customer")

    with st.form("customer_form"):

        name = st.text_input("Customer Name")

        phone = st.text_input("Phone Number")

        email = st.text_input("Email")

        city = st.text_input("City")

        submitted = st.form_submit_button(
            "Add Customer"
        )

        if submitted:

            add_customer(
                name,
                phone,
                email,
                city
            )

            st.success(
                "Customer added successfully!"
            )

            st.rerun()

    st.divider()

    st.subheader("Customer List")

    st.dataframe(
        customer_df,
        use_container_width=True
    )

# =========================
# PRODUCT PAGE
# =========================
elif menu == "Products":

    st.title("Product Inventory")

    st.subheader("Add New Product")

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

        stock = st.number_input(
            "Stock",
            min_value=0,
            step=1
        )

        price = st.number_input(
            "Price",
            min_value=0,
            step=1000
        )

        submitted = st.form_submit_button(
            "Add Product"
        )

        if submitted:

            add_product(
                name,
                category,
                int(stock),
                int(price)
            )

            st.success(
                "Product added successfully!"
            )

            st.rerun()

    st.divider()

    st.subheader("Product List")

    st.dataframe(
        product_df,
        use_container_width=True
    )

# =========================
# ORDER PAGE
# =========================
elif menu == "Orders":

    st.title("Order Management")

    st.subheader("Create New Order")

    # =========================
    # DROPDOWN DATA
    # =========================
    customer_names = customer_df["name"].tolist()

    product_names = product_df["name"].tolist()

    # =========================
    # ORDER FORM
    # =========================
    with st.form("order_form"):

        customer_name = st.selectbox(
            "Select Customer",
            customer_names
        )

        product_name = st.selectbox(
            "Select Product",
            product_names
        )

        quantity = st.number_input(
            "Quantity",
            min_value=1,
            step=1
        )

        status = st.selectbox(
            "Order Status",
            [
                "Pending",
                "Processing",
                "Completed"
            ]
        )

        # =========================
        # AUTO PRICE CALCULATION
        # =========================
        selected_product = product_df[
            product_df["name"] == product_name
        ]

        product_price = selected_product.iloc[0]["price"]

        total_amount = int(
            quantity * product_price
        )

        st.info(
            f"Total Amount: Rp {total_amount:,.0f}"
        )

        submitted = st.form_submit_button(
            "Create Order"
        )

        if submitted:

            add_order(
                customer_name,
                product_name,
                int(quantity),
                int(total_amount),
                status
            )

            st.success(
                "Order created successfully!"
            )

            st.rerun()

    st.divider()

    st.subheader("Order List")

    st.dataframe(
        order_df,
        use_container_width=True
    )