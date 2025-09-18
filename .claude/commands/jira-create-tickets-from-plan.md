---
allowed-tools: Bash(jira-cli create-tickets-from-plan:*), Bash(jira-cli save-process-data:*), Task(*)
description: Create Jira tickets from a plan file
---

## Create Tickets from Plan

Generate instructions to create Jira tickets from a Markdown plan file.

**Usage:** `/jira-create-tickets-from-plan <plan-file>`

## Command Execution

!`jira-cli create-tickets-from-plan $ARGUMENTS`

## Next Steps

Execute the ticket creation instructions provided above. Follow the complete prompt including:

- Read and analyze the plan file content
- Extract Epics, User Stories, Tasks, and other work items
- Use Jira MCP server to create tickets for each item
- Preserve hierarchical structure (Epics → Stories → Tasks)
- Link related tickets appropriately

## CRITICAL: Save Process Results

After creating all tickets, you MUST save the process results to prevent duplicate processing:

1. **Collect all created ticket information** in this format:

```json
{
  "task_mappings": [
    {
      "title": "Task Title 1",
      "jira_key": "PROJ-123",
      "ticket_type": "Epic",
      "story_points": 8,
      "priority": "High",
      "status": "created"
    },
    {
      "title": "Task Title 2",
      "jira_key": "PROJ-124",
      "ticket_type": "Story",
      "story_points": 5,
      "priority": "Medium",
      "status": "created"
    }
  ],
  "summary": {
    "epics": 1,
    "stories": 1,
    "tasks": 0,
    "total_story_points": 13
  },
  "processed_status": "COMPLETED"
}
```

**Status Values:**

- `"COMPLETED"`: All tickets from the plan have been created
- `"PARTIAL"`: Only some tickets were created, more can be added later

2. **Save the results** using the bash tool calling:
   `jira-cli save-process-data $PLAN_FILE "$JSON_DATA"`

## Important Notes

- Plan file must be in the project root directory
- All tickets will be created in the active Jira project
- Preserves hierarchical structure from the plan
- Sets appropriate ticket types and priorities
- Links related tickets (Stories to Epics, Tasks to Stories)
- **MUST save process results to prevent reprocessing**

## Plan File Format

The plan file should be a Markdown file containing:

- Epics (high-level features)
- User Stories (specific requirements)
- Tasks (implementation details)
- Any other work items to be converted to Jira tickets
