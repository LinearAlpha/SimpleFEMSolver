from pathlib import Path


def check_dir_exist(path_to_check: Path | str, mkdir: bool) -> [bool, Path]:
    out_flag: bool = False

    # Check if input is string, if it is converted to path object
    if type(path_to_check) == str:
        path_to_check = Path(path_to_check)

    # Check if input directory is exist, and make directory if flag is true
    if not path_to_check.exists() and mkdir:
        path_to_check.mkdir()
    else:
        out_flag = True
    return [out_flag, path_to_check]
