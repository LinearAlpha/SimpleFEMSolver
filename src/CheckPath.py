def CheckPath(path_in: str) -> str:
    tmp_sym = path_in[-1] 
    if tmp_sym == "\\" or tmp_sym == '/':
        path_out = path_in
    else:
        path_out = path_in + ("\\" if "\\" in path_in else "/")
    if "\\" in path_out and "/" in path_out:
        path_out = path_out.replace("\\", "/")
    return path_out