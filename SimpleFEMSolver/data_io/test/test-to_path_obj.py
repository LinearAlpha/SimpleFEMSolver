from SimpleFEMSolver.data_io import to_path_obj


def main() -> None:
    tmp_path = to_path_obj("./")
    print(tmp_path)
    print(type(tmp_path))
    print(tmp_path.parent)

    print("")

    tmp_path = to_path_obj("./test.txt")
    print(tmp_path)
    print(type(tmp_path))
    print(tmp_path.parent)


if __name__ == "__main__":
    main()
