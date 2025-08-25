#!/usr/bin/env python3

import secretstorage
import os

# Set DISPLAY environment variable if not set
if 'DISPLAY' not in os.environ:
    os.environ['DISPLAY'] = ':0'

# Connect to D-Bus
bus = secretstorage.dbus_init()

# Get the default collection (usually 'login')
collection = secretstorage.get_default_collection(bus)

# Print header
print(f"{'Service':<20} {'Username':<20} {'Label'}")
print("-" * 60)

# Iterate through all items in the collection
for item in collection.get_all_items():
    attributes = item.get_attributes()
    service = attributes.get('service', 'N/A')
    username = attributes.get('username', 'N/A')
    label = item.get_label()
    print(f"{service:<20} {username:<20} {label}")