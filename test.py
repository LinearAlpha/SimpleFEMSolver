import os
import pandas as pd
import SimpleFEMSolver.TrussSolver as TrussSolver

os.system('cls')
print("\n\tTesting code for FEM Solver\n\n")

node = [
    [0, 0],
    [2, 0],
    [4, 0],
    [6, 0],
    [4, 1],
    [2, 2],
    [0, 3]
]
elements = [
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
E = 70e6
A = 0.003125
f = [
    [
        [5, 0],
        [6, 0]
    ],
    [
        [5, -2e3],
        [6, -2e3]
    ]
]
disp = [
    [
        [1, 0],
        [7, 0]
    ],
    [
        [1, 0],
        [7, 0],
        [4, -0.6]
    ]
]


tmp_cls = TrussSolver(
    nd=node, elem=elements,
    sys_unit={"lenght": "in", "force": "lb"}
)
print(tmp_cls.__class__.__mro__)
tmp_cls.set_bc(disp, f)
tmp_cls.set_eng_prop(E, A)
tmp_cls.calculate_truss()
file_path = "./data_out/tmp/"
print("\nTest print for system stiffness matrix")
print(tmp_cls._ks)
pd.DataFrame(tmp_cls._ks).to_excel(file_path + "tmp_ks.xlsx")
print("\nTest print for force")
print(tmp_cls.rs_f)
pd.DataFrame(tmp_cls.rs_f).to_excel(file_path + "rs_f.xlsx")
print("\nTest print for displacement")
print(tmp_cls.rs_disp)
pd.DataFrame(tmp_cls.rs_disp).to_excel(file_path + "rs_disp.xlsx")
print("\nTest print for stress on each node")
print(tmp_cls.sig)
pd.DataFrame(tmp_cls.sig).to_excel(file_path + "stress.xlsx")
print("\nTest print for original node")
print(tmp_cls.nd)
pd.DataFrame(tmp_cls.nd).to_excel(file_path + "node_original.xlsx")
print("\nTest print for node set 2")
print(tmp_cls.nd)
pd.DataFrame(tmp_cls.nd_set2).to_excel(file_path + "node_set2.xlsx")
print(tmp_cls.xyz)

tmp_cls.plot_system(show_plt=False, img_type="png")
tmp_cls.save_force()
tmp_cls.save_force(f_name="RS_Force_excel", f_type="xlsx")
tmp_cls.save_displacement()
tmp_cls.save_displacement(f_name="RS_Displacement_excel", f_type="xlsx")
