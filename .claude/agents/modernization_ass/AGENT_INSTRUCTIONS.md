# Agent Execution Instructions

## Overview
This e-commerce demo can be enhanced by AI agents using the structured task system. The system provides:

1. **AGENT_TASKS.json** - Structured task definitions
2. **agent_executor.py** - Python script to execute tasks
3. **Validation checks** - Automated testing of results

## Quick Start

### 1. Check Current Status
```bash
# Verify services are running
curl http://localhost:8000/  # Backend
curl http://localhost:3000/  # Frontend
```

### 2. Execute Tasks by Phase
```bash
# Execute specific phase
python3 agent_executor.py --phase phase_1_demo_data

# Execute all phases
python3 agent_executor.py --all

# Validate demo readiness
python3 agent_executor.py --validate
```

## Task Structure

Each task includes:
- **action**: What to do (e.g., "create_sample_products")
- **description**: Human-readable description
- **backend_endpoint**: API endpoint to use
- **frontend_component**: React component to create
- **validation**: How to verify success

## Phase Execution Order

1. **phase_1_demo_data** (Critical) - Add sample data
2. **phase_2_search_system** (High) - Implement search & filtering  
3. **phase_3_wishlist_system** (High) - Add wishlist functionality
4. **phase_4_ui_polish** (Medium) - Improve UI/UX

## Agent-Friendly Features

### ✅ **Structured JSON Format**
- Easy to parse and modify
- Clear task dependencies
- Validation criteria included

### ✅ **Executable Python Script**
- Can be run by any agent
- Built-in error handling
- Progress tracking

### ✅ **Validation System**
- Automated checks after each phase
- Clear success/failure indicators
- Rollback capability

### ✅ **Integration Ready**
- Works with existing FastAPI/React stack
- Uses current API endpoints
- Docker-compatible

## Customization

### Adding New Tasks
1. Edit `AGENT_TASKS.json`
2. Add new task to appropriate phase
3. Implement task logic in `agent_executor.py`
4. Add validation criteria

### Modifying Priorities
1. Change phase order in `AGENT_TASKS.json`
2. Update `agent_executor.py` phase list
3. Re-run validation

## Error Handling

- **Service Check**: Verifies backend/frontend are running
- **Task Validation**: Each task has success criteria
- **Phase Rollback**: Failed phases can be re-executed
- **Progress Tracking**: Shows completion status

## Integration with Existing Tools

- **explorer.py**: Analyzes current state
- **planner.py**: Creates strategic roadmap  
- **agent_executor.py**: Implements the plan
- **Docker**: Runs in containerized environment

## Example Agent Workflow

```bash
# 1. Analyze current state
python3 ./.claude/agents/modernization_ass/explorer.py --repo . --out modernization_artifacts

# 2. Create modernization plan
python3 ./.claude/agents/modernization_ass/planner.py --inventory modernization_artifacts/global/INVENTORY.json --goals FEATURE_PROPOSALS.md

# 3. Execute implementation tasks
python3 agent_executor.py --all

# 4. Validate results
python3 agent_executor.py --validate
```

This system allows any AI agent to systematically enhance the e-commerce demo following a structured, validated approach.
