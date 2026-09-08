import asyncio
import json
from langgraph.graph import END, StateGraph
from app.graph.state import piiState
from app.graph.nodes.nodes import (
    selector,
    route_selector,
    a_setup,
    a_validate,
    b_probe,
    b_category,
    b_basic,
    b_build,
    b_analyze,
    execute,
    route_execute,
    route_b,
    observe_branch_a,
    observe_branch_b,
    final_observation,
    TARGET_1,
    TARGET_2,
    TARGET_3,
    CORPUS,
    TARGET_URL,
    POOL
)

def build_pii_graph() -> StateGraph:
    wf = StateGraph(piiState)
    wf.add_node("selector", selector)
    wf.add_node("a_setup", a_setup)
    wf.add_node("execute", execute)
    wf.add_node("observe_branch_a", observe_branch_a)
    wf.add_node("observe_branch_b", observe_branch_b)
    wf.add_node("a_validate", a_validate)
    wf.add_node("b_probe", b_probe)
    wf.add_node("b_category", b_category)
    wf.add_node("b_basic", b_basic)
    wf.add_node("b_build", b_build)
    wf.add_node("b_analyze", b_analyze)
    wf.add_node("final_observation", final_observation)

    wf.set_entry_point("selector")
    wf.add_conditional_edges("selector", route_selector,
                             {"branch_a": "a_setup", "branch_b": "b_probe", "end": "final_observation"})
    wf.add_edge("a_setup", "execute")
    wf.add_conditional_edges("execute", route_execute,
                             {"observe_branch_a": "observe_branch_a", "observe_branch_b": "observe_branch_b"})
    wf.add_edge("observe_branch_a", "a_validate")
    wf.add_edge("observe_branch_b", "b_analyze")
    wf.add_edge("a_validate", "selector")
    wf.add_edge("b_probe", "b_category")
    wf.add_edge("b_category", "b_basic")
    wf.add_edge("b_basic", "b_build")
    wf.add_edge("b_build", "execute")
    wf.add_conditional_edges("b_analyze", route_b,
                             {"chain": "b_build", "done": "selector"})
    wf.add_edge("final_observation", END)
    return wf

async def run_sample_test():
    print("=" * 60)
    print("REDLINE - PII Exfiltration (Branch A: few-shot | Branch B: chaining)")
    print("=" * 60)

    targets = [t for t in [TARGET_1, TARGET_2, TARGET_3] if t in CORPUS]
    for n in CORPUS:
        if len(targets) >= 3:
            break
        if n not in targets:
            targets.append(n)

    initial_state: piiState = {
        "target_url": TARGET_URL, "targets": targets,
        "a_index": 0, "b_index": 0, "variations": [],
    }

    app = build_pii_graph().compile()
    async for event in app.astream(initial_state):
        for node_name, node_output in event.items():
            print(f"\n--- Node: {node_name} ---")
            print(f"Output: {json.dumps(node_output, indent=2, default=str, ensure_ascii=False)}")

    print("\n" + "=" * 60)
    print("FINAL POOL (Branch A learned pairs):")
    for ex in POOL:
        print(f"  - {ex['name']}: {ex['info']}")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_sample_test())
