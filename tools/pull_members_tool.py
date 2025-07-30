"""pull members tool module"""
import json
import sys
import os
from typing import Any

# Add parent directory to sys.path to import local supabase module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client.client import get_supabase_client

def pull_members_tool(organization_id: str, message: str) -> Any:
    print(f"[pull_members] Starting with organization_id: {organization_id}")
    print(f"[pull_members] Message: {message}")
    
    try:
        # Create Supabase client
        print("[pull_members] Creating Supabase client...")
        supabase = get_supabase_client()
        
        # Query organization_members table to get user_ids
        print(f"[pull_members] Querying organization_members table for organization_id: {organization_id}")
        members_response = supabase.table("organization_members").select("user_id").eq("organization_id", organization_id).execute()
        
        if not members_response.data:
            print("[pull_members] No members found for the given organization_id")
            result = {
                "json": {
                    "members": [],
                    "message": "No members found for the given organization_id"
                }
            }
            
            # Save empty result to JSON file
            print("[pull_members] Saving empty result to JSON file...")
            with open("pull_members_tool.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            return result
        
        # Extract user_ids from the organization_members query
        user_ids = [member.get("user_id") for member in members_response.data if member.get("user_id")]
        print(f"[pull_members] Found {len(user_ids)} user_ids: {user_ids}")
        
        if not user_ids:
            print("[pull_members] No valid user_ids found")
            result = {
                "json": {
                    "members": [],
                    "message": "No valid user_ids found in organization members"
                }
            }
            
            # Save empty result to JSON file
            print("[pull_members] Saving empty result to JSON file...")
            with open("pull_members_tool.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            return result
        
        # Query profiles table using the extracted user_ids
        print(f"[pull_members] Querying profiles table for user_ids: {user_ids}")
        profiles_response = supabase.table("profiles").select("id, full_name, email").in_("id", user_ids).execute()
        
        print(f"[pull_members] Found {len(profiles_response.data)} matching profiles")
        
        # Return the matching profiles
        result = {
            "json": {
                "members": profiles_response.data,
                "user_ids": user_ids,
                "message": message
            }
        }
        
        # Save result to JSON file
        print("[pull_members] Saving result to JSON file...")
        with open("pull_members_tool.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print("[pull_members] SUCCESS: Completed successfully")
        return result

    except ValueError as e:
        print(f"[pull_members] ERROR: {str(e)}")
        return {"error": str(e)}
    except Exception as e:
        print(f"[pull_members] ERROR: Exception occurred - {str(e)}")
        return {"error": f"An error occurred: {str(e)}"}

if __name__ == "__main__":
    test_org_id = "b5d4ea64-ccf1-4cb6-9236-6e8b239d9097"
    test_message = "List up all members"
    result = pull_members_tool(test_org_id, test_message)
    print(f"Result: {result}")
