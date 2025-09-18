#!/bin/bash

# Update Jira CLI script
# This script reinstalls the Jira CLI after code changes without restarting the container

echo "Updating Jira CLI..."

# Create a temporary copy to avoid permission issues
cp -r /workspaces/old-school-travel/jira-cli /tmp/jira-cli-temp
cd /tmp/jira-cli-temp

# Reinstall the package
python3 -m pip install . --force-reinstall

# Clean up temporary directory
rm -rf /tmp/jira-cli-temp

echo "Jira CLI updated successfully!"
