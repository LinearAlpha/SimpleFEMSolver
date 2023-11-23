import os
from pathlib import Path
from typing import Final
import numpy as np
import pandas as pd


def _is_win_path(path2ch: str) -> bool:
    """It is checking if path is using back slash

    Args:
        path2ch (str): Input path thet try to check

    Returns:
        bool: Returns True if is using back slash(windows path)
    """

    return True if "\\" in path2ch else False


def _is_end_slash(path2ch: str) -> bool:
    """Checkinf if path input end with slash

    Args:
        path2ch (str): Input path that tries to check

    Returns:
        bool: Return True is ended with slash
    """

    return True if path2ch[-1] == "\\" or path2ch[-1] == "/" else False


def _is_type_support(type2ch: str) -> bool:
    SUPPORT_FILE: Final[list[str]] = [
        "csv", "xls", "xlsx", "xlsm", "xlsb", "odf", "ods", "odt"
    ]
    return True if type2ch in SUPPORT_FILE else False


def _add_slash2end(path_in: str) -> str:
    path_out: str = path_in
    if not _is_end_slash(path2ch=path_in):
        path_out += ("\\" if _is_win_path(path2ch=path_in) else "/")
    return path_out


def ch_path(path2ch: str, create_dir: bool = False) -> bool:
    tmp_path = Path(path2ch)
    flag_out: bool = tmp_path.exists()
    print(os.getcwd())
    if not flag_out and create_dir:
        os.mkdir(path=tmp_path)
        flag_out = True
    return flag_out


def ReadExcel(
        path_in: str,
        file_name: str = None,
        file_type: str = "csv",
        val_sep: str = ","
) -> np.ndarray:
    is_file: bool = Path(path_in).is_file()
    data_out: np.ndarray = np.ndarray()
    slash_type: str = "\\" if _is_win_path(path2ch=path_in) else "/"

    # Chekc if path input is incould file, and update some parameter
    if is_file:
        tmp_fs_type: str = (path_in.splt(slash_type)).split(".")[-1]
        tmp_fs_type = tmp_fs_type.lower()
        # Check user input file is supported or not
        if _is_type_support(type2ch=tmp_fs_type):
            file_type = tmp_fs_type
        else:
            msg_err: str = f'\"{tmp_fs_type}\" is not support.'
            raise ValueError(msg_err)  # Exit with error
    else:
        msg_err: str = f'\"{path_in}\" is not exsit, please check your input.'
        raise ValueError(msg_err)  # Exit with error
    # Case when there is input for file name
    if not is_file and file_name != None:
        if not _is_type_support(type2ch=file_type):
            msg_err: str = f'\"{tmp_fs_type}\" is not support.'
            raise ValueError(msg_err)  # Exit with error
    else:
        msg_err: str = f'File name is not given, please check your input'
        raise ValueError(msg_err)  # Exit with error
    # Set file name based on input
    if is_file:
        file_path = path_in
    else:
        file_path: str = _add_slash2end(path_in=path_in)
        file_path += file_name + "." + file_type
    # Read files
    if file_type == "csv":
        data_out = pd.read_csv(
            filepath_or_buffer=file_path, sep=val_sep
        ).to_numpy()
    else:
        data_out = pd.read_excel(filepath_or_buffer=file_path).to_numpy()
    return data_out
