# Jira Ticket Management CLI

A CLI tool for managing Jira tickets integrated with Claude Code through slash commands.

## Installation

### DevContainer (Automatic)

The CLI is automatically installed when the DevContainer is first configured.

### Manual Installation

```bash
# Create a temporary copy to avoid permission issues
cp -r /workspaces/old-school-travel/jira-cli /tmp/jira-cli-temp
cd /tmp/jira-cli-temp
python3 -m pip install .
rm -rf /tmp/jira-cli-temp
```

### Updating after code changes

If you modify the CLI code and need the new version **without restarting the container**:

```bash
# Option 1: Use the update script (recommended)
./update-jira-cli.sh

# Option 2: Manual reinstall from temporary directory
cp -r /workspaces/old-school-travel/jira-cli /tmp/jira-cli-temp
cd /tmp/jira-cli-temp
python3 -m pip install . --force-reinstall
rm -rf /tmp/jira-cli-temp

# Option 3: Reinstall directly (if no permission issues)
cd /workspaces/old-school-travel/jira-cli
python3 -m pip install . --force-reinstall
```

**Note**: The update script (Option 1) is the easiest way and avoids permission issues between WSL and the container.

## Available Commands

### 1. `/jira-set-project <project-id>`

Sets the active Jira project. **REQUIRED** for all other commands.

```bash
# Example
/jira-set-project PROJ-123
```

### 2. `/jira-work-with <ticket-id>`

Generates instructions to work on a specific ticket from the active project.

```bash
# Example
/jira-work-with PROJ-456
```

### 3. `/jira-my-tickets`

Lists all tickets assigned to the user in the active project.

```bash
# Example
/jira-my-tickets
```

### 4. `/jira-create-tickets-from-plan <plan-file>`

Creates Jira tickets from a Markdown plan file.

```bash
# Example
/jira-create-tickets-from-plan project-plan.md
```

### 5. `/jira-status`

Shows the current status of the active Jira project.

```bash
# Example
/jira-status
```

## Features

- **Project Validation**: All commands verify that there's an active project
- **AI Guidance Mode**: Provides helpful guidance instead of failing
- **MCP Integration**: Uses the existing Jira MCP server
- **Dynamic Prompts**: Generates specific instructions for each task
- **File Validation**: Verifies that plan files exist

## State Files

- `.jira-active-project.json`: Stores the active Jira project
- Plan files must be in the project root directory

## Workflow

1. **Set up project**: `/jira-set-project <project-id>`
2. **View assigned tickets**: `/jira-my-tickets`
3. **Work on ticket**: `/jira-work-with <ticket-id>`
4. **Create tickets from plan**: `/jira-create-tickets-from-plan <plan-file>`

## Requirements

- Python 3.8+
- Click 8.0.0+
- Jira MCP server configured
- Claude Code with slash commands enabled
