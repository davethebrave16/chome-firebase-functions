#!/bin/bash

# This script generates a markdown file with the project's directory structure.
# It is a shell-script replacement for a PowerShell script that was causing errors.

echo "Updating directory structure..."

PROJECT_ROOT="."
OUTPUT_DIR=".cursor/knowledge-base"
OUTPUT_FILE="$OUTPUT_DIR/directory_structure.md"

# Create the output directory if it doesn't exist.
mkdir -p "$OUTPUT_DIR"

# Recursive function to generate directory listing.
# Arguments:
#   $1: directory path to list
#   $2: indentation level
list_directory_contents() {
    local path="$1"
    local indent_level="$2"

    # Use find to get immediate children. Sort for consistent order.
    find "$path" -maxdepth 1 -mindepth 1 2>/dev/null | sort | while IFS= read -r entry; do
        local basename
        basename=$(basename "$entry")

        # Skip ignored files and directories.
        case "$basename" in
            .git|.cursor|build|target|dist|bin|node_modules|*.log|*.tmp|*.cache|.env|.DS_Store|.firebaserc|venv|firebase-debug.log|firebase-debug.*.log|__pycache__)
                continue
                ;;
        esac

        local indent_string=""
        # Create indentation string (4 spaces per level).
        for ((i=0; i<indent_level; i++)); do
            indent_string+="    "
        done

        if [ -d "$entry" ]; then
            echo "${indent_string}- **${basename}/**"
            # Recursive call for subdirectories.
            list_directory_contents "$entry" $((indent_level + 1))
        else
            echo "${indent_string}- ${basename}"
        fi
    done
}

# Generate the directory listing.
directory_tree=$(list_directory_contents "$PROJECT_ROOT" 0)

# Generate the final markdown content and write it to the output file.
cat > "$OUTPUT_FILE" << EOF
# Current Directory Structure

## Core Components

\`\`\`
$PROJECT_ROOT
$directory_tree
\`\`\`
EOF

echo "Directory structure updated in $OUTPUT_FILE"
