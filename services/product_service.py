from config.supabase_config import supabase

# ====================================
# GET PRODUCTS
# ====================================
def get_products():

    response = supabase.table(
        "products"
    ).select("*").execute()

    return response.data


# ====================================
# ADD PRODUCT
# ====================================
def add_product(
    name,
    category,
    stock,
    price
):

    data = {
        "name": name,
        "category": category,
        "stock": int(stock),
        "price": int(price)
    }

    response = supabase.table(
        "products"
    ).insert(data).execute()

    return response


# ====================================
# UPDATE STOCK (AUTO REDUCE)
# ====================================
def update_stock(
    product_name,
    quantity
):

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

        supabase.table(
            "products"
        ).update(
            {
                "stock": new_stock
            }
        ).eq(
            "name",
            product_name
        ).execute()


# ====================================
# RESTOCK PRODUCT
# ====================================
def restock_product(
    product_name,
    added_stock
):

    product = supabase.table(
        "products"
    ).select("*").eq(
        "name",
        product_name
    ).execute()

    if product.data:

        current_stock = product.data[0]["stock"]

        new_stock = current_stock + added_stock

        supabase.table(
            "products"
        ).update(
            {
                "stock": new_stock
            }
        ).eq(
            "name",
            product_name
        ).execute()