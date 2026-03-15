"""
Example script demonstrating database connection and user operations.

Usage:
    1. Start PostgreSQL with Docker: docker-compose up -d
    2. Run this script: python db_example.py
"""

from db import DatabaseConnection, get_db_connection, UserRepository


def main():
    # Get database connection
    db = get_db_connection()
    
    # Connect to the database
    print("Connecting to PostgreSQL...")
    db.connect()
    
    # Health check
    if db.health_check():
        print("Database connection is healthy!")
    else:
        print("Database connection failed!")
        return
    
    # Initialize user repository
    user_repo = UserRepository()
    
    # List existing users
    print("\n--- Existing Users ---")
    users = user_repo.get_all()
    for user in users:
        print(f"  ID: {user.id}, Username: {user.username}, Email: {user.email}")
    
    # Create a new user (if doesn't exist)
    print("\n--- Creating Test User ---")
    existing_user = user_repo.get_by_username("testuser")
    if existing_user:
        print(f"  User 'testuser' already exists with ID: {existing_user.id}")
    else:
        new_user = user_repo.create(
            username="testuser",
            email="testuser@example.com",
            password="securepassword123"
        )
        print(f"  Created user: {new_user.username} (ID: {new_user.id})")
    
    # Test authentication
    print("\n--- Testing Authentication ---")
    auth_user = user_repo.authenticate("testuser", "securepassword123")
    if auth_user:
        print(f"  Authentication successful for: {auth_user.username}")
    else:
        print("  Authentication failed!")
    
    # Close connection
    db.close()
    print("\nDone!")


if __name__ == "__main__":
    main()
