#!/usr/bin/env python3
"""
Migration script to update existing comments to the new schema
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def migrate_comments():
    """Migrate existing comments to new schema"""
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    print("🔄 Starting comment migration...")
    
    # Get all comments
    comments = await db.comments.find({}).to_list(None)
    print(f"Found {len(comments)} comments to migrate")
    
    migrated_count = 0
    
    for comment in comments:
        try:
            # Get user information for this comment
            user = await db.users.find_one({"id": comment["user_id"]})
            
            update_fields = {}
            
            # Rename comment_text to content
            if "comment_text" in comment and "content" not in comment:
                update_fields["content"] = comment["comment_text"]
                update_fields["$unset"] = {"comment_text": ""}
            
            # Rename likes to likes_count
            if "likes" in comment and "likes_count" not in comment:
                update_fields["likes_count"] = comment.get("likes", 0)
                if "$unset" not in update_fields:
                    update_fields["$unset"] = {}
                update_fields["$unset"]["likes"] = ""
            
            # Add missing fields
            if user:
                if "user_name" not in comment:
                    update_fields["user_name"] = user.get("name", "Unknown User")
                if "user_picture" not in comment:
                    update_fields["user_picture"] = user.get("picture", "")
            else:
                # Fallback for comments with missing users
                if "user_name" not in comment:
                    update_fields["user_name"] = "Unknown User"
                if "user_picture" not in comment:
                    update_fields["user_picture"] = ""
            
            if "is_flagged" not in comment:
                update_fields["is_flagged"] = False
            
            if "replies_count" not in comment:
                update_fields["replies_count"] = 0
            
            # Update the comment if there are changes
            if update_fields:
                set_fields = {k: v for k, v in update_fields.items() if k != "$unset"}
                unset_fields = update_fields.get("$unset", {})
                
                update_doc = {}
                if set_fields:
                    update_doc["$set"] = set_fields
                if unset_fields:
                    update_doc["$unset"] = unset_fields
                
                await db.comments.update_one(
                    {"_id": comment["_id"]},
                    update_doc
                )
                migrated_count += 1
                
        except Exception as e:
            print(f"Error migrating comment {comment.get('id', 'unknown')}: {str(e)}")
    
    print(f"✅ Migration completed. Updated {migrated_count} comments")
    
    # Verify migration
    sample_comment = await db.comments.find_one()
    if sample_comment:
        print("Sample migrated comment fields:", list(sample_comment.keys()))
    
    client.close()

if __name__ == "__main__":
    asyncio.run(migrate_comments())