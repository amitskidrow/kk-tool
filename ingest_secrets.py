#!/usr/bin/env python3
"""
Secret Ingestion Script for kk tool

This script ingests environment files (.env) and stores their contents
as secrets in GNOME Keyring using the keyring library.

File naming convention:
- .binance.env -> service name: binance
- .upstox.env -> service name: upstox

Within each file, key-value pairs are stored as:
- Key becomes the label
- Value becomes the secret
- Service name is derived from filename
"""

import os
import sys
import argparse
import keyring
from pathlib import Path


def extract_service_name(filename):
    """
    Extract service name from filename.
    
    Examples:
    - .binance.env -> binance
    - .upstox.env -> upstox
    - test.env -> test
    """
    # Remove leading dot if present
    if filename.startswith('.'):
        filename = filename[1:]
    
    # Remove .env extension
    if filename.endswith('.env'):
        filename = filename[:-4]
    
    return filename


def parse_env_file(filepath):
    """
    Parse a .env file and return key-value pairs.
    
    Returns:
        dict: Dictionary of key-value pairs from the file
    """
    secrets = {}
    
    try:
        with open(filepath, 'r') as f:
            for line_num, line in enumerate(f, 1):
                # Skip empty lines and comments
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Skip lines without '='
                if '=' not in line:
                    print(f"Warning: Skipping line {line_num} in {filepath}: No '=' found")
                    continue
                
                # Split on first '=' only to handle values with '='
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Remove quotes if present
                if value.startswith('"') and value.endswith('"') and len(value) >= 2:
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'") and len(value) >= 2:
                    value = value[1:-1]
                
                if not key:
                    print(f"Warning: Skipping line {line_num} in {filepath}: Empty key")
                    continue
                
                secrets[key] = value
                
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None
    
    return secrets


def ingest_secrets(directory, dry_run=False):
    """
    Ingest secrets from .env files in the specified directory.
    
    Args:
        directory (str): Directory to scan for .env files
        dry_run (bool): If True, only print what would be done without storing secrets
    """
    directory_path = Path(directory)
    
    if not directory_path.exists():
        print(f"Error: Directory {directory} does not exist")
        return False
    
    if not directory_path.is_dir():
        print(f"Error: {directory} is not a directory")
        return False
    
    # Find all .env files (avoiding duplicates)
    env_files = list(directory_path.glob(".*.env"))
    # Add non-hidden .env files that aren't already included
    for file in directory_path.glob("*.env"):
        if not file.name.startswith('.'):
            env_files.append(file)
    
    if not env_files:
        print(f"No .env files found in {directory}")
        return True
    
    print(f"Found {len(env_files)} .env files:")
    
    for env_file in env_files:
        print(f"\nProcessing {env_file.name}...")
        
        # Extract service name from filename
        service_name = extract_service_name(env_file.name)
        print(f"  Service name: {service_name}")
        
        # Parse the file
        secrets = parse_env_file(env_file)
        if secrets is None:
            print(f"  Skipping {env_file.name} due to read error")
            continue
        
        if not secrets:
            print(f"  No secrets found in {env_file.name}")
            continue
        
        print(f"  Found {len(secrets)} secrets:")
        
        # Store each secret
        for key, value in secrets.items():
            if dry_run:
                print(f"    Would store: {key} -> [SECRET]")
            else:
                try:
                    # Use key as both label and username for identification
                    keyring.set_password(service_name, key, value)
                    print(f"    Stored: {key}")
                except Exception as e:
                    print(f"    Error storing {key}: {e}")
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Ingest secrets from .env files into GNOME Keyring")
    parser.add_argument("directory", nargs="?", default=".", 
                        help="Directory to scan for .env files (default: current directory)")
    parser.add_argument("--dry-run", action="store_true", 
                        help="Show what would be done without actually storing secrets")
    
    args = parser.parse_args()
    
    print("Secret Ingestion Script for kk tool")
    print("=" * 40)
    
    if args.dry_run:
        print("DRY RUN MODE - No secrets will be stored")
        print()
    
    success = ingest_secrets(args.directory, args.dry_run)
    
    if success:
        print("\nIngestion completed.")
        if not args.dry_run:
            print("You can now use 'kk list' to view the stored secrets.")
        return 0
    else:
        print("\nIngestion failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())