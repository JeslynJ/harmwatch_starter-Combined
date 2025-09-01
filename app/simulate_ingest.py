import requests
import json
import time
from datetime import datetime

BRIDGE_URL = "http://localhost:8000"

def ingest_sample_data():
    """Simulate ingesting sample data to the bridge server."""
    
    sample_posts = [
        {
            "text": "Check out this amazing free prize! Click here to claim your gift card now!",
            "source": "twitter",
            "author": "user123",
            "platform": "Twitter",
            "url": "https://twitter.com/user123/status/123456"
        },
        {
            "text": "I'm feeling really hopeless today. Everything seems so dark.",
            "source": "instagram",
            "author": "user456",
            "platform": "Instagram",
            "url": "https://instagram.com/p/abcdef/"
        },
        {
            "text": "This is fake news! Don't believe the mainstream media!",
            "source": "facebook",
            "author": "user789",
            "platform": "Facebook",
            "url": "https://facebook.com/groups/123/posts/456"
        },
        {
            "text": "You're so stupid and worthless. Nobody likes you.",
            "source": "reddit",
            "author": "user101",
            "platform": "Reddit",
            "url": "https://reddit.com/r/subreddit/comments/123"
        },
        {
            "text": "New CVE-2024-1234 vulnerability discovered. Here's the exploit code...",
            "source": "hacker_forum",
            "author": "hacker_user",
            "platform": "Forum",
            "url": "https://hackerforum.com/threads/123"
        }
    ]
    
    print("Starting data ingestion simulation...")
    
    for i, post in enumerate(sample_posts):
        try:
            # Add timestamp
            post["timestamp"] = datetime.utcnow().isoformat() + "Z"
            
            # Send to bridge
            response = requests.post(f"{BRIDGE_URL}/ingest", json=post)
            
            if response.status_code == 200:
                print(f"✅ Ingested post {i+1}: {post['text'][:50]}...")
            else:
                print(f"❌ Failed to ingest post {i+1}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error ingesting post {i+1}: {e}")
        
        # Wait between posts
        time.sleep(2)
    
    print("Data ingestion simulation completed!")

def check_bridge_health():
    """Check if the bridge server is running."""
    try:
        response = requests.get(f"{BRIDGE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Bridge server is healthy: {data}")
            return True
        else:
            print(f"❌ Bridge server returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to bridge server: {e}")
        return False

if __name__ == "__main__":
    print("HarmWatch Data Ingestion Simulator")
    print("=" * 40)
    
    if check_bridge_health():
        ingest_sample_data()
    else:
        print("\nPlease start the bridge server first:")
        print("cd harmwatch_starter/app")
        print("python bridge.py")
