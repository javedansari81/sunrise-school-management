#!/usr/bin/env python3
"""
Script to test password verification
"""
from app.core.security import verify_password

# Hash from database
stored_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsHjxstm6"

# Test different passwords
test_passwords = [
    "admin123",
    "password123",
    "password",
    "123456",
    "admin",
    "sunrise123",
    "school123",
    "test123"
]

print("Testing password verification...")
print(f"Stored hash: {stored_hash}")
print("-" * 50)

for password in test_passwords:
    result = verify_password(password, stored_hash)
    status = "✅ MATCH" if result else "❌ NO MATCH"
    print(f"{password:12} -> {status}")
