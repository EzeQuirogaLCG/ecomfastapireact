#!/usr/bin/env python3

import json
from pathlib import Path
from typing import Dict, Optional

import click

# Global paths
WORKSPACE_ROOT = Path.cwd()
PROJECT_STATUS_FILE = WORKSPACE_ROOT / '.jira-project-status.json'


def read_json(file_path: Path) -> Optional[Dict]:
    """Read JSON file safely"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def write_json(file_path: Path, data: Dict) -> None:
    """Write JSON file"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)


def get_active_project() -> Optional[str]:
    """Get active Jira project ID"""
    status_data = read_json(PROJECT_STATUS_FILE)
    return status_data.get('project_id') if status_data else None


def set_active_project(project_id: str) -> None:
    """Set active Jira project ID"""
    status_data = read_json(PROJECT_STATUS_FILE) or {}
    status_data['project_id'] = project_id
    if 'processed_plans' not in status_data:
        status_data['processed_plans'] = []
    write_json(PROJECT_STATUS_FILE, status_data)


def get_project_status() -> Dict:
    """Get complete project status"""
    return read_json(PROJECT_STATUS_FILE) or {}


def is_plan_processed(plan_file: str) -> bool:
    """Check if a plan file has been processed"""
    status_data = get_project_status()
    processed_plans = status_data.get('processed_plans', [])
    return any(plan.get('plan_file') == plan_file for plan in processed_plans)


def get_plan_status(plan_file: str) -> str:
    """Get processing status of a plan file (COMPLETED, PARTIAL, or None)"""
    status_data = get_project_status()
    processed_plans = status_data.get('processed_plans', [])
    for plan in processed_plans:
        if plan.get('plan_file') == plan_file:
            return plan.get('processed_status', 'UNKNOWN')
    return None


def get_plan_tickets(plan_file: str) -> list:
    """Get task mappings for a specific plan file"""
    status_data = get_project_status()
    processed_plans = status_data.get('processed_plans', [])
    for plan in processed_plans:
        if plan.get('plan_file') == plan_file:
            return plan.get('task_mappings', [])
    return []


def get_plan_data(plan_file: str) -> dict:
    """Get complete plan data for a specific plan file"""
    status_data = get_project_status()
    processed_plans = status_data.get('processed_plans', [])
    for plan in processed_plans:
        if plan.get('plan_file') == plan_file:
            return plan
    return {}


def record_plan_processing(plan_file: str, task_mappings: list, summary: dict = None, processed_status: str = "COMPLETED") -> None:
    """Record that a plan file has been processed with task mappings"""
    status_data = get_project_status()
    if 'processed_plans' not in status_data:
        status_data['processed_plans'] = []

    from datetime import datetime

    # Check if plan already exists and update it, or add new one
    plan_exists = False
    for i, plan in enumerate(status_data['processed_plans']):
        if plan.get('plan_file') == plan_file:
            # Merge with existing tickets if status is PARTIAL
            if processed_status == "PARTIAL" and plan.get('processed_status') == "PARTIAL":
                existing_tickets = plan.get('task_mappings', [])
                existing_titles = {ticket.get('title')
                                   for ticket in existing_tickets}

                # Add only new tickets
                new_tickets = [ticket for ticket in task_mappings if ticket.get(
                    'title') not in existing_titles]
                all_tickets = existing_tickets + new_tickets

                # Update summary
                updated_summary = plan.get('summary', {})
                if summary:
                    for key, value in summary.items():
                        updated_summary[key] = updated_summary.get(
                            key, 0) + value

                status_data['processed_plans'][i] = {
                    'plan_file': plan_file,
                    'processed_date': datetime.utcnow().isoformat().split('T')[0],
                    'processed_status': processed_status,
                    'task_mappings': all_tickets,
                    'summary': updated_summary
                }
            else:
                # Replace completely for COMPLETED status
                status_data['processed_plans'][i] = {
                    'plan_file': plan_file,
                    'processed_date': datetime.utcnow().isoformat().split('T')[0],
                    'processed_status': processed_status,
                    'task_mappings': task_mappings,
                    'summary': summary or {}
                }
            plan_exists = True
            break

    if not plan_exists:
        status_data['processed_plans'].append({
            'plan_file': plan_file,
            'processed_date': datetime.utcnow().isoformat().split('T')[0],
            'processed_status': processed_status,
            'task_mappings': task_mappings,
            'summary': summary or {}
        })

    write_json(PROJECT_STATUS_FILE, status_data)


def validate_project_set(ctx) -> bool:
    """Validate that a Jira project is set"""
    project_id = get_active_project()

    if not project_id:
        guidance_msg = """NO JIRA PROJECT SET

The user tried to use a Jira command but no project is currently active.

HELP THE USER BY:
1. Explaining they need to set a Jira project first
2. Asking which Jira project they want to work with

TELL THE USER TO RUN:
  /jira-set-project <project-id>

EXAMPLE SUGGESTIONS:
- /jira-set-project PROJ-123
- /jira-set-project MYPROJECT
- /jira-set-project WEB-DEV

GUIDANCE FOR USER:
- Project ID is the key/identifier of your Jira project
- This is required before using any other Jira commands
- You can find the project ID in your Jira project URL or settings"""

        print("🤖 AI GUIDANCE MODE")
        print("")
        print(guidance_msg)
        print("")
        print("Please set a Jira project first and try again.")
        return False

    return True


def handle_error_or_guidance(ctx, error_message: str, guidance_message: str, exit_code: int = 1):
    """Handle errors with AI guidance mode"""
    print("🤖 AI GUIDANCE MODE")
    print("")
    print(guidance_message)
    print("")
    print("Please fix the issue above and try again.")
    return False


@click.group()
@click.pass_context
def cli(ctx):
    """Jira Ticket Management CLI"""
    # Always use AI guidance mode for Claude Code integration
    ctx.ensure_object(dict)
    ctx.obj['ai_guidance'] = True


@cli.command('set-project')
@click.argument('project_id')
@click.pass_context
def set_project(ctx, project_id: str):
    """Set active Jira project ID"""

    if not project_id:
        error_msg = "Project ID is required"
        guidance_msg = """MISSING PROJECT ID

The user tried to set a Jira project but didn't provide a project ID.

HELP THE USER BY:
1. Explaining they need to provide a Jira project ID
2. Asking which project they want to work with

SUGGESTED FORMAT FOR USER:
  /jira-set-project <project-id>

EXAMPLE SUGGESTIONS:
- /jira-set-project PROJ-123
- /jira-set-project MYPROJECT
- /jira-set-project WEB-DEV

GUIDANCE FOR USER:
- Project ID is the key/identifier of your Jira project
- You can find it in your Jira project URL or settings
- This will be used for all subsequent Jira operations"""

        return handle_error_or_guidance(ctx, error_msg, guidance_msg)

    set_active_project(project_id)
    print(f"Set active Jira project: {project_id}")
    print("You can now use other Jira commands with this project context")


@cli.command('work-with')
@click.argument('ticket_id')
@click.pass_context
def work_with(ctx, ticket_id: str):
    """Generate prompt to work with a specific Jira ticket"""

    if not validate_project_set(ctx):
        return

    project_id = get_active_project()

    # The ticket_id argument is always provided by Click, so no need to check for its presence.

    # Generate work-with prompt
    prompt = build_work_with_prompt(project_id, ticket_id)
    print(prompt)


@cli.command('my-tickets')
@click.pass_context
def my_tickets(ctx):
    """Generate prompt to list user's assigned tickets"""

    if not validate_project_set(ctx):
        return

    project_id = get_active_project()

    # Generate my-tickets prompt
    prompt = build_my_tickets_prompt(project_id)
    print(prompt)


@cli.command('create-tickets-from-plan')
@click.argument('plan_file')
@click.pass_context
def create_tickets_from_plan(ctx, plan_file: str):
    """Generate prompt to create tickets from a plan file"""

    if not validate_project_set(ctx):
        return

    project_id = get_active_project()

    # Check if plan file exists
    plan_path = WORKSPACE_ROOT / plan_file
    if not plan_path.exists():
        error_msg = f"Plan file not found: {plan_file}"
        guidance_msg = f"""PLAN FILE NOT FOUND

The user tried to create tickets from plan file "{plan_file}" but the file doesn't exist.

FILE LOCATION CHECKED:
- {plan_path}
- File must be in the project root directory

HELP THE USER BY:
1. Explaining the file doesn't exist at the expected location
2. Asking them to check the file path or create the file

REQUIRED FILE LOCATION:
- The plan file must be in the project root directory
- Use relative path from project root (e.g., "plan.md", "roadmap.md")

SUGGESTED ACTIONS:
- Check if the file exists in the project root
- Create the plan file if it doesn't exist
- Use the correct relative path from project root

PLAN FILE FORMAT:
The plan file should be a Markdown file containing:
- Epics (high-level features)
- User Stories (specific requirements)
- Tasks (implementation details)
- Any other work items to be converted to Jira tickets"""

        return handle_error_or_guidance(ctx, error_msg, guidance_msg)

    # Check if plan has already been processed
    if is_plan_processed(plan_file):
        plan_status = get_plan_status(plan_file)
        existing_tickets = get_plan_tickets(plan_file)

        print("🤖 AI GUIDANCE MODE")
        print("")

        if plan_status == "COMPLETED":
            print("PLAN ALREADY COMPLETED")
            print("")
            print(
                f"The plan file '{plan_file}' has been completely processed.")
            print(f"Status: {plan_status}")
            print(
                f"Found {len(existing_tickets)} tickets created from this plan:")
            print("")

            for ticket in existing_tickets:
                jira_key = ticket.get('jira_key', 'N/A')
                title = ticket.get('title', 'No title')
                ticket_type = ticket.get('ticket_type', 'Unknown')
                print(f"  • {jira_key}: {title} ({ticket_type})")

            print("")
            print("This plan is marked as COMPLETED and cannot be reprocessed.")
            print("If you need to modify this plan:")
            print(
                "1. Change the processed_status to 'PARTIAL' in .jira-project-status.json")
            print("2. Or delete the plan entry and reprocess")
            print("")
            return

        elif plan_status == "PARTIAL":
            print("PLAN PARTIALLY PROCESSED")
            print("")
            print(f"The plan file '{plan_file}' has been partially processed.")
            print(f"Status: {plan_status}")
            print(f"Found {len(existing_tickets)} tickets already created:")
            print("")

            for ticket in existing_tickets:
                jira_key = ticket.get('jira_key', 'N/A')
                title = ticket.get('title', 'No title')
                ticket_type = ticket.get('ticket_type', 'Unknown')
                print(f"  • {jira_key}: {title} ({ticket_type})")

            print("")
            print("This plan can be continued to create remaining tickets.")
            print("Only new tickets will be created (existing ones will be skipped).")
            print("")
            print("Continuing with partial processing...")
            print("")
        else:
            print("PLAN PROCESSING STATUS UNKNOWN")
            print("")
            print(
                f"The plan file '{plan_file}' has been processed but status is unknown.")
            print("Proceeding with full processing...")
            print("")

    # Generate create-tickets prompt
    prompt = build_create_tickets_prompt(project_id, plan_file, plan_path)
    print(prompt)


def build_work_with_prompt(project_id: str, ticket_id: str) -> str:
    """Build prompt for working with a specific Jira ticket"""

    prompt_parts = [
        "JIRA TICKET WORK SESSION",
        f"Project: {project_id}",
        f"Ticket: {ticket_id}",
        "",
        "TASK: Work on the specified Jira ticket",
        "",
        "INSTRUCTIONS:",
        "1. Use the Jira MCP server to access the ticket details",
        f"2. Read ticket {ticket_id} from project {project_id}",
        "3. Analyze the ticket description, acceptance criteria, and requirements",
        "4. Generate detailed implementation instructions based on the ticket content",
        "5. Provide step-by-step coding guidance",
        "6. Include any necessary file modifications or new files to create",
        "",
        "CRITICAL REQUIREMENTS:",
        f"- Ticket must belong to project {project_id}",
        "- Only work on tickets from the active project",
        "- Provide complete implementation guidance",
        "- Include code examples and file structures",
        "- Address all acceptance criteria mentioned in the ticket",
        "",
        "WORKFLOW:",
        "1. Access Jira and read the ticket details",
        "2. Analyze requirements and acceptance criteria",
        "3. Generate implementation plan",
        "4. Provide detailed coding instructions",
        "5. Include file modifications needed",
        "",
        "Use the Jira MCP server tools to access ticket information and work accordingly."
    ]

    return "\n".join(prompt_parts)


def build_my_tickets_prompt(project_id: str) -> str:
    """Build prompt for listing user's assigned tickets"""

    prompt_parts = [
        "JIRA MY TICKETS",
        f"Project: {project_id}",
        "",
        "TASK: List and analyze user's assigned tickets",
        "",
        "INSTRUCTIONS:",
        "1. Use the Jira MCP server to access assigned tickets",
        f"2. Search for tickets assigned to the current user in project {project_id}",
        "3. Display ticket information in an organized format",
        "4. Show ticket status, priority, and key details",
        "5. Provide summary of work load and priorities",
        "",
        "CRITICAL REQUIREMENTS:",
        f"- Only show tickets from project {project_id}",
        "- Only show tickets assigned to the current user",
        "- Display tickets in a clear, organized format",
        "- Include ticket status and priority information",
        "",
        "OUTPUT FORMAT:",
        "- List each ticket with key information",
        "- Group by status (To Do, In Progress, Done, etc.)",
        "- Show priority levels",
        "- Include brief descriptions",
        "- Provide summary of work load",
        "",
        "Use the Jira MCP server tools to access ticket information and display accordingly."
    ]

    return "\n".join(prompt_parts)


def build_create_tickets_prompt(project_id: str, plan_file: str, plan_path: Path) -> str:
    """Build prompt for creating tickets from a plan file"""

    prompt_parts = [
        "JIRA CREATE TICKETS FROM PLAN",
        f"Project: {project_id}",
        f"Plan File: {plan_file}",
        f"Plan Path: {plan_path}",
        "",
        "TASK: Create Jira tickets from the plan file",
        "",
        "INSTRUCTIONS:",
        "1. Read and analyze the plan file content",
        f"2. Extract Epics, User Stories, Tasks, and other work items from {plan_file}",
        "3. Use the Jira MCP server to create tickets for each item",
        f"4. Create all tickets in project {project_id}",
        "5. Set appropriate ticket types (Epic, Story, Task, etc.)",
        "6. Include descriptions and acceptance criteria from the plan",
        "7. IMPORTANT: Record all created tickets for tracking",
        "",
        "CRITICAL REQUIREMENTS:",
        f"- All tickets must be created in project {project_id}",
        "- Preserve the hierarchical structure from the plan (Epics → Stories → Tasks)",
        "- Include all relevant information from the plan file",
        "- Set appropriate ticket types and priorities",
        "- Link related tickets (Stories to Epics, Tasks to Stories)",
        "- Track all created tickets to prevent reprocessing",
        "",
        "WORKFLOW:",
        "1. Read the plan file content",
        "2. Parse and structure the work items",
        "3. Create Epic tickets first",
        "4. Create User Story tickets and link to Epics",
        "5. Create Task tickets and link to Stories",
        "6. Set appropriate fields and descriptions",
        "7. Record all created tickets with their details",
        "",
        "CRITICAL: SAVE PROCESS RESULTS",
        "After creating all tickets, you MUST save the results to prevent reprocessing:",
        "",
        "1. Collect all created ticket information in this exact format:",
        '{"task_mappings": [{"title": "Task Title", "jira_key": "PROJ-123", "ticket_type": "Epic", "story_points": 8, "priority": "High", "status": "created"}], "summary": {"epics": 1, "stories": 0, "tasks": 0, "total_story_points": 8}}',
        "",
        "2. Save using: jira-cli save-process-data <plan-file> \"<json-data>\"",
        "",
        "EXAMPLE COMMAND:",
        'jira-cli save-process-data modernization-statement/MODERNIZATION_PLAN.md \'{"task_mappings": [...], "summary": {...}}\'',
        "",
        "PLAN FILE ANALYSIS:",
        f"Read the file at: {plan_path}",
        "Extract all work items and their relationships",
        "Convert each item to appropriate Jira ticket type",
        "",
        "Use the Jira MCP server tools to create tickets and the file system tools to read the plan file.",
        "IMPORTANT: After creating all tickets, use the 'jira-cli save-process-data' command to prevent duplicates."
    ]

    return "\n".join(prompt_parts)


@cli.command('status')
def status():
    """Show current Jira project status"""
    project_id = get_active_project()

    if not project_id:
        print("No active Jira project set")
        print("Run 'jira-cli set-project <project-id>' to set a project")
        return

    print(f"Active Jira Project: {project_id}")
    print("Available commands:")
    print("- /jira-work-with <ticket-id> - Work on a specific ticket")
    print("- /jira-my-tickets - List your assigned tickets")
    print("- /jira-create-tickets-from-plan <plan-file> - Create tickets from plan")
    print("- /jira-save-process-data <plan-file> <json-data> - Save process results")
    print("- /jira-plan-status - Show processed plans status")


@cli.command('save-process-data')
@click.argument('plan_file')
@click.argument('process_data')
@click.pass_context
def save_process_data(ctx, plan_file: str, process_data: str):
    """Save process data for a plan file"""

    if not validate_project_set(ctx):
        return

    try:
        import json
        data = json.loads(process_data)
        task_mappings = data.get('task_mappings', [])
        summary = data.get('summary', {})
        processed_status = data.get('processed_status', 'COMPLETED')

        # Convert old dict format to new list format if needed
        if isinstance(task_mappings, dict):
            task_mappings = [{"title": title, **info}
                             for title, info in task_mappings.items()]

        record_plan_processing(plan_file, task_mappings,
                               summary, processed_status)
        print(f"✅ Process data saved for plan: {plan_file}")
        print(f"   Status: {processed_status}")
        print(f"   Tickets recorded: {len(task_mappings)}")

        if summary:
            print(
                f"   Summary: {summary.get('epics', 0)} Epics, {summary.get('stories', 0)} Stories, {summary.get('tasks', 0)} Tasks")

    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON data - {e}")
        return
    except Exception as e:
        print(f"❌ Error saving process data: {e}")
        return


@cli.command('plan-status')
def plan_status():
    """Show status of processed plan files"""
    project_id = get_active_project()

    if not project_id:
        print("No active Jira project set")
        print("Run 'jira-cli set-project <project-id>' to set a project")
        return

    status_data = get_project_status()
    processed_plans = status_data.get('processed_plans', [])

    if not processed_plans:
        print("No plan files have been processed yet.")
        print("Use 'jira-cli create-tickets-from-plan <plan-file>' to process a plan.")
        return

    print(f"Processed Plans for Project: {project_id}")
    print("=" * 50)

    for plan_data in processed_plans:
        plan_file = plan_data.get('plan_file', 'Unknown')
        processed_date = plan_data.get('processed_date', 'Unknown')
        processed_status = plan_data.get('processed_status', 'UNKNOWN')
        task_mappings = plan_data.get('task_mappings', [])
        summary = plan_data.get('summary', {})

        print(f"\n📄 Plan: {plan_file}")
        print(f"   Processed: {processed_date}")
        print(f"   Status: {processed_status}")
        print(f"   Tickets Created: {len(task_mappings)}")

        if summary:
            print(
                f"   Summary: {summary.get('epics', 0)} Epics, {summary.get('stories', 0)} Stories, {summary.get('tasks', 0)} Tasks")
            print(
                f"   Total Story Points: {summary.get('total_story_points', 0)}")

        if task_mappings:
            print("   Created Tickets:")
            for ticket in task_mappings:
                jira_key = ticket.get('jira_key', 'N/A')
                title = ticket.get('title', 'No title')
                ticket_type = ticket.get('ticket_type', 'Unknown')
                story_points = ticket.get('story_points', '')
                points_str = f" ({story_points}pts)" if story_points else ""
                print(
                    f"     • {jira_key}: {title} ({ticket_type}){points_str}")

    print(f"\nTotal Plans Processed: {len(processed_plans)}")
    total_tickets = sum(len(plan_data.get('task_mappings', []))
                        for plan_data in processed_plans)
    print(f"Total Tickets Created: {total_tickets}")


def main():
    """Entry point for console script"""
    cli()


if __name__ == '__main__':
    main()
