# gml_reder.py
# Author 정연

from typing import TextIO
import numpy as np
import numpy.typing as npt

infile_name = 'depth.txt'
outfile_name = 'graph.gml'

ngene: int                        # |V|
weights: npt.NDArray[np.float64]  # |V| 사이즈 가중치 행렬
adj: npt.NDArray[np.bool_]        # (|V|, |V|) 사이즈 인접행렬
erasure: npt.NDArray[np.bool_]    # i번째 노드를 출력할것인가

weight_min: float = 1
weight_max: float = 1600

def update_erasure():
    global ngene, weights, adj, weight_max, weight_min, erasure
    for i in range(ngene):
        neighbor_count = 0
        for j in range(ngene):
            if adj[i,j]:
                neighbor_count += 1
        erasure[i] = neighbor_count < 5

def read_graph_adj_list(f: TextIO):
    global ngene, weights, adj, weight_max, weight_min, erasure
    ngene = int(f.readline().strip())
    weights = np.zeros((ngene,), dtype=np.float64)
    adj = np.full((ngene, ngene), False, dtype=np.bool_)
    erasure = np.full((ngene,), False, dtype=np.bool_)
    weights_read = f.readline().strip().split(' ')
    assert len(weights_read) == ngene
    assert len(weights) == ngene
    for i, item in enumerate(weights_read):
        weights[i] = float(item.strip())
    weight_min = np.min(weights)
    weight_max = np.max(weights)
    for i in range(ngene):
        neighbors_read = f.readline().strip().split()
        for neighbor in neighbors_read:
            j = int(neighbor)
            adj[i, j] = True
    update_erasure

def lerp_color(fromColor: npt.NDArray[np.int32], toColor: npt.NDArray[np.int32], percent: float):
  return fromColor + percent*(toColor - fromColor)

def repr_color(color: npt.NDArray[np.int32]) -> str:
  assert len(color) == 3
  return '#' + ''.join([hex(int(value))[2:].rjust(2,'0') for value in color])

assert repr_color(np.array([0, 0, 0])).lower() == '#000000', f'actual value is {repr_color(np.array([0, 0, 0]))}'
assert repr_color(np.array([255, 255, 255])).lower() == '#ffffff'
assert repr_color(np.array([192, 128, 0])).lower() == '#c08000'

startcolor: npt.NDArray[np.int32] = np.array([114, 2, 250], dtype=np.int32)
endcolor: npt.NDArray[np.int32] = np.array([250, 151, 2], dtype=np.int32)

def color_node(i: int) -> npt.NDArray[np.int32]:
    weight: float = min(weight_max, max(weight_min, weights[i]))
    percent: float = np.log2(weight - weight_min+1)/np.log2(weight_max - weight_min+1)
    # 이 식을 조정하면 됨
    # percent: float = (weight - weight_min+1)/(weight_max - weight_min+1)
    # percent should be in [0, 1]
    return lerp_color(startcolor, endcolor, percent)

def repr_node(i: int) -> str:
    color = color_node(i)
    color_str = repr_color(color)
    if erasure[i]:
        return ""
    return f"node [ id {i} graphics [ fill \"{color_str}\" ] ]"

def repr_edge(i: int, j: int) -> str:
    if erasure[i] or erasure[j]:
        return ""
    return f"edge [ source {i} target {j} ]"

def repr_graph() -> str:
    nodes = [repr_node(i) for i in range(ngene)]
    edges = []
    for i in range(ngene):
        for j in range(i+1, ngene):
            if adj[i, j]:
                edges.append(repr_edge(i, j))
    terpi = '\n'
    return f"graph [\n{terpi.join(nodes)}\n{terpi.join(edges)}\n]\n"

def write_graph(f: TextIO):
    f.write(repr_graph())

# ngene = 4
# weights = np.array([1.0, 1.5, 2.0, 2.5])
# adj = np.full((4, 4), False, dtype=np.bool_)
# adj[2,3] = True
# adj[3,2] = True

# import sys
# write_graph(sys.stdout)
# with open('graph.gml', 'w') as f:
#     write_graph(f)

graph_info = infile_name
with open(graph_info, 'r') as f:
    read_graph_adj_list(f)
    with open(outfile_name, 'w') as w:
        write_graph(w)