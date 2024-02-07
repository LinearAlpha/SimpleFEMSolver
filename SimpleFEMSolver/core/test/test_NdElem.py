import numpy as np
from SimpleFEMSolver.core import NdElem


# Testing data set
elements: list[list[int]] = [
    [1, 2],
    [1, 6],
    [2, 3],
    [2, 7],
    [2, 6],
    [2, 5],
    [3, 5],
    [3, 4],
    [4, 5],
    [5, 6],
    [6, 7]
]
node: list[list[int]] = [
    [0, 0],
    [2, 0],
    [4, 0],
    [6, 0],
    [4, 1],
    [2, 2],
    [0, 3]
]

test_ob: NdElem = NdElem(node, elements)
print(type(test_ob))
print(test_ob.nd)
print(test_ob.L)
print(test_ob.xyz)

# node2: list[list[float]] = [
#     [0.5, 0.5],
#     [2.5, 0.5],
#     [4.5, 0.5],
#     [6.5, 0.5],
#     [4.5, 1.5],
#     [2.5, 2.5],
#     [0.5, 3.5]
# ]
# node3: list[list[int]] = np.transpose(np.asarray(node)).tolist()


# test_ob: NdElem = NdElem(node, elements)
# test_ob2: NdElem = NdElem(node2, elements)
# test_ob3: NdElem = NdElem(node3, elements)
# print(test_ob.nd)
# print(test_ob2.nd)
# print(test_ob3.nd)
