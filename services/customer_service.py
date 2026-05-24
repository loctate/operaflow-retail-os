from services.supabase_client import supabase

def get_customers():
    response = supabase.table("customers").select("*").execute()
    return response.data