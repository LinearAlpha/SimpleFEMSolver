# Built in modules
import sys
from pathlib import Path
from typing import Final

# Installed package
import numpy as np
import pandas as pd

# Current project path. In case when this program is compiled with nuitka,
# the project path need to parse from initial system call
CURRENT_P_PATH: Path = Path(f"{sys.argv[0]}").parent.resolve()
# Constant list of file extension that is supported
SUPPORT_FILE: Final[list[str]] = [
    "csv",
    "xls",
    "xlsx",
    "xlsm",
    "xlsx",
    "odf",
    "ods",
    "odt",
]


def __is_supported(type2ch: str) -> bool:
    """Check if input file extension is supported

    Args:
        type2ch (str): File extension name

    Returns:
        bool: Return True is input extension is supported on this program
    """

    return True if type2ch.lower() in SUPPORT_FILE else False


def __update_path(path2update: Path, file_name: str, file_type: str) -> Path:
    """Check user input of file name and extension and update those information
    into path object

    Args:
        path2update (Path): Input path to update.
        file_name (str): File name is given by user.
        file_type (str): File extension given as input.

    Raises:
        ValueError: Given file extension is not supported on this program.

    Returns:
        Path: Update Path object with file name and extension.
    """

    # Check if file name was given with extension
    if "." in file_name:
        # Predefined valuable to parse file extension information
        tmp_split = file_name.split(".")
        # Only update valuable when parsed information is supported
        if __is_supported(tmp_split[-1]):
            file_type = tmp_split[-1]
            file_name = ".".join(tmp_split[:-1])

    # Check file type is given with dot
    if "." in file_type:
        file_type = file_type.split(".")[-1]

    # Check input file extension is supported
    if not __is_supported(file_type):
        # Raise error
        raise ValueError(
            f'"{file_type}" is not supported.\n'
            + f"Supported file list: {SUPPORT_FILE}"
        )

    # Update path2file valuable with file name and extension
    return path2update.joinpath(f"{file_name}.{file_type}")


def to_path_obj(path2check: Path | str) -> Path:
    """Check if user given path information as string. If it is, then convert
    to Path object

    Args:
        path2check (Path | str): Path given by user

    Returns:
        Path: Converted object
    """

    ty_flag: bool = type(path2check) == str  # Check if input type is string
    return Path(path2check).resolve() if ty_flag else path2check.resolve()  # type: ignore


def read_excel(
    path2file: Path | str,
    file_name: str = "",
    file_type: str = "csv",
    **kwargs,
) -> np.ndarray:
    """Load excel or csv from drive, and convert into numpy array.

    Args:
        path2file (Path | str): Root or file path to the excel file
        file_name (str, optional): Name of excel file. Defaults to "".
        file_type (str, optional): Extension of the excel file. Defaults to "csv".

    Raises:
        FileExistsError: Given file is not exist in the provided path

    Returns:
        np.ndarray: Date that parsed form file
    """

    path2file = to_path_obj(path2file)  # Convert to Path object

    # Check if file name input was given
    if file_name != "":
        path2file = __update_path(path2file, file_name, file_type)

    # Check if file is exist. If it is, then load file from drive
    if not path2file.exists():
        raise FileExistsError("File is not exist")
    else:
        # Return loaded data in numpy array
        if path2file.suffix == ".csv":
            return pd.read_csv(path2file, **kwargs).to_numpy()
        else:
            return pd.read_excel(path2file, **kwargs).to_numpy()


def write2excel(
    data: np.ndarray,
    data_header: list[str] | list[int] | list[float] = [],
    path2write: Path | str = CURRENT_P_PATH.joinpath("data_out"),
    file_name: str = "out_data",
    file_type: str = "csv",
    pd_index: bool = False,
    **kwargs,
) -> None:
    """Save input data into excel file.

    Args:
        data (np.ndarray): Data to save
        data_header (list[str] | list[int] | list[float], optional): Header
        of that data, first column of the file. Defaults to [""].
        path2write (Path | str, optional): Path to save data.
        Defaults to CURRENT_P_PATH.joinpath("data_out").
        file_name (str, optional): Name of output file. Defaults to "out_data".
        file_type (str, optional): Output file extension. Defaults to "csv".
        pd_index (bool, optional): Choose whether enable Pandas DataFrame index
        when save to file. Defaults to False.
    """

    path2write = to_path_obj(path2write)  # Convert to Path object

    # Check if user provide full file with file name and extension
    if path2write.suffix == "":
        path2write = __update_path(path2write, file_name, file_type)

    # If output path is not exist, create one
    if not path2write.parent.exists():
        path2write.parent.mkdir()

    # If file exist under same name, carnage existing file with old at te end
    if path2write.exists():
        tmp_path = path2write.with_stem(f"{path2write.stem}_old")
        try:
            # path2write.rename(path2write.with_stem(f"{path2write.stem}_old"))
            path2write.rename(tmp_path)
        except:
            tmp_path.unlink()
            path2write.rename(tmp_path)

    flag: bool = not data_header  # Flag to user input
    # Create Pandas object based on user input
    data_pd: pd.DataFrame = (
        pd.DataFrame(data) if flag else pd.DataFrame(data, columns=data_header)
    )

    # Add index to the kwargs
    if not "index" in kwargs.keys():
        kwargs.update({"index": pd_index})

    # Write to file
    if path2write.suffix == ".csv":
        data_pd.to_csv(path2write, **kwargs)
    else:
        data_pd.to_excel(path2write, **kwargs)
