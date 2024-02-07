import numpy as np
from SimpleFEMSolver.core import EngData
from SimpleFEMSolver.data_visual import ExportData
from SimpleFEMSolver.FileOperation import ReadWrite


class SolverCore(EngData):
    # Class attribute
    __tmpK: np.ndarray = np.array(
        [
            [1, -1],
            [-1, 1]
        ],
        dtype=int
    )

    def __init__(self, out_path: str = "./data_out", **kwargs) -> None:
        # Initailzing parent class (FEMData)
        super().__init__(**kwargs)
        # Output path for the reasult
        self.out_path = out_path
        # Trans post matrix. In case of 2D, it initializes to 1
        self._trans: np.ndarray = np.ones(self.num_elem) if self.dim == 1 \
            else np.zeros([self.num_elem, 2, self.dim * 2])
        # Global stiffness matrix
        self._kg: np.ndarray = np.zeros(
            [self.num_elem, self.dim * 2, self.dim * 2]
        )
        # number of index for the force, displacement, and stress reasult
        self.num_rs_index = self.dim * self.nd.shape[0]
        #  System stiffness matrix
        self._ks: np.ndarray = np.zeros([self.num_rs_index, self.num_rs_index])

    def __calc_kg(self) -> None:
        """Calculates global stiffness matrix
        """
        for i in range(self.num_elem):
            if self.dim == 1:
                self._kg[i] = self.int_e[i] / self.L[i] * self.__tmpK
            else:
                # Shape function variable
                c = np.array(
                    [
                        self.xyz[0][i, 1] - self.xyz[0][i, 0],
                        self.xyz[1][i, 1] - self.xyz[1][i, 0]
                    ]
                )
                if self.dim == 3:
                    np.append(c, self.xyz[2][i, 1] - self.xyz[2][i, 0])
                c = c / self.L[i]
                # Add transfered global postion in to transformation matrix
                self._trans[i][0, :self.dim] = c
                self._trans[i][1, self.dim:] = c
                tmp_kl = self.int_e[i] / self.L[i] * self.__tmpK
                self._kg[i] += self._trans[i].T @ tmp_kl @ self._trans[i]

    def __calc_ks(self) -> None:
        """Calculates system stiffness matrix
        """

        for i in range(self.num_elem):
            if self.dim == 1:
                # Position 1 on system stiffness matrix
                po1 = self.elem[i, 0]
                # Position 2 on system stiffness matrix
                po2 = self.elem[i, 1]
                # Node 1 of the system stiffness matrix
                self._ks[po1, po2] += self._kg[i, 0, 0]
                self._ks[po1, po2] += self._kg[i, 0, 1]
                # Node 2 of the system stiffness matrix
                self._ks[po2, po1] += self._kg[i, 1, 0]
                self._ks[po2, po1] += self._kg[i, 1, 1]
            else:
                # Starting potition 1 on system stiffness matrix
                po1_1 = self.dim * self.elem[i, 0] - self.dim
                # One is added for slicing
                po1_2 = self.dim * self.elem[i, 0]
                # Starting potition 2 on system stiffness matrix
                po2_1 = self.dim * self.elem[i, 1] - self.dim
                # One is added for slicing
                po2_2 = self.dim * self.elem[i, 1]
                # One is added for slicing
                tmp_dim1 = self.dim
                tmp_dim2 = self.dim * 2
                # Node 1 of the eletment
                self._ks[po1_1:po1_2, po1_1:po1_2] += \
                    self._kg[i][0:tmp_dim1, 0:tmp_dim1]
                self._ks[po1_1:po1_2, po2_1:po2_2] += \
                    self._kg[i][0:tmp_dim1, self.dim:tmp_dim2]
                # Node 2 of the eletment
                self._ks[po2_1:po2_2, po1_1:po1_2] += \
                    self._kg[i][self.dim:tmp_dim2, 0:tmp_dim1]
                self._ks[po2_1:po2_2, po2_1:po2_2] += \
                    self._kg[i][self.dim:tmp_dim2, self.dim:tmp_dim2]

    def _calc_stiffness(self) -> None:
        self.__calc_kg()
        self.__calc_ks()

    def _data_label(self, tmp_str) -> list[str]:
        tmp_out = []
        for i in range(0, self.num_rs_index, self.dim):
            tmp_out.append(tmp_str + str(i + 1) + "x")
            if self.dim >= 2:
                tmp_out.append(tmp_str + str(i + 2) + "y")
            if self.dim == 3:
                tmp_out.append(tmp_str + str(i + 3) + "z")
        return tmp_out

    def _save_data_FD(
        self, data_in: np.ndarray, col_name: str, index_name: str,
        unit: str, name: str, type: str, sig_fig: str
    ) -> None:
        out_row: list[str] = [" ".join([col_name, "[" + unit + "]"])]
        out_col: list[str] = self._data_label(index_name)
        save_path = ReadWrite.ch_path(self.out_path)
        ExportData(save_path).save_to_file(
            fs_name=name, fs_type=type, sig_fig=sig_fig,
            data=data_in, columns=out_row, index=out_col
        )

    def _save_data_stress(
        self, data_in: np.ndarray, unit: str, name: str, type: str, sig_fig: str
    ) -> None:
        out_row: list[str] = [" ".join(["Stress", "[" + unit + "]"])]
        out_col: list[str] = []
        for i in range(self.num_rs_index):
            out_col.append(" ".join(["Elements", "(" + ") "]))
