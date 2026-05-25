import streamlit as st
import pandas as pd
import plotly.express as px

from services.customer_service import (
    get_customers,
    add_customer
)

from services.product_service import (
    get_products,
    add_product,
    update_stock
)

from services.order_service import (
    get_orders,
    add_order
)

# ====================================
# LOGIN CONFIG
# ====================================
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# ====================================
# PAGE CONFIG
# ====================================
st.set_page_config(
    page_title="OperaFlow",
    page_icon="📦",
    layout="wide"
)

# ====================================
# SESSION STATE
# ====================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "cart" not in st.session_state:
    st.session_state.cart = []
    
if "last_transaction" not in st.session_state:
    st.session_state.last_transaction = {}
    
# ====================================
# LOGIN FUNCTION
# ====================================
def login():

    if (
        st.session_state.username
        == ADMIN_USERNAME
        and
        st.session_state.password
        == ADMIN_PASSWORD
    ):

        st.session_state.logged_in = True
        st.session_state.login_error = False

    else:

        st.session_state.login_error = True

# ====================================
# LOGIN PAGE
# ====================================
if not st.session_state.logged_in:

    st.title("OperaFlow Login")

    st.caption(
        "Cloud Retail Management Dashboard"
    )

    st.subheader(
        "Retail Management System"
    )

    if "login_error" not in st.session_state:
        st.session_state.login_error = False

    st.text_input(
        "Username",
        key="username"
    )

    st.text_input(
        "Password",
        type="password",
        key="password",
        on_change=login
    )

    st.button(
        "Login",
        on_click=login
    )

    if st.session_state.login_error:

        st.error(
            "Invalid username or password"
        )

    if st.session_state.logged_in:

        st.success("Login successful!")

        st.rerun()

    st.stop()

# ====================================
# LOAD DATA
# ====================================
customers = get_customers()
products = get_products()
orders = get_orders()

customer_df = pd.DataFrame(customers)
product_df = pd.DataFrame(products)
order_df = pd.DataFrame(orders)

# ====================================
# SAFE EMPTY HANDLING
# ====================================
if not product_df.empty:
    total_stock = product_df["stock"].sum()
else:
    total_stock = 0

if not order_df.empty:
    total_revenue = order_df["total_amount"].sum()
else:
    total_revenue = 0

# ====================================
# KPI
# ====================================
total_customers = len(customer_df)
total_products = len(product_df)
total_orders = len(order_df)

# ====================================
# SIDEBAR
# ====================================
st.sidebar.title("OperaFlow")
st.sidebar.subheader("Retail OS")

st.sidebar.divider()

st.sidebar.info(
    "Cloud Retail Management System"
)

# ====================================
# LOGOUT
# ====================================
if st.sidebar.button("Logout"):

    st.session_state.logged_in = False

    st.rerun()

# ====================================
# MENU
# ====================================
menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Customers",
        "Products",
        "Orders",
        "POS"
    ]
)

# ====================================
# DASHBOARD PAGE
# ====================================
if menu == "Dashboard":

    st.title("Retail Business Dashboard")

    # ====================================
    # KPI CARDS
    # ====================================
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Customers", total_customers)

    with col2:
        st.metric("Products", total_products)

    with col3:
        st.metric("Orders", total_orders)

    with col4:
        st.metric(
            "Inventory Stock",
            total_stock
        )

    with col5:
        st.metric(
            "Revenue",
            f"Rp {total_revenue:,.0f}"
        )

    st.divider()

    # ====================================
    # REVENUE TREND
    # ====================================
    st.subheader("Revenue Trend")

    if not order_df.empty:

        order_df["created_at"] = pd.to_datetime(
            order_df["created_at"]
        )

        order_df["order_date"] = (
            order_df["created_at"]
            .dt.date
        )

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

        st.plotly_chart(
            revenue_chart,
            use_container_width=True
        )

    else:

        st.info(
            "No revenue data available."
        )

    st.divider()

    # ====================================
    # CHARTS
    # ====================================
    col1, col2 = st.columns(2)

    with col1:

        if not order_df.empty:

            product_chart = px.bar(
                order_df,
                x="product_name",
                y="total_amount",
                title="Revenue by Product"
            )

            st.plotly_chart(
                product_chart,
                use_container_width=True
            )

        else:

            st.info(
                "No product sales data."
            )

    with col2:

        if not order_df.empty:

            status_chart = px.pie(
                order_df,
                names="status",
                title="Order Status"
            )

            st.plotly_chart(
                status_chart,
                use_container_width=True
            )

        else:

            st.info(
                "No order status data."
            )

    st.divider()

    # ====================================
    # TOP PRODUCTS
    # ====================================
    st.subheader("Top Selling Products")

    if not order_df.empty:

        top_products = order_df.groupby(
            "product_name",
            as_index=False
        )["quantity"].sum()

        top_chart = px.bar(
            top_products,
            x="product_name",
            y="quantity",
            title="Most Ordered Products"
        )

        st.plotly_chart(
            top_chart,
            use_container_width=True
        )

    else:

        st.info(
            "No top selling product data."
        )

    st.divider()

    # ====================================
    # LOW STOCK ALERT
    # ====================================
    st.subheader("Low Stock Alert")

    if not product_df.empty:

        low_stock_df = product_df[
            product_df["stock"] < 25
        ]

        if len(low_stock_df) > 0:

            st.warning(
                f"{len(low_stock_df)} products have low stock!"
            )

            st.dataframe(
                low_stock_df,
                use_container_width=True
            )

        else:

            st.success(
                "Inventory stock levels are healthy."
            )

    else:

        st.info(
            "No inventory data available."
        )

    st.divider()

    # ====================================
    # RECENT ORDERS
    # ====================================
    st.subheader("Recent Orders")

    if not order_df.empty:

        recent_orders = order_df.sort_values(
            by="created_at",
            ascending=False
        )

        display_orders = recent_orders.copy()

        display_orders["total_amount"] = (
            display_orders["total_amount"]
            .apply(
                lambda x:
                f"Rp {x:,.0f}"
            )
        )

        st.dataframe(
            display_orders.head(5),
            use_container_width=True
        )

    else:

        st.info(
            "No recent orders available."
        )

# ====================================
# CUSTOMER PAGE
# ====================================
elif menu == "Customers":

    st.title("Customer Database")

    st.subheader("Add New Customer")

    with st.form("customer_form"):

        name = st.text_input(
            "Customer Name"
        )

        phone = st.text_input(
            "Phone Number"
        )

        email = st.text_input(
            "Email"
        )

        city = st.text_input(
            "City"
        )

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

    csv_customer = customer_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Download Customer CSV",
        data=csv_customer,
        file_name="customers.csv",
        mime="text/csv"
    )

# ====================================
# PRODUCT PAGE
# ====================================
elif menu == "Products":

    st.title("Product Inventory")

    st.subheader("Add New Product")

    with st.form("product_form"):

        name = st.text_input(
            "Product Name"
        )

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

    display_products = product_df.copy()

    if not display_products.empty:

        display_products["price"] = (
            display_products["price"]
            .apply(
                lambda x:
                f"Rp {x:,.0f}"
            )
        )

    st.dataframe(
        display_products,
        use_container_width=True
    )

    csv_product = product_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Download Product CSV",
        data=csv_product,
        file_name="products.csv",
        mime="text/csv"
    )

# ====================================
# ORDER PAGE
# ====================================
elif menu == "Orders":

    st.title("Order Management")

    st.subheader("Order List")

    if not order_df.empty:

        display_orders = order_df.copy()

        display_orders["total_amount"] = (
            display_orders["total_amount"]
            .apply(
                lambda x:
                f"Rp {x:,.0f}"
            )
        )

        st.dataframe(
            display_orders,
            use_container_width=True
        )

    else:

        st.info(
            "No order data available."
        )

    csv_order = order_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Download Orders CSV",
        data=csv_order,
        file_name="orders.csv",
        mime="text/csv"
    )

# ====================================
# POS PAGE
# ====================================
elif menu == "POS":

    st.title("Point of Sales")

    st.subheader("Cashier Mode")

    if product_df.empty:

        st.warning(
            "No products available."
        )

    else:

        product_names = product_df[
            "name"
        ].tolist()

        col1, col2 = st.columns(2)

        with col1:

            selected_product = st.selectbox(
                "Select Product",
                product_names
            )

        product_data = product_df[
            product_df["name"]
            == selected_product
        ]

        product_price = int(
            product_data.iloc[0]["price"]
        )

        current_stock = int(
            product_data.iloc[0]["stock"]
        )

        with col2:

            quantity = st.number_input(
                "Quantity",
                min_value=1,
                step=1
            )

        st.info(
            f"Stock Available: {current_stock}"
        )

        total_price = (
            product_price * quantity
        )

        st.metric(
            "Item Total",
            f"Rp {total_price:,.0f}"
        )

        # ====================================
        # ADD TO CART
        # ====================================
        if st.button("Add to Cart"):

            cart_item = {
                "product_name": selected_product,
                "quantity": quantity,
                "price": product_price,
                "total": total_price
            }

            st.session_state.cart.append(
                cart_item
            )

            st.success(
                "Item added to cart!"
            )

            st.rerun()

        st.divider()

        # ====================================
        # CART SECTION
        # ====================================
        st.subheader("Shopping Cart")

        if len(st.session_state.cart) == 0:

            st.info("Cart is empty.")

        else:

            # ====================================
            # CART HEADER
            # ====================================
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

            # ====================================
            # CART ITEMS
            # ====================================
            for index, item in enumerate(
                st.session_state.cart
            ):

                col1, col2, col3, col4, col5 = st.columns(
                    [3, 1, 2, 2, 1]
                )

                with col1:
                    st.write(
                        item["product_name"]
                    )

                with col2:
                    st.write(
                        item["quantity"]
                    )

                with col3:
                    st.write(
                        f"Rp {item['price']:,.0f}"
                    )

                with col4:
                    st.write(
                        f"Rp {item['total']:,.0f}"
                    )

                with col5:

                    if st.button(
                        "❌",
                        key=f"remove_{index}"
                    ):

                        st.session_state.cart.pop(
                            index
                        )

                        st.rerun()

            st.divider()

            # ====================================
            # GRAND TOTAL
            # ====================================
            grand_total = sum(
                item["total"]
                for item in st.session_state.cart
            )

            st.metric(
                "Grand Total",
                f"Rp {grand_total:,.0f}"
            )

            customer_name = st.text_input(
                "Customer Name"
            )

            # ====================================
            # CHECKOUT
            # ====================================
            if st.button("Checkout All"):

                if customer_name == "":

                    st.warning(
                        "Please input customer name."
                    )

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
                        "total_price": grand_total,
                        "total_items": len(
                            st.session_state.cart
                        )
                    }

                    st.session_state.cart = []

                    st.success(
                        "Transaction completed!"
                    )

                    st.balloons()

                    st.rerun()

            # ====================================
            # CLEAR CART
            # ====================================
            if st.button("Clear Cart"):

                st.session_state.cart = []

                st.warning(
                    "Cart cleared."
                )

                st.rerun()

    # ====================================
    # RECEIPT SECTION
    # ====================================
    if "last_transaction" in st.session_state:

        trx = st.session_state.last_transaction

        st.divider()

        st.subheader(
            "Transaction Receipt"
        )

        receipt_html = f"""
        <div style="
            padding:20px;
            border-radius:10px;
            border:1px solid #444;
            background-color:#111;
        ">

        <h3>OperaFlow Receipt</h3>

        <hr>

        <p><b>Customer:</b>
        {trx.get('customer_name', '-')}</p>

        <p><b>Total Items:</b>
        {trx.get('total_items', 1)}</p>

        <p><b>Total Payment:</b>
        Rp {trx.get('total_price', 0):,.0f}</p>

        <hr>

        <p>Thank you for shopping!</p>

        </div>
        """

        st.markdown(
            receipt_html,
            unsafe_allow_html=True
        )