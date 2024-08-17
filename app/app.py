from media_agents.graph_description import build_workfrlow, compile_workflow

workflow = build_workfrlow()
graph = compile_workflow(workflow)

if __name__ == "__main__":
    graph.invoke()
