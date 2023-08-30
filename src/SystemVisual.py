import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from CheckPath import CheckPath

class VisualCore():
    # None tye values that can use to check array input
    _NoneType = type(None)

    def __init__(self, out_path: str, fs_type: str = None) -> None:
        self.out_path = CheckPath(out_path)
        self.fs_type = fs_type
        self._check_folder()

    def _check_folder(self) -> None:
        if not os.path.exists(Path(self.out_path)): os.makedirs(self.out_path)

class ReasultToFile(VisualCore):
    def save_to_file(
        self, fs_name: str, fs_type: str = "csv", sig_fig: str = "%.3f",
        **kwargs
    ) -> None:
        p_fs_type = ["csv", "xlsx"]
        if "." in fs_name and fs_name.split(".")[-1] in p_fs_type:
            fs_type = fs_name.split(".")[-1]
            name_out = self.out_path + fs_name
        else:
            name_out = self.out_path + fs_name + "." + fs_type
        data_pd = pd.DataFrame(**kwargs)
        if fs_type == "csv": data_pd.to_csv(name_out, float_format=sig_fig)
        else: data_pd.to_excel(name_out, float_format=sig_fig)

class PlotSystem(VisualCore):
    def __init__(self, **kwargs) -> None:
        # Initializing parent class (VisualCore)
        super().__init__(**kwargs)
        self.fig: mpl.figure.Figure# Matplotlib figure object
        self.ax: plt.Axes # Matplotlib axes object
        self.dim: int # Dimention of the system 

    def __ploting(
        self, data: np.ndarray, plt_param: dict,
        data2: np.ndarray = None, plt_param2: dict = None
    ) -> None:
        """
        Plotting system based on inputs. To make life easy, when it is 
        plotting two syste, whcih is original and deformed, it will plot 
        alternativly so it can make legend easy as just passing names in order.
        This function must fallow data format below to plot system.

        data = [
            [
                [x1, x2], [x3, x4], ....
            ],
            [
                [y1, y2], [y3, y4], ....
            ], 
            [
                [z1, z2], [z3, z4], .... # Z-axis can be omitted
            ]
        ]

        For the plot paramater, please refer matplotlib to check plot parmater

        Args:
            data (np.ndarray): System data to plot
            plt_param (dict): Plot paramater to use when plotting original 
            system
            data2 (np.ndarray, optional): Deformed system data to plot. 
            Defaults to None.
            plt_param2 (dict, optional): Plot paramater to use when plotting deformed system. Defaults to None.
        """

        arr_shape = data.shape # Get shape of input array
        self.dim = arr_shape[0] # Getting dimention of the system
        for i in range(arr_shape[1]):
            if self.dim < 3:
                self.ax.plot(data[0][i, :], data[1][i, :], **plt_param)
                # Ploting deformed system
                if not isinstance(data2, self._NoneType):
                    self.ax.plot(data2[0][i, :], data2[1][i, :], **plt_param2)
            else: # In case of 3D
                self.ax.plot(
                    data[0][i, :], data[1][i, :], data[2][i, :], **plt_param)
                # Ploting deformed system
                if not isinstance(data2, self._NoneType):
                    self.ax.plot(
                        data2[0][i, :], data2[1][i, :], data[2][i, :],
                        **plt_param2
                    )

    def __plt_labels(self, title: str, label_unit: str) -> None:
        """Adding labels and title to the fiture

        Args:
            title (str): Title of thr plot 
            label_unit (str): Unit of axis, this function assaumes all of the
            axis has same unit
        """

        self.ax.set_title(title)
        # Setting up axis title format
        tmp_str: str = "".join(["x-axis", "[", label_unit, "]"])
        self.ax.set_xlabel(tmp_str)
        tmp_str.replace("x-", "y-")
        self.ax.set_ylabel(tmp_str)
        # Case when system is in 3D
        if self.dim == 3: self.ax.set_zlabel(tmp_str.replace("y-", "z-"))

    def __to_img(self, fs_name: str, img_type: str = None) -> None:
        """Saves figure into image

        Args:
            fs_name (str): File name
            img_type (str, optional): Format of image. Defaults to None.
        """

        if img_type != None: self.fs_type = img_type
        plt.savefig("".join([self.out_path, "/", fs_name, ".", self.fs_type]))

    def __plt_operation(
        self, name: str, show_plt: bool, save_img: bool, img_type: str = None
    ) -> None:
        """It perfroms operations that saving plot and showing plot based on
        user inputs

        Args:
            name (str): Name of the image file
            show_plt (bool): Flag that weather show plot or not
            save_img (bool): Flag weather save plot to image or not
            img_type (str, optional): Image file type. Defaults to None.
        """

        if save_img: self.__to_img(name, img_type)
        if show_plt: plt.show() # Show system only if user what

    def plot_system(
        self, xyz_org: np.ndarray, xyz_deform: np.ndarray = None,
        plt_param: dict = None, plt_param2: dict = None, 
        fig_size: tuple = (16, 9), plt_title: str = None, axis_unit: str = "m", 
        show_plt: bool = False, save2img: bool = True, img_name: str = None,
        img_type: str = None, scale_fact: float = 1
    ) -> plt.Axes:
        self.fig, self.ax = plt.subplots(figsize=fig_size, layout='constrained')
        plt.grid() # Turing on grid on the plot
        # Case when there is no user input for plot parameter. 
        # It will set plot parameter to the default
        if isinstance(plt_param, self._NoneType) & \
            isinstance(xyz_deform, self._NoneType): 
            plt_param = {'color': 'b', 'marker': 'o', 'linestyle': '-'}
        else:
            plt_param = {'color': 'b', 'marker': 'o', 'linestyle': '--'}
        # Case when there is deformed data, but no parameter inputs
        if not isinstance(xyz_deform, self._NoneType) & \
            isinstance(plt_param2, self._NoneType):
                plt_param2 = {'color': 'r', 'marker': 'o', 'linestyle': '-'}
        if isinstance(xyz_deform, self._NoneType):
            # Setting up plot title and output file name
            if plt_title == None: plt_title = "Original System"
            if img_name == None: img_name = "plt_sys"
        else:
            if plt_title == None: plt_title = "System Plot with Deformation"
            if img_name == None: img_name = "plt_sys_w_deform"
        # Ploting system
        self.__ploting(xyz_org, plt_param, xyz_deform, plt_param2)
        # Adding legend to the plot only when we have second input
        if not isinstance(xyz_deform, self._NoneType):
            self.ax.legend(["Original System", "Deformed System"])
        self.__plt_labels(plt_title, axis_unit)
        self.__plt_operation(img_name, show_plt, save2img, img_type)
        return self.ax