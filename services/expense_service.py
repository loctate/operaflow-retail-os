from services.supabase_client import supabase

def get_expenses():
    response = supabase.table("expenses").select("*").execute()
    return response.data


def add_expense(expense_name, category, amount, description):
    data = {
        "expense_name": expense_name,
        "category": category,
        "amount": int(amount),
        "description": description
    }

    response = supabase.table("expenses").insert(data).execute()
    return response