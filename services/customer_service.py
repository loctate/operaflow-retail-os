from services.supabase_client import supabase

# =========================
# GET CUSTOMERS
# =========================
def get_customers():
    response = supabase.table("customers").select("*").execute()
    return response.data

# =========================
# ADD CUSTOMER
# =========================
def add_customer(name, phone, email, city):

    data = {
        "name": name,
        "phone": phone,
        "email": email,
        "city": city
    }

    response = supabase.table("customers").insert(data).execute()

    return response