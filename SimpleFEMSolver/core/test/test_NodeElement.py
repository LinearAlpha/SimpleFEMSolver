import numpy as np
from SimpleFEMSolver.core import NodeElement


def test_print(obj: NodeElement) -> None:
    print(f"Dimension:\n{obj.dim}\n")
    print(f"Node:\n{obj.node}\n")
    print(f"Elements:\n{obj.elements}\n")
    print(f"XYZ Coordinate:\n{obj.xyz}\n")
    print(f"Area:\n{obj.area}\n")
    print(f"Elastic modules:\n{obj.elastic_modules}\n")
    print(f"Internal Energy:\n{obj._internal_e}\n")
    print(f"Unit:\n{obj.system_unit}\n")


def main() -> None:
    # Testing data set
    node: list[list[int]] = [
        [0, 0],
        [2, 0],
        [4, 0],
        [6, 0],
        [4, 1],
        [2, 2],
        [0, 3],
    ]

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
        [6, 7],
    ]

    element_area = 0.158
    elastic_m = 5e10

    test_obj = NodeElement()
    test_obj.set_nd_elem(node=node, element=elements)
    test_obj.set_elem_property(elem_area=element_area, elastic_m=elastic_m)
    test_print(test_obj)

    element_area = [[1, 1.23], [2, 4.56], [3, 7.89]]
    elastic_m = [[1, 5e10], [2, 5e10], [3, 5e10]]
    test_obj.set_elem_property_batch(
        elem_area=element_area, elastic_m=elastic_m
    )
    test_obj.set_system_unit(force="It is working")
    test_print(test_obj)


if __name__ == "__main__":
    main()
