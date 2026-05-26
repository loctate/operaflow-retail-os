from services.supabase_client import supabase

def get_purchase_orders():
    response = supabase.table("purchase_orders").select("*").execute()
    return response.data


def add_purchase_order(
    supplier_name,
    product_name,
    quantity,
    total_cost,
    status
):
    data = {
        "supplier_name": supplier_name,
        "product_name": product_name,
        "quantity": int(quantity),
        "total_cost": int(total_cost),
        "status": status
    }

    response = supabase.table("purchase_orders").insert(data).execute()
    return response