from services.supabase_client import supabase

def get_products():
    response = supabase.table("products").select("*").execute()
    return response.data