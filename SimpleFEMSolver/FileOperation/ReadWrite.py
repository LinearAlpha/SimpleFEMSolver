from pathlib import Path
from typing import Final
import numpy as np
import pandas as pd

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
        **kwargs
) -> np.ndarray:
    """Reads data from excel or csv files and convers that 
    data into numpy array

    Args:
        path_in (Path | str): Location of the file
        f_name (str, optional): Data file name. Defaults to "".
        f_extention (str, optional): Data file extention. Defaults to "csv".
        CSV by pandas read_csv function. Defaults to ",".

    Raises:
        ValueError: File extention is not supportted
        ValueError: File name is not given
        ValueError: File extention is not supportted
        FileExistsError: File is not exist

    Returns:
        np.ndarray: Data has been readed from file
    """

    f_to_read: Path = Path(path_in)
    # Message place holder when case the file is not supportted
    msg: str = f"\"{f_extention}\" is not supported\n" + \
        f"Supported file list: {SUPPORT_FILE}"

    # Check, input path is incloud file name name and extension
    if f_name != "":
        # Cheking if file extention is suppoerted or not
        if __is_type_support(f_extention):
            f_to_read.joinpath(
                ("" if "." in f_extention else ".").join([f_name, f_extention])
            )
        else:
            raise ValueError(msg)
    # Case when file name is not given
    elif f_to_read.suffix == "" and type(f_name) == None:
        raise ValueError(f"File name is not given")
    # Case when file extention is not supported
    elif not __is_type_support(f_to_read.suffix.replace(".", "")):
        raise ValueError(msg)
    else:
        # Updating file extention
        f_extention = f_to_read.suffix.replace(".", "")

    # Check if file exist
    if not f_to_read.exists():
        raise FileExistsError(f"{f_to_read.name} is not exist")
    else:
        data: np.ndarray  # Defining variavble that stores out put data.
        # Read files
        if f_extention == "csv":
            data = pd.read_csv(f_to_read, **kwargs).to_numpy()
        else:
            data = pd.read_excel(f_to_read, **kwargs).to_numpy()
    return data


def WriteExcel(
    data: np.ndarray | list[int] | list[float],
    path_in: Path | str,
    f_name: str,
    f_extention: str = "csv",
    data_heater: list[str] | list[int] | list[float] = None,
    **kwargs
) -> None:

    project_p: Path = Path(path_in)
    f_to_save: Path = project_p.joinpath(
        ("" if "." in f_extention else ".").join([f_name, f_extention])
    )

    # Make directory if it is not exist
    if not project_p.exists():
        project_p.mkdir()

    # Check if file exis and if rxist, repalce file with "_old" surffix
    if f_to_save.exists():
        f_to_save.replace(
            f_to_save.with_name(
                ("" if "." in f_extention else ".").join(
                    [f_name + "_old", f_extention]
                )
            )
        )

    # Converting numpy array to pandas dataframe
    data_to_save = pd.DataFrame(data, columns=data_heater)

    # Save to excel files
    if f_extention.replace(".", "") == "csv":
        data_to_save.to_csv(f_to_save, **kwargs)
    else:
        data_to_save.to_excel(f_to_save, **kwargs)
