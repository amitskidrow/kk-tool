#!/usr/bin/env python3

import argparse
import sys
from typing import List, Tuple
import secretstorage
import os


def get_dbus_connection():
    """Establish D-Bus connection to Secret Service"""
    # Set DISPLAY environment variable if not set (needed for some systems)
    if 'DISPLAY' not in os.environ:
        os.environ['DISPLAY'] = ':0'
    
    try:
        bus = secretstorage.dbus_init()
        return bus
    except Exception as e:
        print(f"Error connecting to Secret Service: {e}")
        sys.exit(1)


def get_default_collection(bus):
    """Get the default collection (usually 'login')"""
    try:
        collection = secretstorage.get_default_collection(bus)
        if not collection.is_locked():
            return collection
        else:
            print("Error: Collection is locked")
            sys.exit(1)
    except Exception as e:
        print(f"Error accessing collection: {e}")
        sys.exit(1)


def mask_secret(secret: str, visible_ratio: float = 0.7) -> str:
    """
    Mask a secret by showing only the first visible_ratio portion
    
    Args:
        secret: The secret string to mask
        visible_ratio: Ratio of the secret to show (default 0.7 = 70%)
    
    Returns:
        Masked secret string
    """
    if not secret:
        return ""
    
    # For very short secrets, show only first 3 characters
    if len(secret) <= 5:
        visible_chars = min(3, len(secret))
        return secret[:visible_chars] + "*" * (len(secret) - visible_chars)
    
    # For longer secrets, show the specified ratio
    visible_length = int(len(secret) * visible_ratio)
    # Ensure at least 1 character is visible and at least 1 is masked
    visible_length = max(1, min(visible_length, len(secret) - 1))
    
    return secret[:visible_length] + "*" * (len(secret) - visible_length)


def list_secrets(masked: bool = True) -> None:
    """
    List all secrets in the keyring
    
    Args:
        masked: Whether to show masked secrets (default True)
    """
    bus = get_dbus_connection()
    collection = get_default_collection(bus)
    
    # Print header
    if masked:
        print(f"{'Service':<20} {'Username':<20} {'Label':<30} {'Secret (masked)'}")
        print("-" * 90)
    else:
        print(f"{'Service':<20} {'Username':<20} {'Label':<30} {'Secret'}")
        print("-" * 90)
    
    # Iterate through all items in the collection
    items_found = False
    for item in collection.get_all_items():
        items_found = True
        attributes = item.get_attributes()
        service = attributes.get('service', 'N/A')
        username = attributes.get('username', 'N/A')
        label = item.get_label()
        
        # Handle potential encoding issues
        try:
            if masked:
                secret_value = mask_secret(item.get_secret().decode('utf-8'))
            else:
                secret_value = item.get_secret().decode('utf-8')
        except UnicodeDecodeError:
            # If we can't decode the secret, show a placeholder
            if masked:
                secret_value = "****"
            else:
                secret_value = "[Binary data - cannot display]"
        
        print(f"{service:<20} {username:<20} {label:<30} {secret_value}")
    
    if not items_found:
        print("No secrets found in the keyring.")


def search_secrets(attribute: str, value: str, masked: bool = True) -> None:
    """
    Search for secrets by attribute
    
    Args:
        attribute: Attribute name to search by
        value: Attribute value to search for
        masked: Whether to show masked secrets (default True)
    """
    bus = get_dbus_connection()
    collection = get_default_collection(bus)
    
    # Print header
    if masked:
        print(f"{'Service':<20} {'Username':<20} {'Label':<30} {'Secret (masked)'}")
        print("-" * 90)
    else:
        print(f"{'Service':<20} {'Username':<20} {'Label':<30} {'Secret'}")
        print("-" * 90)
    
    # Search for items with matching attributes
    items_found = False
    for item in collection.get_all_items():
        attributes = item.get_attributes()
        if attributes.get(attribute) == value:
            items_found = True
            service = attributes.get('service', 'N/A')
            username = attributes.get('username', 'N/A')
            label = item.get_label()
            
            # Handle potential encoding issues
            try:
                if masked:
                    secret_value = mask_secret(item.get_secret().decode('utf-8'))
                else:
                    secret_value = item.get_secret().decode('utf-8')
            except UnicodeDecodeError:
                # If we can't decode the secret, show a placeholder
                if masked:
                    secret_value = "****"
                else:
                    secret_value = "[Binary data - cannot display]"
            
            print(f"{service:<20} {username:<20} {label:<30} {secret_value}")
    
    if not items_found:
        print(f"No secrets found with attribute '{attribute}' = '{value}'.")


def get_secret(service: str, username: str) -> None:
    """
    Retrieve and display a full secret
    
    Args:
        service: Service name
        username: Username
    """
    bus = get_dbus_connection()
    collection = get_default_collection(bus)
    
    # Search for the specific item
    for item in collection.get_all_items():
        attributes = item.get_attributes()
        if attributes.get('service') == service and attributes.get('username') == username:
            label = item.get_label()
            
            # Handle potential encoding issues
            try:
                secret_value = item.get_secret().decode('utf-8')
            except UnicodeDecodeError:
                print(f"Error: Cannot decode secret for '{label}' (may be binary data)")
                return
            
            # For non-interactive environments, just show the secret
            # In interactive environments, confirm before showing
            if sys.stdin.isatty():
                response = input(f"Show full secret for '{label}'? Type 'yes' to confirm: ")
                if response.lower() != 'yes':
                    print("Operation cancelled.")
                    return
            
            print(f"Service: {service}")
            print(f"Username: {username}")
            print(f"Label: {label}")
            print(f"Secret: {secret_value}")
            return
    
    print(f"No secret found for service '{service}' and username '{username}'.")


def main():
    parser = argparse.ArgumentParser(
        description="Browse and manage secrets in GNOME Keyring",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  list      List all secrets (with masked values by default)
  search    Search for secrets by attribute
  get       Retrieve a full secret (requires confirmation in interactive mode)

Examples:
  secret-browser list
  secret-browser search service binance
  secret-browser get binance trader1
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all secrets')
    list_parser.add_argument(
        '--unmask', 
        action='store_true',
        help='Show full secrets (WARNING: Exposes sensitive data)'
    )
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for secrets by attribute')
    search_parser.add_argument('attribute', help='Attribute name to search by')
    search_parser.add_argument('value', help='Attribute value to search for')
    search_parser.add_argument(
        '--unmask', 
        action='store_true',
        help='Show full secrets (WARNING: Exposes sensitive data)'
    )
    
    # Get command
    get_parser = subparsers.add_parser('get', help='Retrieve a full secret')
    get_parser.add_argument('service', help='Service name')
    get_parser.add_argument('username', help='Username')
    
    # Version command
    subparsers.add_parser('version', help='Show version')
    
    args = parser.parse_args()
    
    if args.command == 'list':
        list_secrets(not args.unmask)
    elif args.command == 'search':
        search_secrets(args.attribute, args.value, not args.unmask)
    elif args.command == 'get':
        get_secret(args.service, args.username)
    elif args.command == 'version':
        print("secret-browser 1.0.0")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()