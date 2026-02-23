import os
import re
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta


def visualize_results(final_state):
    print(f"\n=== Project Report: {final_state['project_description']} ===")

    # Format Risk History (e.g., "25 -> 10 -> 0")
    risk_scores = final_state.get("project_risk_score_iterations", [])
    risk_display = " -> ".join(map(str, risk_scores)) if risk_scores else "N/A"
    print(f"Risk Score History: {risk_display}")

    print("\n--- Team Structure ---")
    for m in final_state["team"].team_members:
        print(f"└── {m.name} ({m.role})")

    # --- Prepare Data ---
    sched_data = []
    start_date_base = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)

    # Lookup maps
    sched_map = {item.task.task_name: item for item in final_state["schedule"].schedule}
    alloc_map = {
        a.task.task_name: a.team_member.name
        for a in final_state["task_allocations"].task_allocations
    }

    # Iterate through ALL tasks (master list)
    for task in final_state["tasks"].task:
        t_name = task.task_name
        assignee = alloc_map.get(t_name, "Unassigned")

        if t_name in sched_map:
            item = sched_map[t_name]
            start_day = max(0, item.start_day)
            end_day = max(start_day + 1, item.end_day)  # Ensure end > start
        else:
            start_day = 0
            end_day = 1
            assignee = f"{assignee} (Unscheduled)"

        s_date = start_date_base + timedelta(days=start_day)
        duration = max(1, end_day - start_day)
        e_date = s_date + timedelta(days=duration)

        sched_data.append(
            {
                "Task": t_name,
                "Start": s_date.strftime("%Y-%m-%d"),
                "Finish": e_date.strftime("%Y-%m-%d"),
                "Assignee": assignee,
                "Duration (Days)": duration,
                "Description": (task.task_description or "")[:60] + "...",
            }
        )

    if not sched_data:
        print("\n[ERROR] No tasks found to plot.")
        return

    df = pd.DataFrame(sched_data).sort_values("Start")
    if df.empty:
        print("\n[ERROR] No tasks found to plot.")
        return

    fig = px.timeline(
        df,
        x_start="Start",
        x_end="Finish",
        y="Task",
        color="Assignee",
        hover_data=["Duration (Days)", "Description"],
        title=f"<b>Project Schedule</b>: {final_state['project_description']}<br>(Risk Score History: {risk_display})",
        template="plotly_white",
        height=400 + (len(df) * 30),
    )

    fig.update_yaxes(autorange="reversed", title="")
    fig.update_xaxes(title="Timeline", dtick="D1", tickformat="%b %d")
    fig.update_layout(
        bargap=0.2,
        legend_title_text="Team Member",
        font=dict(family="Arial", size=12),
        margin=dict(l=150, r=50, t=90, b=50),
    )

    # Always save HTML with project-name-based filename
    os.makedirs("outputs", exist_ok=True)
    project_title = final_state.get("project_description", "project")
    safe_title = re.sub(r"[^a-zA-Z0-9]+", "_", project_title).strip("_")[:80]
    output_file = os.path.join("outputs", f"{safe_title}.html")

    fig.write_html(output_file)
    print(f"\n[INFO] Gantt chart saved to '{output_file}'")

    # Also display in notebook if available
    try:
        get_ipython()
        fig.show()
    except Exception:
        pass
