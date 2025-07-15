import psycopg2

# Test different connection methods
test_configs = [
    {'host': '127.0.0.1', 'user': 'postgres', 'password': 'polymath88', 'database': 'postgres'},
    {'host': 'localhost', 'user': 'postgres', 'password': 'polymath88', 'database': 'postgres'},
    {'host': '::1', 'user': 'postgres', 'password': 'polymath88', 'database': 'postgres'},
]

for i, config in enumerate(test_configs):
    print(f"Testing config {i+1}: {config['host']}")
    try:
        conn = psycopg2.connect(**config)
        print(f"✅ Success with {config['host']}")
        conn.close()
        break
    except Exception as e:
        print(f"❌ Failed with {config['host']}: {e}")

print("\nIf none worked, the password might be incorrect.")