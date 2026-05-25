from services.supabase_client import supabase

# =========================
# GET PRODUCTS
# =========================
def get_products():

    response = supabase.table("products").select("*").execute()

    return response.data

# =========================
# ADD PRODUCT
# =========================
def add_product(name, category, stock, price):

    data = {
        "name": name,
        "category": category,
        "stock": stock,
        "price": price
    }

    response = supabase.table("products").insert(data).execute()

    return response