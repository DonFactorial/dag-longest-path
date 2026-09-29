import networkx as nx
import plotly.graph_objects as go
from plotly.offline import init_notebook_mode, iplot

# Generating node data
# For ease of programming, I'm indexing nodes starting from k=0 instead of 1
#    as in the problem statement
node_data = [(0, {"t": 0, "x": 0, "y": 0})]
mod_num = 10007

for i in range(1, 1000):
    node_data.append( (i, {"t": (17*node_data[-1][1]["y"] + 23) % mod_num,
                    "x": (31*node_data[-1][1]["t"] + 37) % mod_num,
                    "y": (43*node_data[-1][1]["x"] + 47) % mod_num}) )

DG = nx.DiGraph()
DG.add_nodes_from(node_data)

# Create a topological sorting based on time
# topo_sorted stores (index, dict of data) ordered by time
topo_sorted = sorted(DG.nodes(data=True), key=lambda n: n[1]["t"])


# Create edges between nodes depending on the time and distance
def calculate_distance(node1, node2):
    """"Returns distance between two nodes. Nodes must have \"t\", \"x\", and \"y\" attributes."""
    return (-100*(1 - 2/(9+node1["x"]**2+node1["y"]**2) - 
                 2/(9+node2["x"]**2+node2["y"]**2))*(node2["t"]-node1["t"])**2 
                + (node2["x"]-node1["x"])**2 + (node2["y"]-node1["y"])**2)

for i in range(len(DG.nodes)):
    for j in range(len(DG.nodes)):
        if i != j:
            dist = calculate_distance(DG.nodes[i], DG.nodes[j])
            if DG.nodes[i]["t"] < DG.nodes[j]["t"] and dist<0:
                DG.add_edge(i, j, distance=dist)


# Find the longest path in the network with dynamic programming
def find_longest_path(DG, topo_arg_sorted):
    """"Returns the longest path for a directed acyclic graph (DAG) given a topological sorting."""
    dp = [[] for _ in range(len(DG.nodes))]
    
    # Cycle through each node, but we'll be going in order of the topological sort
    for i in range(len(DG.nodes)):
        longest_arr = []
        
        # Find the predecessor with the longest path before it
        for pred in DG.predecessors(topo_arg_sorted[i][0]):
            if len(dp[pred]) > len(longest_arr):
                longest_arr = dp[pred]
                
        # Append our current node and continue forward through the digraph
        dp[topo_arg_sorted[i][0]] = longest_arr + [topo_arg_sorted[i][0]]
        
    return max(dp, key=lambda arr: len(arr))

longest_path = find_longest_path(DG, topo_sorted)
longest_path_fixed_index = [n+1 for n in longest_path]
print(longest_path_fixed_index)
print(len(longest_path))


# Do a sanity check
def check_path(DG, path):
    """"Sanity check that a path is valid."""
    for i in range(1,len(path)):
        if (DG.nodes[path[i-1]]["t"] >= DG.nodes[path[i]]["t"] or 
            calculate_distance(DG.nodes[path[i-1]], DG.nodes[path[i]]) >= 0):
            return False
    return True

print(check_path(DG, longest_path))


# Visualize with plotly
pos = nx.spring_layout(DG)
longest_path_set = set(longest_path)

# Drawing only the edges used in the optimal path (otherwise you just get a cloud)
path_edges = [(longest_path[i], longest_path[i+1]) for i in range(len(longest_path)-1)]
edge_x = []
edge_y = []
for u, v in path_edges:
    edge_x += [pos[u][0], pos[v][0], None]
    edge_y += [pos[u][1], pos[v][1], None]
    
edge_trace = go.Scattergl(x=edge_x, y=edge_y, line=dict(width=1, color="#888"),
                          hoverinfo="none", mode="lines")

# Draw all nodes, but give special colors to the nodes in the optimal path
node_x = [pos[n][0] for n in DG.nodes()]
node_y = [pos[n][1] for n in DG.nodes()]

color_list = []
for n in DG.nodes():
    if n == longest_path[0] or n == longest_path[-1]:
        color_list.append("green")
    elif n in longest_path_set:
        color_list.append("red")
    else:
        color_list.append("blue")

node_trace = go.Scattergl(x=node_x, y=node_y, mode="markers", hoverinfo="text",
                          marker=dict(showscale=False, 
                                      color=color_list, size=7, line_width=0.5),
                          text=[str(n+1) for n in DG.nodes()])

fig = go.Figure(data=[edge_trace, node_trace],
                layout=go.Layout(
                    title='The Timelike Tourist\'s Path',
                    title_font_size=16,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    xaxis=dict(showgrid=False, zeroline=False, visible=False),
                    yaxis=dict(showgrid=False, zeroline=False, visible=False)
                ))

fig.write_html("digraph.html")