import os
from pathlib import Path
from FileOperation import CheckPath


class PostProcessCore():
    # None tye values that can use to check array input
    _NoneType = type(None)

    def __init__(self, out_path: str, fs_type: str = None) -> None:
        self.out_path = CheckPath(out_path)
        self.fs_type = fs_type
        self._check_folder()

    def _check_folder(self) -> None:
        if not os.path.exists(Path(self.out_path)): os.makedirs(self.out_path)



