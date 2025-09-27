import oracledb

# Connection details
dsn = "192.168.0.127:1521/XEPDB1"   # Change to your Oracle DB DSN
username = "heman"                  # Your username
password = "password"               # Your password

# Establish connection
conn = oracledb.connect(user=username, password=password, dsn=dsn)
cursor = conn.cursor()

# Insert sample data
insert_query = """
INSERT INTO SAMPLE (user_prompt, generated_response)
VALUES (:1, :2)
"""
sample_data = ("Hello, how are you?", "I am fine, thank you.")
cursor.execute(insert_query, sample_data)

# Commit changes
conn.commit()
print("Sample row inserted and committed.")

# Clean up
cursor.close()
conn.close()
