from services.supabase_client import supabase

def get_orders():
    response = supabase.table("orders").select("*").execute()
    return response.data