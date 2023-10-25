import copy
import numpy as np
from . import NdElem


class EngData(NdElem):
    def __init__(self, sys_unit: dict = None, **kwargs) -> None:
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
        """

        # Initailzing parent class (NdElem)
        super().__init__(**kwargs)
        # Temperate array for Boundery Condition (BC) condition
        self.tmp_bc_arr: np.ndarray = np.zeros([self.dim * len(self.nd), 1])
        # Instance attributes
        # Knwon BC for force, it flags to True when there is force BC.
        self._kn_bc_f: np.ndarray = np.zeros(
            [self.dim * len(self.nd)], dtype=bool
        )
        # Knwon BC for displacement, it flags to True when there is
        # displacement BC.
        self._kn_bc_disp: np.ndarray = copy.deepcopy(self._kn_bc_f)
        self._bc_flag: bool = False  # Flag True when BC has been setted
        # Elastic modules of each elements
        self.ela: np.ndarray = np.zeros([self.num_elem, 1])
        # Area of the each elements
        self.are: np.ndarray = copy.deepcopy(self.ela)
        self.__ela_flag: bool = False  # Flag for Elastic modules
        self.__are_flag: bool = False  # Flag for Area
        self.int_e: np.ndarray  # Internal entergy (Area * Elastic modulus)
        self.bc_f: np.ndarray = copy.deepcopy(self.tmp_bc_arr)  # BC for force
        # BC for displacement
        self.bc_disp: np.ndarray = copy.deepcopy(self.tmp_bc_arr)
        self.sys_unit = sys_unit

    def __set_unit(self) -> None:
        if isinstance(self.sys_unit, self._NoneType):
            self.sys_unit = {"lenght": "mm", "force": "N"}
        else:
            if ~("lenght" in self.sys_unit.key()):
                pass

    def __to_bc_shape(self, tmp_in: list) -> list[np.ndarray, np.ndarray]:
        """Converts user inputs into shape of bounderty condtion.
        This function assaume data format as below
        tmp_in = [[tmp_x], [tmp_y], ...]

        Args:
            tmp_in (list): Input of boundery condition

        Returns:
            list: return format is showin below
            [tmp_out: np.ndarray, out_bool: np.ndarray]
            tmp_out - formatted array as N x 1 araay
            out_bool - similer to tmo_out, but boolian to indicate with BC
                       was given by user input
        """

        # Initializes the outputs of this functions.
        out_bool: np.ndarray = np.zeros([self.dim * len(self.nd)], dtype=bool)
        tmp_out: np.ndarray = copy.deepcopy(self.tmp_bc_arr)
        for i in range(len(tmp_in)):
            # If object was None, when there was no BC on that axis
            if not isinstance(tmp_in[i], self._NoneType):
                tmp = self._to_numpy_arr(tmp_in[i])  # Conver to numpy array
                for j in range(len(tmp)):
                    tmp_lo = int((tmp[j, 0] * self.dim) - (self.dim - i))
                    tmp_out[tmp_lo] = tmp[j, 1]
                    out_bool[tmp_lo] = True
        return [tmp_out, out_bool]  # Rrturing formatted array

    def __set_property(self, tmp_val: list, tmp_in: list) -> np.ndarray:
        """Setting system properties into desired format

        Args:
            tmp_val (list): Value that need to set or update
            tmp_in (list): User input of property

        Returns:
            np.ndarray: Updated or initialized system propery
        """

        tmp_in = self._to_numpy_arr(tmp_in)
        if tmp_in.size == 1:
            tmp_val[:] = tmp_in
        else:
            for tmp_arr in tmp_in:
                tmp_val[tmp_arr[0] - 1] = tmp_arr[1]
        return tmp_val

    def __calc_int_energy(self) -> None:
        """Calculates internal energy on the system
        """

        if self.__ela_flag & self.__are_flag:
            self.int_e = self.ela * self.are

    def set_bc(self, bc_disp_in: list, bc_f_in: list = None) -> None:
        """Setting Bounderty conditions.

        Args:
            bc_disp_in (list): Boundery condition of displacement
            bc_f_in (list, optional): Boundery condition of force.
                                      Defaults to None.
        """

        self.bc_disp, self._kn_bc_disp = self.__to_bc_shape(bc_disp_in)
        if not isinstance(bc_f_in, self._NoneType):
            self.bc_f, self._kn_bc_f = self.__to_bc_shape(bc_f_in)
        # Based on the FEM
        self._kn_bc_f = np.invert(self._kn_bc_disp)
        self._bc_flag = True

    def set_eng_prop(self, ela_in: list, are_in: list) -> None:
        """Setting engineering properties of the system. If only one valueable
        is given by input, it will initialize entire array by that values.
        All of the input valiavle format assumes as
        Case 1 - [val]
        Case 2 - [[elem, val], [elem, val], ....]

        Args:
            ela_in (list): Elastic modulus of the element.
            are_in (list): Area of cross section of element.
        """

        self.ela = self.__set_property(self.ela, ela_in)
        self.__ela_flag = True
        self.are = self.__set_property(self.are, are_in)
        self.__are_flag = True
        self.__calc_int_energy()

    def update_ela(self, ela_in: list) -> None:
        """Updating elastic modulus of the system. The input data format 
        asssumes as
        Case 1 - [val]
        Case 2 - [[elem, val], [elem, val], ....]

        Args:
            ela_in (list): Elastic modulus of the element.
        """

        self.ela = self.__set_property(self.ela, ela_in)
        self.__ela_flag = True  # Flag up!
        self.__calc_int_energy()

    def update_are(self, are_in: list) -> None:
        """Updating area of the system. The input data format asssumes as
        Case 1 - [val]
        Case 2 - [[elem, val], [elem, val], ....]

        Args:
            are_in (list): Area of the element
        """

        self.are = self.__set_property(self.are, are_in)
        self.__are_flag = True  # Flag up!
        self.__calc_int_energy()
