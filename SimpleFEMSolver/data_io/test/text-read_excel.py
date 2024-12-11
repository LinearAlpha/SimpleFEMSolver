from SimpleFEMSolver.data_io import read_excel
import numpy as np


def main() -> None:
    tmp_path = "./data/setup/"

    tmp: np.ndarray

    print("Test 1")
    tmp = read_excel(tmp_path, file_name="elements.csv")
    print(f"{tmp}\n")

    print("Test 2")
    tmp = read_excel(tmp_path, file_name="elements.xlsx")
    print(f"{tmp}\n")

    print("Test 3")
    tmp = read_excel(tmp_path, file_name="elements", file_type=".xlsx")
    print(f"{tmp}\n")

    print("Test 4")
    tmp = read_excel(tmp_path, file_name="elements", file_type="xlsx")
    print(f"{tmp}\n")

    print("Test 5")
    tmp = read_excel(f"{tmp_path}/elements.xlsx")
    print(f"{tmp}\n")


if __name__ == "__main__":
    main()
