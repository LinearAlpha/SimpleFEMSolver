from pathlib import Path
import pytest
import pandas as pd
from SimpleFEMSolver.FileOperation import ReadExcel

project_path: Path = Path(r"./data/setup")
files: list[Path] = [x for x in project_path.glob('**/*') if x.is_file()]

print(f"========ReadExcel function test is start========")
for fs_tmp in files:
    print(f"Excel file readinf test for {fs_tmp}")
    if fs_tmp.suffix.lower().replace(".", "") == "csv":
        assert ReadExcel(fs_tmp).all() == pd.read_csv(fs_tmp).to_numpy().all()
    else:
        assert ReadExcel(fs_tmp).all() == pd.read_excel(
            fs_tmp).to_numpy().all()
print(f"Testing indiviaul file with cvs")
file_ls: list[str] = ["elements", "elements3D", "node", "node3D"]
f_exten = "csv"
for fs_tmp in file_ls:
    print(f"Testing file for {fs_tmp}")
    tmp: Path = project_path.joinpath(".".join([fs_tmp, f_exten]))
    assert ReadExcel(project_path, fs_tmp, f_exten).all() == \
        pd.read_csv(tmp).to_numpy().all()
file_ls: list[str] = ["elements", "node"]
f_exten = "xlsx"
for fs_tmp in file_ls:
    print(f"Testing file for {fs_tmp}")
    tmp: Path = project_path.joinpath(".".join([fs_tmp, f_exten]))
    assert ReadExcel(project_path, fs_tmp, f_exten).all() == \
        pd.read_excel(tmp).to_numpy().all()
print("========ReadExcel function test is complete========")
