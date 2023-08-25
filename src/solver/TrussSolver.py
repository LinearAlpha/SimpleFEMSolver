from matplotlib.pyplot import plot
import numpy as np
from solver.SolverCore import SolverCore
from SystemVisual import ReasultToFile, PlotSystem

class TrussSolver(SolverCore, PlotSystem, ReasultToFile):
    # def __init__(
    #     self, nd: list = None, elem: list = None, input_path: str = None,
    #     fs_name: list = None, fs_name_input: str = None, 
    #     out_path: str = "./data_out", fs_name_rs = "csv", fs_name_img = "png"
    # ) -> None:
    def __init__(
        self, nd: list = None, elem: list = None, out_path: str = "./data_out",
        fs_name_rs = "csv", fs_name_img = "png", **kwargs
        ) -> None:
        """Class constructer.
        This constructer is super to from NdElem.py class NdElem

        Args:
            nd (list, optional): Node of the system. Defaults to None.
            elem (list, optional): Elements of the system. Defaults to None.
            path (str, optional): Path where node and elements file saed.
                                  Defaults to None.
            fs_name (list, optional): File names of node and eleemtns
                                      [Node, Eleents]. Defaults to None.
            fs_type (str, optional): Type of the file, currently only support
                                     CSV and Excel. Defaults to None.
            out_path (str, optional): Output path for the reasult. 
                                      Defaults to "./data_out/".
        """

        # Initailzing parent class (SolverCore)
        super().__init__(nd, elem, **kwargs)
        # super().__init__(nd, elem, input_path, fs_name, fs_name_input)
        # Initialing ReasultToFile class as composition
        self.rs_to_file = ReasultToFile(out_path, fs_name_rs)
        # Initialing PlotSystem class as composition
        self.pltsys = PlotSystem("".join([out_path, "/plt_img"]), fs_name_img)
        self.rs_f: np.ndarray = self.tmp_bc_arr.copy() # Force on the system
        self.rs_disp: np.ndarray = self.tmp_bc_arr.copy() # Elongation of system
        # Stress at each elements
        self.sig: np.ndarray = np.zeros([self.num_elem, 1])
        self.flag_calc: bool = False

    def __calc_f(self) -> None:
        """Calculate force of the system.
        """

        tmp_ks = self._ks[:, ~self._kn_bc_disp]
        tmp_ks = tmp_ks[self._kn_bc_f, :]
        tmp_f = self.bc_f[self._kn_bc_f].copy()
        for i in range(self._kn_bc_disp.size):
            if self._kn_bc_disp[i]:
                tmp = self._ks[self._kn_bc_f, i].reshape(tmp_f.shape[0], 1)
                tmp_f -= tmp * self.bc_disp[i]
        self.rs_disp = self.bc_disp.copy()
        self.rs_disp[~self._kn_bc_disp] = np.linalg.solve(tmp_ks, tmp_f)
        self.rs_f = self._ks @ self.rs_disp

    def __calc_sig(self) -> None:
        """Calculate stress of the system on each elements.
        """

        for i in range(self.num_elem):
            po = self.elem[i] * self.dim
            po_diff = po - self.dim
            tmp_disp = np.zeros([self.dim * 2, 1])
            tmp_disp[0:2] = self.rs_disp[po_diff[0]:po[0]]
            tmp_disp[2:4] = self.rs_disp[po_diff[1]:po[1]]
            tmp_l = np.array([-1 / self.L[i], 1 / self.L[i]]).reshape(1, 2)
            self.sig[i] = self.ela[i] * tmp_l @ self._trans[i] @ tmp_disp

    def calculate_truss(self) -> None:
        """Calculateing system.
        """

        self._calc_stiffness()
        # Calculating force on each node
        self.__calc_f()
        # Calculating stress on each elements
        self.__calc_sig()
        # Setting up new node set based on displacement
        self.new_nd(self.rs_disp)
        self.flag_calc = True
        self.rs_to_file.save_to_file()

    def plot_system(
        self, sys_only: bool = False, fig_size: tuple = (16, 9), 
        plt_param: dict = None, plt_param2: dict = None, plt_title: str = None, 
        axis_unit: str = "m", show_plt: bool = False, save_img: bool = True,
        img_name: str = None, img_type: str = None
    ) -> None:

        # Setting drformed data points for plot
        xyz_deform = self.xyz_set2 if self.flag_calc & (not sys_only) else None
        # setting data for plotting
        self.pltsys.plot_system(
            self.xyz, xyz_deform, fig_size, plt_param, plt_param2, plt_title,
            axis_unit, show_plt, save_img, img_name, img_type
        )