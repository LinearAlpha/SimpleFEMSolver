from dataclasses import dataclass
import numpy as np
from SimpleFEMSolver.core import NodeElement


@dataclass
class BCInputs:
    """
    Data class that holds boundary condition inputs
    """

    def __init__(
        self,
        node_num: int,
        x: int | float = np.nan,
        y: int | float = np.nan,
        z: int | float = np.nan,
    ) -> None:
        self.node_num: int = node_num  # Node number for this input

        self.x: int | float  # X value of boundary condition
        self.flag_x: bool = False  # Flag to check if X value was given
        if not np.isnan(x):  # Only set valuable when there is input
            self.x = x
            self.flag_x = True

        self.y: int | float  # Y value of boundary condition
        self.flag_y: bool = False  # Flag to check if Y value was given
        if not np.isnan(y):  # Only set valuable when there is input
            self.y = y
            self.flag_y = True

        self.z: int | float  # Z value of boundary condition
        self.flag_z: bool = False  # Flag to check if Z value was given
        if not np.isnan(z):  # Only set valuable when there is input
            self.z = z
            self.flag_z = True


class BCData(NodeElement, BCInputs):
    """
    Class that holds boundary condition data for force and displacement. Also,
    hold calculated force and displacement data
    """

    def __init__(self, **kwargs) -> None:
        # Initialing parent class (Node Elements)
        super().__init__(**kwargs)

        # Force related valuables
        # Temperately holds BC inputs before initialize
        self.__tmp_bc_f: list[BCInputs] = []
        self._bc_force: np.ndarray
        self._kn_bc_force: np.ndarray
        self.__flag_bc_force: bool = False

        # Displacement replated valuables
        # Temperately holds BC inputs before initialize
        self.__tmp_bc_disp: list[BCInputs] = []
        self._bc_disp: np.ndarray
        self._kn_bc_disp: np.ndarray
        self.__flag_bc_disp: bool = False

        # Calculated result
        self.force: np.ndarray
        self.displacement: np.ndarray
        self.stress: np.ndarray

    def __init_kn_bc(self) -> np.ndarray:
        """Initializes known boundary condition array

        Returns:
            np.ndarray: Initialized known boundary condition
        """

        return np.zeros([self._dim * self.node.shape[0], 1], dtype=bool)

    def __init_val_bc(self) -> np.ndarray:
        """Initializes boundary condition array

        Returns:
            np.ndarray: Initialized boundary condition
        """

        return np.zeros([self._dim * self.node.shape[0], 1])

    def __bc_mapper(
        self,
        bc_val_in: np.ndarray,
        kn_bc_in: np.ndarray,
        bc_inputs: list[BCInputs],
    ) -> None:
        """Mapping boundary condition inputs into calculable array

        Args:
            bc_val_in (np.ndarray): Boundary condition valuable array to map.
            kn_bc_in (np.ndarray): Known boundary condition to map.
            bc_inputs (list[BCInputs]): List of user input for the boundary
            condition.
        """

        for tmp_input in bc_inputs:
            # Based position to map into array
            end_position: int = tmp_input.node_num * self.dim
            cur_po: int  # Current position mapper based on the axis

            # Update valuables and known BC only when there was user input
            if tmp_input.flag_x:
                cur_po = end_position - self.dim - 1
                bc_val_in[cur_po] = tmp_input.x
                kn_bc_in[cur_po] = True

            if tmp_input.flag_y:
                cur_po = end_position - self.dim - 2
                bc_val_in[cur_po] = tmp_input.y
                kn_bc_in[cur_po] = True

            if tmp_input.flag_z:
                cur_po = end_position - self.dim - 3
                bc_val_in[cur_po] = tmp_input.z
                kn_bc_in[cur_po] = True

    def bc_fore_input(
        self,
        node_num: int = -1,
        x: int | float = np.nan,
        y: int | float = np.nan,
        z: int | float = np.nan,
        batch_inputs: list[BCInputs] = [],
    ) -> None:
        """Setter for Force boundary condition.

        Args:
            node_num (int, optional): Node number. Defaults to -1
            x (int | float, optional): X axis input. Defaults to np.nan.
            y (int | float, optional): Y axis input. Defaults to np.nan.
            z (int | float, optional): Z axis input. Defaults to np.nan.
            batch_inputs (list[BCInputs], optional): Only yser when user want
             to set boundary condition at onces. Defaults to [].
        """

        if not self.__flag_bc_force:
            self.__flag_bc_force = True

        if not batch_inputs:
            self.__tmp_bc_f.append(BCInputs(node_num, x, y, z))
        else:
            self.__tmp_bc_f.extend(batch_inputs)

    def bc_disp_input(
        self,
        node_num: int = -1,
        x: int | float = np.nan,
        y: int | float = np.nan,
        z: int | float = np.nan,
        batch_inputs: list[BCInputs] = [],
    ) -> None:
        """
        Setter for Displacement boundary condition.

        Args:
            node_num (int, optional): Node number. Defaults to -1
            x (int | float, optional): X axis input. Defaults to np.nan.
            y (int | float, optional): Y axis input. Defaults to np.nan.
            z (int | float, optional): Z axis input. Defaults to np.nan.
            batch_inputs (list[BCInputs], optional): Only yser when user want
             to set boundary condition at onces. Defaults to [].
        """

        if not self.__flag_bc_disp:
            self.__flag_bc_disp = True

        if not batch_inputs:
            self.__tmp_bc_disp.append(BCInputs(node_num, x, y, z))
        else:
            self.__tmp_bc_disp.extend(batch_inputs)

    def init_bc(self) -> None:
        """initialize boundary condition based on the user input

        Raises:
            Exception: When displacement boundary condition was not given
        """

        # Initialize with 0 for bouldery condition for force and
        # displacement
        self._bc_force = self.__init_val_bc()
        self._bc_disp = self.__init_val_bc()

        # Initialize with False to flagging bc inputs
        self._kn_bc_force = self.__init_kn_bc()
        self._kn_bc_disp = self.__init_kn_bc()

        # Initialize force and displacement boundary condition based on
        # the input
        if self.__flag_bc_force:
            self.__bc_mapper(
                self._bc_force, self._kn_bc_force, self.__tmp_bc_f
            )

        if self.__flag_bc_disp:
            self.__bc_mapper(
                self._bc_disp, self._kn_bc_disp, self.__tmp_bc_disp
            )

        # The initialize process only can complete with displacement user input
        if not self.__flag_bc_disp:
            raise Exception(
                "Boundary condition for displacement was not given"
            )
        else:
            self._kn_bc_force = np.invert(self._kn_bc_disp)

    @property
    def bc_force(self) -> np.ndarray:
        return self._bc_force

    @property
    def bc_disp(self) -> np.ndarray:
        return self._bc_disp
