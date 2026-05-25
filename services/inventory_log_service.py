from services.supabase_client import supabase

# ====================================
# ADD INVENTORY LOG
# ====================================
def add_inventory_log(
    product_name,
    movement_type,
    quantity
):

    data = {
        "product_name": product_name,
        "movement_type": movement_type,
        "quantity": int(quantity)
    }

    response = supabase.table(
        "inventory_logs"
    ).insert(data).execute()

    return response


# ====================================
# GET INVENTORY LOGS
# ====================================
def get_inventory_logs():

    response = supabase.table(
        "inventory_logs"
    ).select("*").execute()

    return response.data