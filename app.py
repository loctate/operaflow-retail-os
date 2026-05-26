import streamlit as st
import pandas as pd
import plotly.express as px

from fpdf import FPDF
from datetime import datetime

from services.customer_service import get_customers, add_customer
from services.product_service import get_products, add_product, update_stock, restock_product
from services.order_service import get_orders, add_order
from services.inventory_log_service import add_inventory_log, get_inventory_logs
from services.supplier_service import get_suppliers, add_supplier
from services.expense_service import get_expenses, add_expense
from services.purchase_order_service import get_purchase_orders, add_purchase_order

USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "cashier": {"password": "cashier123", "role": "cashier"}
}

st.set_page_config(
    page_title="OperaFlow",
    page_icon="🚀",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #0f1117;
    color: white;
}

section[data-testid="stSidebar"] {
    background-color: #151924;
}

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

.stButton > button:hover {
    background-color: #2563eb;
}

.login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 90vh;
}

.login-box {
    background: rgba(255,255,255,0.05);
    padding: 40px;
    border-radius: 20px;
    width: 420px;
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}

.login-title {
    font-size: 42px;
    font-weight: bold;
    text-align: center;
    margin-bottom: 10px;
}

.login-subtitle {
    text-align: center;
    color: #9ca3af;
    margin-bottom: 30px;
}

.demo-box {
    background-color: rgba(59,130,246,0.15);
    padding: 15px;
    border-radius: 12px;
    margin-top: 20px;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "cart" not in st.session_state:
    st.session_state.cart = []

if "last_transaction" not in st.session_state:
    st.session_state.last_transaction = {}

if "role" not in st.session_state:
    st.session_state.role = None

if "current_user" not in st.session_state:
    st.session_state.current_user = None


def login():
    username = st.session_state.username
    password = st.session_state.password

    if username in USERS and USERS[username]["password"] == password:
        st.session_state.logged_in = True
        st.session_state.login_error = False
        st.session_state.role = USERS[username]["role"]
        st.session_state.current_user = username
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

    st.markdown("""
    <div class="login-container">
        <div class="login-box">
            <div class="login-title">
                🚀 OperaFlow
            </div>
            <div class="login-subtitle">
                AI-Powered Retail Operating System
            </div>
    """, unsafe_allow_html=True)

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

    st.markdown("""
            <div class="demo-box">
                <b>Demo Accounts</b><br><br>
                Admin:<br>
                username: admin<br>
                password: admin123<br><br>
                Cashier:<br>
                username: cashier<br>
                password: cashier123
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.logged_in:
        st.success("Login successful!")
        st.rerun()

    st.stop()


customers = get_customers()
products = get_products()
orders = get_orders()
inventory_logs = get_inventory_logs()
suppliers = get_suppliers()
expenses = get_expenses()
purchase_orders = get_purchase_orders()

customer_df = pd.DataFrame(customers)
product_df = pd.DataFrame(products)
order_df = pd.DataFrame(orders)
inventory_log_df = pd.DataFrame(inventory_logs)
supplier_df = pd.DataFrame(suppliers)
expense_df = pd.DataFrame(expenses)
purchase_order_df = pd.DataFrame(purchase_orders)

total_customers = len(customer_df)
total_products = len(product_df)
total_orders = len(order_df)

total_stock = product_df["stock"].sum() if not product_df.empty else 0
total_revenue = order_df["total_amount"].sum() if not order_df.empty else 0
total_expenses = expense_df["amount"].sum() if not expense_df.empty else 0
net_profit = total_revenue - total_expenses

st.sidebar.markdown("""
# 🚀 OperaFlow

### Retail Operating System
""")

st.sidebar.divider()
st.sidebar.success(
    f"Logged in as: {st.session_state.current_user} ({st.session_state.role})"
)
st.sidebar.info("Cloud Retail Management System")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.current_user = None
    st.rerun()

if st.session_state.role == "admin":
    menu_options = [
        "Dashboard",
        "Customers",
        "Products",
        "Orders",
        "POS",
        "Reports",
        "Inventory Logs",
        "Suppliers",
        "Expenses",
        "Profit Dashboard",
        "Purchase Orders",
        "AI Insights"
    ]
elif st.session_state.role == "cashier":
    menu_options = ["POS", "Orders"]
else:
    menu_options = []

menu = st.sidebar.radio("Navigation", menu_options)


if menu == "Dashboard":

    st.markdown("""
    # 🚀 OperaFlow Dashboard

    Welcome back, Admin.  
    Here's your retail business overview today.
    """)

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

    st.subheader("Add New Product")

    with st.form("product_form"):
        name = st.text_input("Product Name")

        category = st.selectbox(
            "Category",
            ["Beverage", "Bakery", "Ingredient", "Frozen Food", "Snack", "Healthy"]
        )

        stock = st.number_input("Stock", min_value=0, step=1)
        price = st.number_input("Price", min_value=0, step=1000)

        submitted = st.form_submit_button("Add Product")

        if submitted:
            add_product(name, category, int(stock), int(price))
            st.success("Product added successfully!")
            st.rerun()

    st.divider()
    st.subheader("Restock Product")

    if product_df.empty:
        st.info("No products available for restock.")
    else:
        product_names = product_df["name"].tolist()
        restock_product_name = st.selectbox("Select Product to Restock", product_names)
        added_stock = st.number_input("Add Stock Quantity", min_value=1, step=1)

        if st.button("Restock Product"):
            restock_product(restock_product_name, int(added_stock))
            add_inventory_log(restock_product_name, "IN", int(added_stock))
            st.success("Product stock updated successfully!")
            st.rerun()

    st.divider()
    st.subheader("Product List")

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

                        update_stock(item["product_name"], int(item["quantity"]))
                        add_inventory_log(item["product_name"], "OUT", int(item["quantity"]))

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

        csv_report = order_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download Sales Report CSV",
            data=csv_report,
            file_name="sales_report.csv",
            mime="text/csv"
        )


elif menu == "Inventory Logs":

    st.title("Inventory Movement Logs")

    if inventory_log_df.empty:
        st.info("No inventory movement logs available.")
    else:
        display_logs = inventory_log_df.copy()
        display_logs["created_at"] = pd.to_datetime(display_logs["created_at"])
        display_logs = display_logs.sort_values(by="created_at", ascending=False)

        st.dataframe(display_logs, use_container_width=True)


elif menu == "Suppliers":

    st.title("Supplier Management")

    st.subheader("Add New Supplier")

    with st.form("supplier_form"):
        supplier_name = st.text_input("Supplier Name")
        phone = st.text_input("Phone")
        email = st.text_input("Email")
        city = st.text_input("City")

        category = st.selectbox(
            "Category",
            [
                "Beverage",
                "Bakery",
                "Ingredient",
                "Frozen Food",
                "Snack",
                "Healthy",
                "Other"
            ]
        )

        submitted = st.form_submit_button("Add Supplier")

        if submitted:
            add_supplier(supplier_name, phone, email, city, category)

            st.success("Supplier added successfully!")
            st.rerun()

    st.divider()
    st.subheader("Supplier List")
    st.dataframe(supplier_df, use_container_width=True)


elif menu == "Expenses":

    st.title("Expense Tracking")

    st.subheader("Add New Expense")

    with st.form("expense_form"):
        expense_name = st.text_input("Expense Name")

        category = st.selectbox(
            "Category",
            [
                "Rent",
                "Salary",
                "Utilities",
                "Internet",
                "Packaging",
                "Marketing",
                "Transport",
                "Other"
            ]
        )

        amount = st.number_input("Amount", min_value=0, step=1000)
        description = st.text_area("Description")

        submitted = st.form_submit_button("Add Expense")

        if submitted:
            add_expense(expense_name, category, int(amount), description)

            st.success("Expense added successfully!")
            st.rerun()

    st.divider()

    st.subheader("Expense List")

    display_expense_df = expense_df.copy()

    if not display_expense_df.empty:
        display_expense_df["amount"] = display_expense_df["amount"].apply(
            lambda x: f"Rp {x:,.0f}"
        )

    st.dataframe(display_expense_df, use_container_width=True)


elif menu == "Profit Dashboard":

    st.title("Profit Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Revenue", f"Rp {total_revenue:,.0f}")

    with col2:
        st.metric("Total Expenses", f"Rp {total_expenses:,.0f}")

    with col3:
        st.metric("Net Profit", f"Rp {net_profit:,.0f}")

    st.divider()

    st.subheader("Expense Breakdown")

    if not expense_df.empty:
        expense_by_category = expense_df.groupby(
            "category",
            as_index=False
        )["amount"].sum()

        expense_chart = px.bar(
            expense_by_category,
            x="category",
            y="amount",
            title="Expenses by Category"
        )

        st.plotly_chart(expense_chart, use_container_width=True)
    else:
        st.info("No expense data available.")


elif menu == "Purchase Orders":

    st.title("Purchase Order System")

    st.subheader("Create Purchase Order")

    if supplier_df.empty or product_df.empty:
        st.warning("Please add suppliers and products first.")
    else:
        supplier_names = supplier_df["supplier_name"].tolist()
        product_names = product_df["name"].tolist()

        with st.form("purchase_order_form"):
            supplier_name = st.selectbox("Select Supplier", supplier_names)
            product_name = st.selectbox("Select Product", product_names)

            quantity = st.number_input("Quantity", min_value=1, step=1)

            total_cost = st.number_input("Total Cost", min_value=0, step=1000)

            status = st.selectbox("Status", ["Pending", "Received"])

            submitted = st.form_submit_button("Create Purchase Order")

            if submitted:
                add_purchase_order(
                    supplier_name,
                    product_name,
                    int(quantity),
                    int(total_cost),
                    status
                )

                if status == "Received":
                    restock_product(product_name, int(quantity))
                    add_inventory_log(product_name, "IN", int(quantity))

                st.success("Purchase order created successfully!")
                st.rerun()

    st.divider()

    st.subheader("Purchase Order List")

    display_po_df = purchase_order_df.copy()

    if not display_po_df.empty:
        display_po_df["total_cost"] = display_po_df["total_cost"].apply(
            lambda x: f"Rp {x:,.0f}"
        )

    st.dataframe(display_po_df, use_container_width=True)


elif menu == "AI Insights":

    st.title("AI Business Insights")

    st.subheader("Smart Restock Recommendation")

    if not product_df.empty:
        low_stock_products = product_df[product_df["stock"] < 20]

        if len(low_stock_products) > 0:
            st.warning("These products are running low and should be restocked soon.")
            st.dataframe(low_stock_products, use_container_width=True)
        else:
            st.success("All products currently have healthy stock levels.")

    st.divider()

    st.subheader("Best Selling Products")

    if not order_df.empty:
        best_seller = order_df.groupby(
            "product_name",
            as_index=False
        )["quantity"].sum()

        best_seller = best_seller.sort_values(by="quantity", ascending=False)

        st.dataframe(best_seller, use_container_width=True)

        best_chart = px.bar(
            best_seller,
            x="product_name",
            y="quantity",
            title="Top Selling Products"
        )

        st.plotly_chart(best_chart, use_container_width=True)
    else:
        st.info("No sales data available.")

    st.divider()

    st.subheader("Slow Moving Products")

    if not order_df.empty and not product_df.empty:
        sold_products = order_df["product_name"].unique()
        slow_products = product_df[
            ~product_df["name"].isin(sold_products)
        ]

        if len(slow_products) > 0:
            st.warning("These products have low or no sales activity.")
            st.dataframe(slow_products, use_container_width=True)
        else:
            st.success("All products have sales activity.")

    st.divider()

    st.subheader("AI Business Summary")

    st.info(
        f"""
        OperaFlow AI Summary:

        • Total Products: {total_products}

        • Total Customers: {total_customers}

        • Total Orders: {total_orders}

        • Current Revenue: Rp {total_revenue:,.0f}

        • Total Expenses: Rp {total_expenses:,.0f}

        • Net Profit: Rp {net_profit:,.0f}

        • System recommends monitoring low-stock products regularly.

        • Best-selling products should be prioritized for restocking.

        • Slow-moving products may require promotion or discount strategies.
        """
    )