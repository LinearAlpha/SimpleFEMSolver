def _is_win_path(path2ch: str) -> bool:
    """It is checking if path is using back slash

    Args:
        path2ch (str): Input path thet try to check

    Returns:
        bool: Returns True if is using back slash(windows path)
    """
    return True if "\\" in path2ch else False


def _is_end_slash(path2ch: str) -> bool:
    """Check if path input end with slash

    Args:
        path2ch (str): In put path that tries to check

    Returns:
        bool: Return True if input path is ended with slash
    """
    return True if path2ch[-1] == "\\" or path2ch[-1] == "/" else False


def _add_slash2end(path_in: str) -> str:
    """Adding slash to the end of path

    Args:
        path_in (str): Paht that need ot check

    Returns:
        str: Path in string after process
    """
    path_out: str = path_in
    if not _is_end_slash(path2ch=path_in):
        path_out += ("\\" if _is_win_path(path2ch=path_in) else "/")
    return path_out


def _has_fs_exten(fs_name: str) -> [bool, str]:
    """Check if file name included file extention

    Args:
        fs_name (str): File name that what to check

    Returns:
        [bool, str]: Falg for file extion is exist or not, file extention
    """
    flag: bool = False
    fs_extention: str = ""
    if "." in fs_name:
        fs_extention = fs_name.split(".")[-1]
        flag = True
    return [flag, fs_extention]
