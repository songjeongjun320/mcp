"""mail to tool module"""

import json
import sys
import os
from typing import Any

# Add parent directory to sys.path to import local supabase module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client.client import get_supabase_client

def mail_to_tool(organization_id: str, sender: str, recipient: str, recipient_email: str, subject: str, body: str, message: str) -> Any:
    print(f"[mail_to] Starting with organization_id: {organization_id}")
    print(f"[mail_to] Message: {message}")
    
    try:
        # Create Supabase client
        print("[mail_to] Creating Supabase client...")
        supabase = get_supabase_client()

    except ValueError as e:
        print(f"[mail_to] ERROR: {str(e)}")
        return {"error": str(e)}
    except Exception as e:
        print(f"[mail_to] ERROR: Exception occurred - {str(e)}")
        return {"error": f"An error occurred: {str(e)}"}
    raise NotImplementedError
