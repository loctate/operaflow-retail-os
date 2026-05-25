from services.supabase_client import supabase

# =========================
# GET ORDERS
# =========================
def get_orders():

    response = supabase.table("orders").select("*").execute()

    return response.data

# =========================
# ADD ORDER
# =========================
def add_order(
    customer_name,
    product_name,
    quantity,
    total_amount,
    status
):

    data = {
        "customer_name": customer_name,
        "product_name": product_name,
        "quantity": quantity,
        "total_amount": total_amount,
        "status": status
    }

    response = supabase.table("orders").insert(data).execute()

    return response