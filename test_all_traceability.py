"""
Test script for traceability_get_all_trees_tool.py
Gets ALL projects' traceability trees for an organization.
"""
import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

os.environ["DEBUG_TRACEABILITY"] = "true"  # Enable debug mode

from tools.traceability_get_all_trees_tool import traceability_get_all_trees_tool
import json

# Your organization ID
ORGANIZATION_ID = "b5d4ea64-ccf1-4cb6-9236-6e8b239d9097"

def test_all_trees():
    """Test getting all project trees for an organization"""
    print("=" * 100)
    print("TESTING: Get ALL Projects Traceability Trees")
    print("=" * 100)

    result = traceability_get_all_trees_tool(ORGANIZATION_ID, include_metadata=True)

    if result.get("success"):
        print("\nSUCCESS!")

        # Show summary
        if "summary" in result:
            print("\n" + "=" * 100)
            print("SUMMARY:")
            print("=" * 100)
            print(json.dumps(result["summary"], indent=2))

        # Show each project's tree
        if "projects" in result:
            print("\n" + "=" * 100)
            print(f"PROJECTS ({len(result['projects'])} total):")
            print("=" * 100)

            for idx, project in enumerate(result["projects"], 1):
                print(f"\n[{idx}] {project['project_name']}")
                print(f"    Project ID: {project['project_id']}")

                if "metadata" in project:
                    meta = project["metadata"]
                    print(f"    Total Nodes: {meta['total_nodes']}")
                    print(f"    Root Nodes: {meta['root_nodes']}")
                    print(f"    Max Depth: {meta['max_depth']}")
                    print(f"    Relationships: {meta['relationships']}")

                if "hierarchy_view" in project and len(project["hierarchy_view"]) > 0:
                    print(f"\n    HIERARCHY:")
                    print("    " + "-" * 76)
                    for line in project["hierarchy_view"]:
                        print(f"    {line}")
                else:
                    print("    (No hierarchy relationships)")

        # Save full result to file
        output_file = "traceability_all_trees_output.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\n" + "=" * 100)
        print(f"Full result saved to: {output_file}")

    else:
        print(f"\nFAILED: {result.get('error')}")
        print(f"Error Code: {result.get('error_code')}")

if __name__ == "__main__":
    print("Starting Organization-Wide Traceability Tree Tests")
    print("=" * 100)

    test_all_trees()

    print("\n" + "=" * 100)
    print("Test completed!")
    print("=" * 100)
