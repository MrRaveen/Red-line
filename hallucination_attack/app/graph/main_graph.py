import asyncio
import json
from langgraph.graph import END, StateGraph
from app.graph.state import hypState
from app.graph.nodes.nodes import (
    load_batch,
    send_prompt,
    extract_imports_node,
    check_registry,
    score,
    rank
)

def build_hallucination_graph() -> StateGraph:
    wf = StateGraph(hypState)
    for name, fn in [("load_batch", load_batch), ("send_prompt", send_prompt),
                     ("extract_imports_node", extract_imports_node),
                     ("check_registry", check_registry), ("score", score),
                     ("rank", rank)]:
        wf.add_node(name, fn)

    wf.set_entry_point("load_batch")
    
    def post_load(state: hypState) -> str:
        return "send_prompt" if (state.get("prompts") or []) else "rank"
    
    wf.add_conditional_edges("load_batch", post_load, {"send_prompt": "send_prompt", "rank": "rank"})

    wf.add_edge("send_prompt", "extract_imports_node")
    wf.add_edge("extract_imports_node", "check_registry")
    wf.add_edge("check_registry", "score")
    
    def after_score(state: hypState) -> str:
        if state.get("ranked"):
            return "end"
        idx = state.get("prompt_index") or 0
        prompts = state.get("prompts") or []
        return "send_prompt" if idx < len(prompts) else "rank"
        
    wf.add_conditional_edges("score", after_score,
                             {"send_prompt": "send_prompt", "rank": "rank", "end": END})
    wf.add_edge("rank", END)
    return wf

async def run_sample_test():
    print("=" * 60)
    print("REDLINE - Hallucination Attack Graph (Package-Squatting Discovery)")
    print("=" * 60)
    initial: hypState = {"prompts": None, "prompt_index": 0}
    app = build_hallucination_graph().compile()
    final = None
    try:
        async for event in app.astream(initial):
            for node_name, node_output in event.items():
                print(f"\n--- Node: {node_name} ---")
                safe = {k: v for k, v in node_output.items() if k not in ("lastCode",)}
                print(f"Output: {json.dumps(safe, indent=2, default=str)}")
            final = event

        final_state = list(final.values())[0] if final else {}
        ranked = final_state.get("ranked")

        print("\n[*] Top hallucinated-package candidates (register these to weaponise):")
        for r in (ranked or []):
            print(f"  - {r['name']} @ {r['registry']} (rate={r['appearance_rate']})")
    except Exception as e:
        print(f"\n[TEST] Graph failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_sample_test())
