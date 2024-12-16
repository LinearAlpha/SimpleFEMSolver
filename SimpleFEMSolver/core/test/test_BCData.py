import numpy as np
from SimpleFEMSolver.core import BCData, BCInputs


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

    # Normal testing
    test_obj = BCData()
    test_obj.set_nd_elem(node=node, element=elements)

    test_obj.bc_fore_input(node_num=5, x=0, y=-2e3)
    test_obj.bc_fore_input(node_num=6, x=0, y=-2e3)

    test_obj.bc_disp_input(node_num=1, x=0, y=0)
    test_obj.bc_disp_input(node_num=7, x=0, y=0)
    test_obj.bc_disp_input(node_num=4, y=-0.6)

    test_obj.init_bc()

    print(f"Boundary Force Input:\n{test_obj.bc_force}\n")
    print(test_obj._kn_bc_force)
    print(f"Boundary Displaycemnet Input:\n{test_obj.bc_disp}\n")
    print(test_obj._kn_bc_disp)

    # Batch testing
    test_obj = BCData()
    test_obj.set_nd_elem(node=node, element=elements)

    force_input = [
        BCInputs(node_num=5, x=0, y=-2e3),
        BCInputs(node_num=6, x=0, y=-2e3),
    ]
    test_obj.bc_fore_input(batch_inputs=force_input)

    disp_input = [
        BCInputs(node_num=1, x=0, y=0),
        BCInputs(node_num=7, x=0, y=0),
        BCInputs(node_num=4, y=-0.6),
    ]
    test_obj.bc_disp_input(batch_inputs=disp_input)

    test_obj.init_bc()

    print("\n\n\n\n")
    print(f"Boundary Force Input:\n{test_obj.bc_force}\n")
    print(test_obj._kn_bc_force)
    print(f"Boundary Displaycemnet Input:\n{test_obj.bc_disp}\n")
    print(test_obj._kn_bc_disp)


if __name__ == "__main__":
    main()
