from notion_client import Client
from config import get_config

def main():
    config = get_config()
    client = Client(auth=config.notion_token)
    
    print("Searching for databases...")
    
    try:
        response = client.search(
            sort={"direction": "descending", "timestamp": "last_edited_time"}
        )
        
        results = response.get("results", [])
        databases = [r for r in results if r["object"] == "database"]
        
        if not databases:
            print("No databases found.")
            return

        for db in databases:
            title = "Untitled"
            if "title" in db and db["title"]:
                title = db["title"][0]["text"]["content"]
            
            print(f"DB: {title}")
            print(f"ID: {db['id']}")
            print("-" * 20)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
