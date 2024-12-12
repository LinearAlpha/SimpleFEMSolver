import copy
import numpy as np
from SimpleFEMSolver.core import BCData


class SolverCore(BCData):
    # Class attribute
    __tmp_k: np.ndarray = np.array([[1, -1], [-1, 1]], dtype=int)

    def __init__(self, **kwargs) -> None:
        # Initializing parent class
        super().__init__(**kwargs)

        self._trans: list[np.ndarray]  # Transpose matrix
        self._kl: list[np.ndarray]  # Local stiffness matrix
        self._kg: list[np.ndarray]  # Global stiffness matrix
        self._ks: np.ndarray  # System stiffness matrix

    def __calc_kg(self) -> None:
        """Calculates global stiffness matrix of each elements"""

        for i in range(self._num_elem):
            # Local stiffness matrix
            self._kl.append(self._internal_e[i] / self._elem_l * self.__tmp_k)

            # Calculate global stiffness matrix based on the dimension
            if self._dim == 1:
                self._kg.append(self._kl[i])
                self._trans.append(np.array(1))

            else:
                # Create shape function
                sh_matrix: np.ndarray = np.zeros(self._dim)
                for j in range(self._dim):
                    sh_matrix[i] = self._xyz[j][i, 1] - self._xyz[j][i, 0]

                # Set transpose matrix
                trans_hold: np.ndarray = np.zeros(self._dim)
                self._trans.append(
                    np.array(
                        [
                            np.append(trans_hold, sh_matrix),
                            np.append(sh_matrix, trans_hold),
                        ]
                    )
                )

                # Calculate global stiffness matrix
                self._kg.append(
                    self._trans[i].T @ self._kl[i] @ self._trans[i]
                )

    def __calc_ks(self) -> None:
        """Calculate system stiffness matrix"""

        # Initialize system stiffness matrix
        len_bc: int = self.__init_val_bc().shape[0]
        self._ks = np.zeros([len_bc, len_bc])

        for i in range(self._num_elem):
            if self._dim == 1:
                # System stiffness matrix position mapper
                po1: int = self._elements[i, 0]  # Position 1
                po2: int = self._elements[i, 1]  # Position 2

                # Mapping first node 1 in to stiffness matrix
                self._ks[po1, po2] += self._kg[i][0, 0]
                self._ks[po1, po2] += self._kg[i][0, 1]

                # Mapping first node 2 in to stiffness matrix
                self._ks[po2, po1] += self._kg[i][1, 0]
                self._ks[po2, po1] += self._kg[i][1, 1]

            # In case of 2D and 3D
            else:
                # Setting position in the system stiffness matrix
                # Position 1 start
                po1_1: int = self._dim * self._elements[i, 0] - self._dim
                # Position 1 end
                po1_2: int = self._dim * self._elements[i, 0]
                # Position 2 start
                po2_1: int = self._dim * self._elements[i, 1] - self._dim
                # Position 2 start
                po2_2: int = self._dim * self._elements[i, 1]

                # Slicing position for global stiffness matrix
                kg_po1: int = self._dim  # Position 1
                kg_po2: int = self._dim * 2  # Position 2

                # Node 1 of the element
                self._ks[po1_1:po1_2, po1_1:po1_2] += self._kg[i][
                    0:kg_po1, 0:kg_po1
                ]
                self._ks[po1_1:po1_2, po2_1:po2_2] += self._kg[i][
                    0:kg_po1, self._dim : kg_po2
                ]

                # Node 2 of elements
                self._ks[po2_1:po2_2, po1_1:po1_2] += self._kg[i][
                    self._dim : kg_po2, 0:kg_po1
                ]
                self._ks[po2_1:po2_2, po2_1:po2_2] += self._kg[i][
                    self._dim : kg_po2, self._dim : kg_po2
                ]

    def __calc_force_disp(self) -> None:
        """Calculates force and displacement of each elements"""

        tmp_ks: np.ndarray = copy.copy(self._ks)
        tmp_bc_f: np.ndarray = self._bc_force[self._kn_bc_force]

        # Parse section need for calculation
        tmp_ks = tmp_ks[:, not self._kn_bc_disp]
        tmp_ks = tmp_ks[self._kn_bc_force, :]

        # To cover case when displacement boundary condition is not zero
        for i, flag_disp in enumerate(self._kn_bc_disp):
            if flag_disp:
                tmp_bc_f -= self._ks[self._kn_bc_force, i] * self._bc_disp[i]

        # Calculate elongation of each elements
        self.displacement = self._bc_disp
        self.displacement[not self._kn_bc_disp] = tmp_ks / tmp_bc_f

        # Calculate force of each elements
        self.force = self._ks * self.displacement

    def __calc_stress(self) -> None:
        """Calculates stress of each elements"""

        # Initialize array to hold stress at each element
        self.stress = np.zeros([self._num_elem, 1])

        # Calculate stress
        for i in range(self._num_elem):
            # Position map to parse displacement for current element
            lo_map: np.ndarray = self._elements[i, :] * self._dim
            lo_start: np.ndarray = lo_map - self._dim

            # Parsed displacement for calculation
            tmp_disp: np.ndarray = np.array(
                [
                    [self.displacement[lo_start[0], lo_map[0]]],
                    [self.displacement[lo_start[1], lo_map[1]]],
                ]
            )

            # Inverse length of current element
            tmp_arr: np.ndarray = np.array(
                [-1 / self._elem_l[i], 1 / self._elem_l[i]]
            )

            # Calculate stress of each elements
            self.stress[i] = self._elem_elastic[i] * tmp_arr @ tmp_disp

    def solve(self) -> None:
        """Run FEM calculation"""

        self.__calc_kg()
        self.__calc_ks()
        self.__calc_force_disp()
        self.__calc_stress()
