from media_agents.graph_description import build_workfrlow, compile_workflow

workflow = build_workfrlow()
graph = compile_workflow(workflow)

def main():  # pragma: no cover
    """
    The main function executes on commands:
    `python -m media_agents` and `$ media_agents `.
    """
    print('it is working!')
    #graph.invoke({'last_processed_id':0})
