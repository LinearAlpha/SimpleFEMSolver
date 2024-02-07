import pandas as pd
from SimpleFEMSolver.data_visual.PostProcessCore import PostProcessCore


class ExportData(PostProcessCore):
    def save_to_file(
        self, fs_name: str, fs_type: str = "csv", sig_fig: str = "%.3f",
        **kwargs
    ) -> None:
        p_fs_type: list[str] = ["csv", "xlsx"]
        if "." in fs_name and fs_name.split(".")[-1] in p_fs_type:
            fs_type = fs_name.split(".")[-1]
            name_out = self.out_path + fs_name
        else:
            name_out = self.out_path + fs_name + "." + fs_type
        data_pd = pd.DataFrame(**kwargs)
        if fs_type == "csv":
            data_pd.to_csv(name_out, float_format=sig_fig)
        else:
            data_pd.to_excel(name_out, float_format=sig_fig)
