import os
from pathlib import Path

import pytest
from SimpleFEMSolver.FileOperation import ReadWrite

# _is_win_path
assert ReadWrite._is_win_path(path2ch="./test") == False
assert ReadWrite._is_win_path(path2ch=".\\test") == True

# _is_end_slash
assert ReadWrite._is_end_slash(path2ch="./test/") == True
assert ReadWrite._is_end_slash(path2ch="./test") == False

# _is_type_support
for tmp in ["csv", "xls", "xlsx", "xlsm", "xlsb", "odf", "ods", "odt"]:
    assert ReadWrite._is_type_support(type2ch=tmp)
assert ReadWrite._is_type_support(type2ch="doxs") == False

# _add_slash2end
assert ReadWrite._add_slash2end(path_in="./test") == "./test/"
assert ReadWrite._add_slash2end(path_in="./test/") == "./test/"

# ch_path
assert ReadWrite.ch_path(path2ch="./tmp") == False
assert ReadWrite.ch_path(path2ch="./tmp", create_dir=True) == True
os.getcwd()
os.remove(path=Path("./tmp"))
