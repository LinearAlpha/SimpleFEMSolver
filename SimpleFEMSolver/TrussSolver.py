import numpy as np
from SimpleFEMSolver.core import SolverCore
from SimpleFEMSolver.FileOperation import fs_ch

import FileOperation.CheckPath as fs_ck


class TrussSolver(SolverCore):
    def __init__(self, **kwargs) -> None:
        # Initailzing parent class (SolverCore)
        super().__init__(**kwargs)
        # Force on the system
        self.rs_f: np.ndarray = self.tmp_bc_arr.copy()
        # Elongation of system
        self.rs_disp: np.ndarray = self.tmp_bc_arr.copy()
        # Stress at each elements
        self.sig: np.ndarray = np.zeros([self.num_elem, 1])
        self.flag_calc: bool = False

    def __calc_f(self) -> None:
        """
        Calculate force of the system.
        """

        tmp_ks: np.ndarray = self._ks[:, ~self._kn_bc_disp]
        tmp_ks = tmp_ks[self._kn_bc_f, :]
        tmp_f: np.ndarray = self.bc_f[self._kn_bc_f].copy()
        for i in range(self._kn_bc_disp.size):
            if self._kn_bc_disp[i]:
                tmp: np.ndarray = \
                    self._ks[self._kn_bc_f, i].reshape(tmp_f.shape[0], 1)
                tmp_f -= tmp * self.bc_disp[i]
        self.rs_disp = self.bc_disp.copy()
        self.rs_disp[~self._kn_bc_disp] = np.linalg.solve(tmp_ks, tmp_f)
        self.rs_f = self._ks @ self.rs_disp

    def __calc_sig(self) -> None:
        """
        Calculate stress of the system on each elements.
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
        """
        Calculateing system.
        """

        self._calc_stiffness()
        # Calculating force on each node
        self.__calc_f()
        # Calculating stress on each elements
        self.__calc_sig()
        # Setting up new node set based on displacement
        self.new_nd(self.rs_disp)
        self.flag_calc = True

    def save_force(
        self, f_name: str = "RS_Force", f_type: str = "csv",
        sig_fig: str = "%.3f"
    ) -> None:
        super()._save_data_FD(
            self.rs_f, "Force", "F", self.sys_unit["force"], f_name, f_type,
            sig_fig
        )

    def save_displacement(
        self, f_name: str = "RS_Displacement", f_type: str = "csv",
        sig_fig: str = "%.3f"
    ) -> None:
        super()._save_data_FD(
            self.rs_f, "Elongation", "U", self.sys_unit["lenght"], f_name, f_type,
            sig_fig
        )

    def plot_system(self, **kwargs) -> None:
        import data_visual
        tmp_path = fs_ck(self.out_path) + "sys_plot"
        p_sys = data_visual.PlotSystem(out_path=tmp_path, fs_type="png")
        # Setting drformed data points for plot
        xyz_deform = self.xyz_set2 if self.flag_calc else None
        # setting data for plotting
        p_sys.plot_system(self.xyz, xyz_deform, **kwargs)
