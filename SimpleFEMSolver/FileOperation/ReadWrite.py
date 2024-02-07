from pathlib import Path
from typing import Final
import numpy as np
import pandas as pd

from SimpleFEMSolver.FileOperation import PathInfo

# Constant list of file extention that is supported
SUPPORT_FILE: Final[list[str]] = [
    "csv", "xls", "xlsx", "xlsm", "xlsb", "odf", "ods", "odt"
]


def __is_type_support(type2ch: str) -> bool:
    """ Check if input file extension type is supported by this proram

    Args:
        type2ch (str): File extension input to check

    Returns:
        bool: Return True is input extension is supported on this program
    """

    return True if type2ch.lower() in SUPPORT_FILE else False


def ReadExcel(
        path_in: Path | str,
        f_name: str = "",
        f_extention: str = "csv",
        val_sep: str = ",",
        **kwargs
) -> np.ndarray:
    f_to_read: Path = Path(path_in)
    # Message place holder when case the file is not supportted
    msg: str = f"\"{f_extention}\" is not supported\n" + \
        f"Supported file list: {SUPPORT_FILE}"

    # Check, input path is incloud file name name and extension
    if f_name != "":
        # Cheking if file extention is suppoerted or not
        if __is_type_support(f_extention):
            f_to_read = f_to_read.joinpath(
                "" if "." in f_extention else ".".join([f_name, f_extention])
            )
        else:
            raise ValueError(msg)
    elif f_to_read.suffix == "" and type(f_name) == None:
        raise ValueError(f"File name is not given")
    elif not __is_type_support(f_to_read.suffix.replace(".", "")):
        raise ValueError(msg)
    else:
        f_extention = f_to_read.suffix.replace(".", "")

    # Check if file exist
    if not f_to_read.exists():
        raise FileExistsError(f"{f_to_read.name} is not exist")
    else:
        data: np.ndarray  # Defining variavble that stores out put data.
        # Read files
        if f_extention == "csv":
            data = pd.read_csv(f_to_read, sep=val_sep, **kwargs).to_numpy()
        else:
            data = pd.read_excel(f_to_read, **kwargs).to_numpy()
    return data


def WriteExcel(
    data: np.ndarray | list[int] | list[float],
    f_name: str = "",
    f_extention: str = "csv",
    val_sep: str = ",",
    **kwargs
) -> None:
    pass
