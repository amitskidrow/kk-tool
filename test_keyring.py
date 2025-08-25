import keyring

# Retrieve the password
password = keyring.get_password('test-service', 'test-user')
print(f"Retrieved password: {password}")