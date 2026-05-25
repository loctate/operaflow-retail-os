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
def update_stock(product_name, quantity):

    product = supabase.table(
        "products"
    ).select("*").eq(
        "name",
        product_name
    ).execute()

    if product.data:

        current_stock = product.data[0]["stock"]

        new_stock = current_stock - quantity

        if new_stock < 0:
            new_stock = 0

        supabase.table("products").update(
            {
                "stock": new_stock
            }
        ).eq(
            "name",
            product_name
        ).execute()