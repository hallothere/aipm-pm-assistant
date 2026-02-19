# main.py
import argparse

from src.models import Team, TeamMember
from src.graph import build_graph
from src.visualization import visualize_results


def build_default_team() -> Team:
    """Default demo team (can be replaced later by loading from JSON/YAML)."""
    return Team(
        team_members=[
            TeamMember(
                name="Alice",
                role="Lead Dev",
                skills=["Python", "LangGraph", "Architecture"],
                seniority="Senior",
            ),
            TeamMember(
                name="Bob",
                role="Frontend",
                skills=["React", "UI/UX"],
                seniority="Mid",
            ),
            TeamMember(
                name="Charlie",
                role="QA",
                skills=["Testing", "Python"],
                seniority="Junior",
            ),
        ]
    )


def main():
    parser = argparse.ArgumentParser(description="Run the modular PM assistant workflow.")
    parser.add_argument(
        "--project",
        type=str,
        default="Create a secure, multi-user AI dashboard using LangGraph and React.",
        help="Project description the agent should plan for.",
    )
    parser.add_argument(
        "--max-iter",
        type=int,
        default=2,
        help="Maximum optimization iterations (auditor cycles).",
    )
    parser.add_argument(
        "--thread-id",
        type=str,
        default="prod_v1",
        help="LangGraph thread_id (used for checkpointing / run identity).",
    )
    args = parser.parse_args()

    # 1) Define Team
    my_team = build_default_team()

    # 2) Define Initial State
    init_state = {
        "project_description": args.project,
        "team": my_team,
        "iteration_number": 0,
        "max_iteration": args.max_iter,
        "insights": [],
        "project_risk_score_iterations": [],
    }

    # 3) Build & Run
    print("Initializing Workflow...")
    graph = build_graph()

    print("Running Agent...")
    final_state = graph.invoke(init_state, {"configurable": {"thread_id": args.thread_id}})

    print("Workflow Finished!")

    # 4) Report
    visualize_results(final_state)


if __name__ == "__main__":
    main()
