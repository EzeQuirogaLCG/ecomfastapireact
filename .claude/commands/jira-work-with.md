---
allowed-tools: Bash(jira-cli work-with:*), Task(*)
description: Work on a specific Jira ticket
---

## Work with Jira Ticket

Generate instructions to work on a specific Jira ticket from the active project.

**Usage:** `/jira-work-with <ticket-id>`

## Command Execution

!`jira-cli work-with $ARGUMENTS`

## Next Steps

Execute the ticket work instructions provided above. Follow the complete prompt including:
- Access the Jira ticket using MCP server tools
- Analyze ticket requirements and acceptance criteria
- Generate detailed implementation guidance
- Provide step-by-step coding instructions
- Include necessary file modifications

## Important Notes

- Ticket must belong to the currently active Jira project
- Use Jira MCP server tools to access ticket details
- Provide complete implementation guidance based on ticket content
- Address all acceptance criteria mentioned in the ticket
