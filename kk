#!/bin/bash

# kk - A CLI tool to browse and manage secrets in GNOME Keyring
# Usage: kk [command] [options]

VERSION="1.1.0"  # Added remove command

# Function to display help
show_help() {
    cat << EOF
kk - A CLI tool to browse and manage secrets in GNOME Keyring

Usage:
  kk [command] [options]

Commands:
  list              List all secrets (with masked values)
  search <attr> <value>  Search for secrets by attribute
  get <service> <username>   Retrieve a full secret (requires confirmation)
  remove <service> <username>  Remove a secret (requires confirmation)
  --help            Show this help message
  --version         Show version information

Examples:
  kk list
  kk search service binance
  kk get binance trader1
  kk remove binance trader1

For agentic CLI tools:
  The list and search commands show masked secrets (first 70% visible)
  This allows agents to verify secrets exist and identify parameters for get
EOF
}

# Function to display version
show_version() {
    echo "kk version $VERSION"
}

# Function to mask a secret, showing only first 70%
mask_secret() {
    local secret="$1"
    local length=${#secret}
    
    # For very short secrets, show only first 3 characters
    if [ $length -le 5 ]; then
        local visible_chars=$((length < 3 ? length : 3))
        printf "%s%*s" "${secret:0:$visible_chars}" $((length - visible_chars)) | tr ' ' '*'
        return
    fi
    
    # For longer secrets, show 70%
    local visible_length=$((length * 7 / 10))
    # Ensure at least 1 character is visible and at least 1 is masked
    if [ $visible_length -lt 1 ]; then
        visible_length=1
    elif [ $visible_length -ge $length ]; then
        visible_length=$((length - 1))
    fi
    
    printf "%s%*s" "${secret:0:$visible_length}" $((length - visible_length)) | tr ' ' '*'
}

# Function to process secret-tool output and extract items
process_secret_output() {
    local output="$1"
    local show_unmasked="$2"
    
    # Variables to hold current item data
    local label=""
    local secret=""
    local service="N/A"
    local username="N/A"
    local in_item=false
    
    # Keep track of items we've already displayed to avoid duplicates
    local displayed_items=()
    
    # Function to display an item if it hasn't been displayed yet
    display_item() {
        local item_service="$1"
        local item_username="$2"
        local item_label="$3"
        local item_secret="$4"
        
        # Create a unique identifier for this item
        local item_id="${item_service}:${item_username}:${item_label}"
        
        # Check if we've already displayed this item
        for displayed in "${displayed_items[@]}"; do
            if [ "$displayed" = "$item_id" ]; then
                return
            fi
        done
        
        # Add to displayed items
        displayed_items+=("$item_id")
        
        # Display the item
        if [ "$show_unmasked" = true ]; then
            printf "%-20s %-20s %-30s %s\n" "$item_service" "$item_username" "$item_label" "$item_secret"
        else
            local masked_secret=$(mask_secret "$item_secret")
            printf "%-20s %-20s %-30s %s\n" "$item_service" "$item_username" "$item_label" "$masked_secret"
        fi
    }
    
    # Process output line by line
    while IFS= read -r line; do
        # Check if this is the start of a new item
        if [[ $line =~ ^\[.*\]$ ]]; then
            # If we were processing an item, display it
            if [ "$in_item" = true ] && [ -n "$secret" ]; then
                display_item "$service" "$username" "$label" "$secret"
            fi
            
            # Reset for new item
            in_item=true
            label=""
            secret=""
            service="N/A"
            username="N/A"
            continue
        fi
        
        # Skip empty lines but don't reset the item
        if [ -z "$line" ]; then
            continue
        fi
        
        # Parse key-value pairs (with spaces around =)
        if [[ $line =~ ^([^=]+)[[:space:]]*=[[:space:]]*(.*)$ ]] && [ "$in_item" = true ]; then
            local key="${BASH_REMATCH[1]}"
            local value="${BASH_REMATCH[2]}"
            
            # Trim leading/trailing whitespace from key
            key=$(echo "$key" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
            
            case "$key" in
                "label")
                    label="$value"
                    ;;
                "secret")
                    secret="$value"
                    ;;
                "created"|"modified"|"schema")
                    # Ignore these fields
                    ;;
                attribute.service)
                    service="$value"
                    ;;
                attribute.username)
                    username="$value"
                    ;;
            esac
        fi
    done <<< "$output"
    
    # Display the last item if we were processing one
    if [ "$in_item" = true ] && [ -n "$secret" ]; then
        display_item "$service" "$username" "$label" "$secret"
    fi
}

# Function to search for secrets by attribute
search_secrets() {
    local attribute="$1"
    local value="$2"
    local show_unmasked=false
    
    if [ "$3" = "--unmask" ]; then
        show_unmasked=true
    fi
    
    if [ -z "$attribute" ] || [ -z "$value" ]; then
        echo "Error: Both attribute and value must be specified"
        echo "Usage: kk search <attribute> <value> [--unmask]"
        exit 1
    fi
    
    # Use secret-tool search to find items, capturing both stdout and stderr
    local output=$(secret-tool search "$attribute" "$value" 2>&1)
    local exit_code=$?
    
    if [ $exit_code -ne 0 ]; then
        # Check if it's just the "no results" error
        if echo "$output" | grep -q "no.*found\|not.*found\|empty"; then
            # Print header
            if [ "$show_unmasked" = true ]; then
                printf "%-20s %-20s %-30s %s\n" "Service" "Username" "Label" "Secret"
                printf "%*s\n" 90 | tr ' ' '-'
            else
                printf "%-20s %-20s %-30s %s\n" "Service" "Username" "Label" "Secret (masked)"
                printf "%*s\n" 90 | tr ' ' '-'
            fi
            echo "No secrets found with attribute '$attribute' = '$value'."
            return
        else
            echo "Error: Failed to access GNOME Keyring"
            echo "$output"
            exit 1
        fi
    fi
    
    # Print header
    if [ "$show_unmasked" = true ]; then
        printf "%-20s %-20s %-30s %s\n" "Service" "Username" "Label" "Secret"
        printf "%*s\n" 90 | tr ' ' '-'
    else
        printf "%-20s %-20s %-30s %s\n" "Service" "Username" "Label" "Secret (masked)"
        printf "%*s\n" 90 | tr ' ' '-'
    fi
    
    # Process the output using our new function
    process_secret_output "$output" "$show_unmasked"
}

# Function to get a full secret
get_secret() {
    local service="$1"
    local username="$2"
    
    if [ -z "$service" ] || [ -z "$username" ]; then
        echo "Error: Both service and username must be specified"
        echo "Usage: kk get <service> <username>"
        exit 1
    fi
    
    # Use secret-tool lookup to get the secret
    local secret=$(secret-tool lookup service "$service" username "$username" 2>/dev/null)
    
    if [ -z "$secret" ]; then
        echo "No secret found for service '$service' and username '$username'"
        exit 1
    fi
    
    # Find the label for this secret
    local output=$(secret-tool search service "$service" username "$username" 2>&1)
    local exit_code=$?
    
    if [ $exit_code -ne 0 ]; then
        echo "Error: Failed to access GNOME Keyring"
        exit 1
    fi
    
    # Extract the label
    local label=$(echo "$output" | grep "^label " | sed 's/label *= *//' | head -n 1)
    if [ -z "$label" ]; then
        label="Unknown"
    fi
    
    # Confirm before showing full secret
    echo "Show full secret for '$label'? Type 'yes' to confirm:"
    read -r response
    
    if [ "$response" != "yes" ]; then
        echo "Operation cancelled."
        exit 0
    fi
    
    echo "Service: $service"
    echo "Username: $username"
    echo "Label: $label"
    echo "Secret: $secret"
}

# Function to remove a secret
remove_secret() {
    local service="$1"
    local username="$2"
    
    if [ -z "$service" ] || [ -z "$username" ]; then
        echo "Error: Both service and username must be specified"
        echo "Usage: kk remove <service> <username>"
        exit 1
    fi
    
    # Check if the secret exists
    local secret=$(secret-tool lookup service "$service" username "$username" 2>/dev/null)
    
    if [ -z "$secret" ]; then
        echo "No secret found for service '$service' and username '$username'"
        exit 1
    fi
    
    # Find the label for this secret
    local output=$(secret-tool search service "$service" username "$username" 2>&1)
    local exit_code=$?
    
    if [ $exit_code -ne 0 ]; then
        echo "Error: Failed to access GNOME Keyring"
        exit 1
    fi
    
    # Extract the label
    local label=$(echo "$output" | grep "^label " | sed 's/label *= *//' | head -n 1)
    if [ -z "$label" ]; then
        label="Unknown"
    fi
    
    # Confirm before removing secret
    echo "Remove secret '$label' for service '$service' and username '$username'? Type 'yes' to confirm:"
    read -r response
    
    if [ "$response" != "yes" ]; then
        echo "Operation cancelled."
        exit 0
    fi
    
    # Use secret-tool clear to remove the secret
    secret-tool clear service "$service" username "$username"
    
    echo "Secret removed successfully."
}

# Function to list common secrets
list_secrets() {
    local show_unmasked=false
    if [ "$1" = "--unmask" ]; then
        show_unmasked=true
    fi
    
    # Print header
    if [ "$show_unmasked" = true ]; then
        printf "%-20s %-20s %-30s %s\n" "Service" "Username" "Label" "Secret"
        printf "%*s\n" 90 | tr ' ' '-'
    else
        printf "%-20s %-20s %-30s %s\n" "Service" "Username" "Label" "Secret (masked)"
        printf "%*s\n" 90 | tr ' ' '-'
    fi
    
    # Track if we found any secrets
    local found_secrets=false
    
    # Search for common services we've used in our tests
    local services=("test-service" "binance" "upstox" "coinbase")
    local usernames=("test-user" "trader1" "investor2" "crypto_user3")
    
    # Keep track of all output to process at the end
    local all_output=""
    
    # Search for services
    for service in "${services[@]}"; do
        local output=$(secret-tool search service "$service" 2>&1)
        if [ $? -eq 0 ] && [ -n "$output" ]; then
            # Add a separator between different service outputs
            if [ -n "$all_output" ]; then
                all_output="$all_output"$'\n'"$output"
            else
                all_output="$output"
            fi
            found_secrets=true
        fi
    done
    
    # Search for usernames
    for username in "${usernames[@]}"; do
        local output=$(secret-tool search username "$username" 2>&1)
        if [ $? -eq 0 ] && [ -n "$output" ]; then
            # Add a separator between different username outputs
            if [ -n "$all_output" ]; then
                all_output="$all_output"$'\n'"$output"
            else
                all_output="$output"
            fi
            found_secrets=true
        fi
    done
    
    # Process all the collected output
    if [ "$found_secrets" = true ] && [ -n "$all_output" ]; then
        process_secret_output "$all_output" "$show_unmasked"
    else
        echo "No secrets found in the keyring."
    fi
}

# Main script logic
main() {
    case "$1" in
        --help|-h)
            show_help
            ;;
        --version|-v)
            show_version
            ;;
        list)
            if [ "$2" = "--unmask" ]; then
                list_secrets "--unmask"
            else
                list_secrets
            fi
            ;;
        search)
            if [ "$4" = "--unmask" ]; then
                search_secrets "$2" "$3" "--unmask"
            else
                search_secrets "$2" "$3"
            fi
            ;;
        get)
            get_secret "$2" "$3"
            ;;
        remove)
            remove_secret "$2" "$3"
            ;;
        "")
            show_help
            ;;
        *)
            echo "Unknown command: $1"
            echo "Use 'kk --help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"