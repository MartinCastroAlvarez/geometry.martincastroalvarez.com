#!/bin/bash

#
# spy.sh - Secrets Retrieval Script with Caching
#
# This script is designed to securely fetch secrets from S3 buckets created by the
# Secrets Management CDK project. It's intended to be distributed to microservices
# that need to retrieve secrets from the centralized vault.
#
# The script implements intelligent caching - it computes a hash of the profile,
# bucket, and file name combination. If a cached version exists, it returns the
# cached version instead of fetching from S3.
#
# Usage: ./spy.sh <aws_profile> <bucket_name> <file_name>
#
# Parameters:
#   aws_profile  - AWS CLI profile to use for authentication
#   bucket_name  - Name of the S3 bucket containing the secret
#   file_name    - Name of the file/secret to retrieve from the bucket
#
# For Example:
#   ./spy.sh nisman com.nisman.vault prod-config.json
#
# Caching:
#   - Cache location: /tmp/spy-secrets-cache/
#   - Cache key: SHA256 hash of "profile:bucket:file"
#   - Cache files have 600 permissions (owner read/write only)
#   - Cache persists until manually cleared
#
# Exit Codes:
#   0 - Success: Secret retrieved and printed to stdout
#   1 - Parameter error: Missing or invalid arguments
#   2 - AWS CLI error: Profile not configured or authentication failed
#   3 - Bucket error: Bucket doesn't exist or access denied
#   4 - File error: File doesn't exist in bucket
#   5 - Content error: File exists but is empty
#

# Enable strict error handling
set -euo pipefail

# Cache configuration
CACHE_DIR="/tmp/spy-secrets-cache"

# Function to print error messages to stderr and exit
error_exit() {
    local exit_code=$1
    local message=$2
    echo "ERROR: $message" >&2
    exit $exit_code
}

# Function to compute cache key hash from profile, bucket, and file
compute_cache_key() {
    local profile=$1
    local bucket=$2
    local file=$3
    
    # Create a unique hash from the combination of profile, bucket, and file
    echo "${profile}:${bucket}:${file}" | shasum -a 256 | cut -d' ' -f1
}

# Function to ensure cache directory exists and is secure
setup_cache_dir() {
    if [[ ! -d "$CACHE_DIR" ]]; then
        mkdir -p "$CACHE_DIR"
        chmod 700 "$CACHE_DIR"  # Only owner can read/write/execute
    fi
}

# Function to get cache file path for a given cache key
get_cache_file_path() {
    local cache_key=$1
    echo "${CACHE_DIR}/${cache_key}"
}

# Function to check if cache file exists
is_cache_valid() {
    local cache_file=$1
    
    # Check if file exists
    if [[ -f "$cache_file" ]]; then
        return 0  # Cache exists and is valid
    else
        return 1  # Cache doesn't exist
    fi
}

# Function to read secret from cache
read_from_cache() {
    local cache_file=$1
    
    # Read and output cached content
    cat "$cache_file"
}

# Function to write secret to cache
write_to_cache() {
    local cache_file=$1
    local content=$2
    
    # Write content to cache file with secure permissions
    echo "$content" > "$cache_file"
    chmod 600 "$cache_file"  # Only owner can read/write
}

# Function to validate that AWS CLI is installed
check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        error_exit 2 "AWS CLI is not installed or not in PATH"
    fi
}

# Function to validate AWS profile exists and is configured
validate_aws_profile() {
    local profile=$1
    
    # Check if profile exists in AWS config
    if ! aws configure list-profiles 2>/dev/null | grep -q "^${profile}$"; then
        error_exit 2 "AWS profile '${profile}' not found. Run 'aws configure --profile ${profile}' to set it up."
    fi
    
    # Test if profile can authenticate (quick check without making actual calls)
    if ! AWS_PROFILE="$profile" aws sts get-caller-identity &>/dev/null; then
        error_exit 2 "AWS profile '${profile}' authentication failed. Check your credentials."
    fi
}

# Function to check if bucket exists and is accessible
validate_bucket() {
    local profile=$1
    local bucket=$2
    
    # Try to list bucket to verify it exists and we have access
    if ! AWS_PROFILE="$profile" aws s3 ls "s3://${bucket}/" &>/dev/null; then
        error_exit 3 "Bucket '${bucket}' doesn't exist or access denied with profile '${profile}'"
    fi
}

# Function to check if file exists in bucket
validate_file_exists() {
    local profile=$1
    local bucket=$2
    local file=$3
    
    # Check if specific file exists in bucket
    if ! AWS_PROFILE="$profile" aws s3 ls "s3://${bucket}/${file}" &>/dev/null; then
        error_exit 4 "File '${file}' not found in bucket '${bucket}'"
    fi
}

# Function to fetch secret from S3 and validate content
fetch_secret_from_s3() {
    local profile=$1
    local bucket=$2
    local file=$3
    
    # Fetch the file content from S3
    local content
    if ! content=$(AWS_PROFILE="$profile" aws s3 cp "s3://${bucket}/${file}" - 2>/dev/null); then
        error_exit 4 "Failed to download file '${file}' from bucket '${bucket}'"
    fi
    
    # Check if content is empty
    if [[ -z "$content" ]]; then
        error_exit 5 "File '${file}' exists but is empty"
    fi
    
    echo "$content"
}

# Function to fetch secret with caching support
fetch_secret() {
    local profile=$1
    local bucket=$2
    local file=$3
    
    # Setup cache directory
    setup_cache_dir
    
    # Compute cache key
    local cache_key=$(compute_cache_key "$profile" "$bucket" "$file")
    local cache_file=$(get_cache_file_path "$cache_key")
    
    # Check if we have a valid cached version
    if is_cache_valid "$cache_file"; then
        # Read from cache
        read_from_cache "$cache_file"
    else
        # Fetch from S3
        local content=$(fetch_secret_from_s3 "$profile" "$bucket" "$file")
        
        # Store in cache for future use
        write_to_cache "$cache_file" "$content"
        
        # Output content to stdout
        echo "$content"
    fi
}

#
# MAIN SCRIPT EXECUTION
#

# Validate number of arguments
if [[ $# -ne 3 ]]; then
    echo "Usage: $0 <aws_profile> <bucket_name> <file_name>" >&2
    echo "" >&2
    echo "Parameters:" >&2
    echo "  aws_profile  - AWS CLI profile to use for authentication" >&2
    echo "  bucket_name  - Name of the S3 bucket containing the secret" >&2
    echo "  file_name    - Name of the file/secret to retrieve" >&2
    echo "" >&2
    echo "For Example:" >&2
    echo "  $0 nisman com.nisman.vault prod-config.json" >&2
    error_exit 1 "Exactly 3 arguments required, got $#"
fi

# Extract and validate arguments
AWS_PROFILE_ARG="$1"
BUCKET_NAME="$2"
FILE_NAME="$3"

# Validate arguments are not empty
if [[ -z "$AWS_PROFILE_ARG" ]]; then
    error_exit 1 "AWS profile cannot be empty"
fi

if [[ -z "$BUCKET_NAME" ]]; then
    error_exit 1 "Bucket name cannot be empty"
fi

if [[ -z "$FILE_NAME" ]]; then
    error_exit 1 "File name cannot be empty"
fi

# Perform all validations before attempting to fetch
check_aws_cli
validate_aws_profile "$AWS_PROFILE_ARG"
validate_bucket "$AWS_PROFILE_ARG" "$BUCKET_NAME"
validate_file_exists "$AWS_PROFILE_ARG" "$BUCKET_NAME" "$FILE_NAME"

# If all validations pass, fetch and output the secret
fetch_secret "$AWS_PROFILE_ARG" "$BUCKET_NAME" "$FILE_NAME"
