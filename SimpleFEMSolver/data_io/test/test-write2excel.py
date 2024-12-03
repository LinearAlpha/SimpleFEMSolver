import numpy as np
from SimpleFEMSolver.data_io import write2excel


def main() -> None:
    test_data: np.ndarray = np.arange(33).reshape(11, 3)
    test_header: list[str] = ["data1", "data2", "data3"]
    test_path = "./data/test_out"

    print("test1")
    write2excel(test_data, path2write=test_path)

    print("test2")
    write2excel(test_data, path2write=test_path, file_name="test1")

    print("test3")
    write2excel(
        test_data, path2write=test_path, file_name="test2", file_type="xlsx"
    )

    print("test4")
    write2excel(
        test_data,
        data_header=test_header,
        path2write=test_path,
        file_name="test3.xlsx",
    )

    print("test5")
    write2excel(
        test_data,
        data_header=test_header,
        path2write=test_path,
        file_name="test4.csv",
    )


if __name__ == "__main__":
    main()
