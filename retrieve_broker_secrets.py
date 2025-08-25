#!/usr/bin/env python3

import keyring

# Define the services and usernames
services = [
    ('binance', 'trader1'),
    ('upstox', 'investor2'),
    ('coinbase', 'crypto_user3')
]

# Print header
print(f"{'Service':<15} {'Username':<15} {'Password'}")
print("-" * 50)

# Retrieve and print passwords for each service
for service, username in services:
    password = keyring.get_password(service, username)
    print(f"{service:<15} {username:<15} {password}")