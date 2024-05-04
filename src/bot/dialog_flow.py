class DialogFlow:
    def __init__(self, nodes):
        self.nodes = nodes


class DialogNode:
    def __init__(self, name, transitions, response_function=None):
        self.name = name
        self.transitions = transitions
        self.response_function = response_function

    def __call__(self, ctx):
        response = None
        if self.response_function is not None:
            response = self.response_function(ctx)
        return response

    async def transition(self, ctx, pipeline):
        for transition in self.transitions:
            condition, flow, node = transition
            if condition(ctx):
                ctx.current_node = pipeline[flow].nodes[node]
                break
