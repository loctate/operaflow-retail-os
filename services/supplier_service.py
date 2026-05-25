from services.supabase_client import supabase

# ====================================
# GET SUPPLIERS
# ====================================
def get_suppliers():

    response = supabase.table(
        "suppliers"
    ).select("*").execute()

    return response.data


# ====================================
# ADD SUPPLIER
# ====================================
def add_supplier(
    supplier_name,
    phone,
    email,
    city,
    category
):

    data = {
        "supplier_name": supplier_name,
        "phone": phone,
        "email": email,
        "city": city,
        "category": category
    }

    response = supabase.table(
        "suppliers"
    ).insert(data).execute()

    return response