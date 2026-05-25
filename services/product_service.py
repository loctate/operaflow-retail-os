from services.supabase_client import supabase

# ====================================
# GET PRODUCTS
# ====================================
def get_products():
    response = supabase.table("products").select("*").execute()
    return response.data


# ====================================
# ADD PRODUCT
# ====================================
def add_product(name, category, stock, price):
    data = {
        "name": name,
        "category": category,
        "stock": int(stock),
        "price": int(price)
    }

    response = supabase.table("products").insert(data).execute()
    return response


# ====================================
# UPDATE STOCK / REDUCE STOCK
# ====================================
def update_stock(product_name, quantity):
    product = (
        supabase.table("products")
        .select("*")
        .eq("name", product_name)
        .execute()
    )

    if product.data:
        current_stock = int(product.data[0]["stock"])
        new_stock = current_stock - int(quantity)

        if new_stock < 0:
            new_stock = 0

        response = (
            supabase.table("products")
            .update({"stock": new_stock})
            .eq("name", product_name)
            .execute()
        )

        return response


# ====================================
# RESTOCK PRODUCT / ADD STOCK
# ====================================
def restock_product(product_name, added_stock):
    product = (
        supabase.table("products")
        .select("*")
        .eq("name", product_name)
        .execute()
    )

    if product.data:
        current_stock = int(product.data[0]["stock"])
        new_stock = current_stock + int(added_stock)

        response = (
            supabase.table("products")
            .update({"stock": new_stock})
            .eq("name", product_name)
            .execute()
        )

        return response