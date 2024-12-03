from SimpleFEMSolver.data_io import read_excel
import numpy as np


def main() -> None:
    tmp_path = "./data/setup/"

    tmp: np.ndarray

    tmp = read_excel(tmp_path, file_name="elements.csv")
    print(f"{tmp}\n")

    tmp = read_excel(tmp_path, file_name="elements.xlsx")
    print(f"{tmp}\n")

    tmp = read_excel(tmp_path, file_name="elements", file_type=".xlsx")
    print(f"{tmp}\n")

    tmp = read_excel(tmp_path, file_name="elements", file_type="xlsx")
    print(f"{tmp}\n")

    tmp = read_excel(f"{tmp_path}\\elements.xlsx")
    print(f"{tmp}\n")


if __name__ == "__main__":
    main()
