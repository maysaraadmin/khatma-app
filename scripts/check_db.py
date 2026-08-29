import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khatma.settings')
django.setup()

from django.db import connection

def check_table_exists(table_name):
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='{table_name}';
        """)
        result = cursor.fetchone()
        return result is not None

# Check if the ReadingGroup table exists
print(f"ReadingGroup table exists: {check_table_exists('groups_readinggroup')}")

# Check if the GroupMembership table exists
print(f"GroupMembership table exists: {check_table_exists('groups_groupmembership')}")

# List all tables in the database
with connection.cursor() as cursor:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("\nAll tables in the database:")
    for table in tables:
        print(f"- {table[0]}")

# Try to create the tables if they don't exist
try:
    from django.core.management import call_command
    print("\nRunning migrations for groups app...")
    call_command('migrate', 'groups')
    print("Migrations completed successfully.")
except Exception as e:
    print(f"Error running migrations: {e}")
