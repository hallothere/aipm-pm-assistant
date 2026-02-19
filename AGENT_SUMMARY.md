# PM Assistant (LangGraph) — Workflow Summary & Improvements

## Workflow summary (high level)
1. `main.py`: Creates initial state (`project_description`, `team`, loop params, empty `insights` and `project_risk_score_iterations`), invokes the graph, then visualizes results.
2. `config.py`: Loads env vars and instantiates the Groq chat model (`llama-3.3-70b-versatile`).
3. `graph.py`: Builds a LangGraph state machine: scoper → mapper → scheduler → allocator → auditor → (optimizer?) → scheduler (loop).
4. Node `scoper` (`scope_decomposition_node`): Uses the LLM to generate 10–15 granular tasks (≤3 days) + assigns IDs; writes `tasks`.
5. Node `mapper` (`dependency_mapping_node`): Uses the LLM to map dependencies between tasks using task IDs; writes `dependencies`.
6. Node `scheduler` (`smart_scheduler_node`): Uses the LLM to produce `start_day`/`end_day` integers; converts into `Schedule`; writes `schedule`.
7. Node `allocator` (`resource_allocation_node`): Uses the LLM to assign tasks to team members; writes `task_allocations`.
8. Node `auditor` (`risk_audit_node`): Uses the LLM to identify risks, sums risk scores into a project risk score; appends to `project_risk_score_iterations`; increments `iteration_number`; writes `risks`.
9. `routing_logic`: Stops if max iterations reached OR latest risk score < threshold; otherwise routes to optimizer.
10. Node `optimizer` (`optimization_insight_node`): Generates one concrete improvement suggestion; appends it to `insights`.
11. `visualization.py`: Builds a Gantt chart + console report from final state and saves HTML if not running in a notebook.

## Implemented improvements (this branch)

### 1) Connect optimizer → scheduler (meaningful iterations)
- **Problem:** `optimization_insight_node` appended insights, but downstream scheduling ignored them.
- **Fix:** `smart_scheduler_node` now includes the latest insight in its prompt and instructs the model to apply it.
- **Impact:** Iterations can now purposefully change the schedule to reduce risk.

### 2) Scheduler validity guard (prevent invalid timelines)
- **Problem:** The scheduler could produce invalid ranges (e.g., `end_day <= start_day`) if the LLM output was inconsistent.
- **Fix:** Enforced `end_day >= start_day + 1` when building `TaskSchedule`.
- **Impact:** Every task has a valid, minimum 1-day duration; visualization and downstream logic are more robust.

### 3) Fix state typing mismatch for dependencies
- **Problem:** `AgentState.dependencies` was typed as `List[dict]` but the code stores `List[Dependency]`.
- **Fix:** Updated type to `List[Dependency]`.
- **Impact:** Better correctness and safer refactoring/IDE support.

### 4) Fix routing logic crash when risk history is empty
- **Problem:** `routing_logic()` accessed `project_risk_score_iterations[-1]` and could crash if the list was empty (e.g., if auditor failed or first run state was incomplete).
- **Fix:** Added a safe fallback (`last_score = 999` when no scores exist).
- **Impact:** Graph routing is now robust and won’t fail on the first iteration.

## Notes
- The system currently uses LLM reasoning inside nodes (no external tools like search/Jira/DB).
- Pydantic models (`models.py` + inner node schemas) are used to validate and normalize LLM JSON outputs.
