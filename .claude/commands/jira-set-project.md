---
allowed-tools: Bash(jira-cli set-project:*)
description: Set active Jira project for ticket management
---

## Set Jira Project

Set the active Jira project for all subsequent ticket management operations.

**Usage:** `/jira-set-project <project-id>`

## Command Execution

!`jira-cli set-project $ARGUMENTS`

## Next Steps

The active Jira project has been set. You can now:
- Use `/jira-work-with <ticket-id>` to work on specific tickets
- Use `/jira-my-tickets` to list your assigned tickets
- Use `/jira-create-tickets-from-plan <plan-file>` to create tickets from plans
- Use `/jira-status` to check current project status

## Important Notes

- Project ID is required for all other Jira commands
- Only tickets from the active project will be accessible
- You can change the active project anytime by running this command again
