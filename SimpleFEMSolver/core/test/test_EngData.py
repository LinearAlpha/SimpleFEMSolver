
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

tmp_cls = SimpleFEMSolver.core.EngData(node, elements)
tmp_cls.set_eng_prop(E, A)
print("\nSingle value Area and Elastic modules test")
print("Testing are")
print(tmp_cls.are)
new_A = [
    [2, 1],
    [5, 1]
]
tmp_cls.update_are(new_A)
print(tmp_cls.are)
tmp_cls.update_ela(new_A)
print(tmp_cls.ela)