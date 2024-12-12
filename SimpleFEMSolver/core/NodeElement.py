# Installed packages
import numpy as np


class NodeElement:

    # Predefined pandas dataframe header
    __ND_HEAD: list[str] = [
        "x",
        "y",
        "z",
    ]

    def __init__(
        self,
        node: list[int] | list[float] | np.ndarray = [],
        element: list[int] | np.ndarray = [],
        elem_area: int | float | list[int] | list[float] = [],
        elastic_m: int | float | list[int] | list[float] = [],
        unit_force: str = "N",
        unit_length: str = "m",
    ) -> None:

        # Instance attributes
        # Node valuables
        self._dim: int  # Dimension of the system
        self._node: np.ndarray  # Node (coordinate of each node in XYZ)
        self._node_deform: np.ndarray  # Node location after deformation

        # Elements valuables
        self._elements: np.ndarray  # Element (connection between node)
        self._num_elem: int  # Number of elements
        self._elem_l: np.ndarray  # Length of each elements
        # Length of each element after deformation
        self._elem_l_deform: np.ndarray
        self._elem_l_diff: np.ndarray  # Difference of each node
        self._elem_area: np.ndarray  # Area of each element
        self._elem_elastic: np.ndarray  # Elastic modules of each elements
        self._internal_e: np.ndarray  # Internal Energy

        # Node coordinate mapped with connection of element
        self._xyz: np.ndarray
        self._xyz_deform: np.ndarray  # Node coordinate after deformation

        # Pandas data from header
        self.node_header: list[str]
        self.elements_header: list[str] = ["Element 1", "Element 2"]

        # Set uit of the system
        self.sys_unit: dict[str, str] = {
            "force": unit_force,
            "length": unit_length,
        }

        # Flag what checks if deformation information has been updated
        self.__flag_deform: bool = False

        # Initialize valuable
        if (
            (not node)
            and (not element)
            and (not elem_area)
            and (not elastic_m)
        ):
            self.set_nd_elem(node, element, elem_area, elastic_m)

    def __check_arr_shape(
        self, arr2check: np.ndarray, max_row: int
    ) -> np.ndarray:
        """Private function
        Check if numpy array is right shape based on the max row number
        provided from user. If row is larger then input, take transpose.

        Args:
            arr2check (np.ndarray): Numpy array to change shape of it
            max_row (int): Max number of row what should input function need to
            be

        Returns:
            np.ndarray: Transposed numpy array
        """

        flag: bool = arr2check.shape[1] <= max_row
        return arr2check if flag else arr2check.T

    def __set_xyz(self, nd2xyz: np.ndarray = np.array([])) -> np.ndarray:
        """Private function
        Set elements connection with node coordinate.

        Output data format:
        [
            [[x1, x2], ...],
            [[y1, y2], ...],
            [[z1, z2], ...]
        ]
        Each column represent each element connection by cartesian coordinate.

        Input node is not required. If node data was not given, the function
        will be use node data from class valuable.

        Args:
            nd2xyz (np.ndarray, optional): Node data to use.
            Defaults to np.array([]).

        Returns:
            np.ndarray: Element connection data what mapped with node data.
        """

        # Case, when node data was not given as a function input.
        if nd2xyz.size == 0:
            nd2xyz = self._node

        # initialize array to hold coordinate information
        xyz_out: np.ndarray = np.zeros([self._dim, self._num_elem, 2])

        # Map each node into coordinate based on elements (Node connections)
        for i, tmp_arr in enumerate(self._elements):
            tmp_arr -= 1

            for j in range(self._dim):
                xyz_out[j, i, :] = [
                    nd2xyz[tmp_arr[0], j],
                    nd2xyz[tmp_arr[1], j],
                ]

        return xyz_out  # Mapping is complete

    def __calc_len(self, xyz2calc: np.ndarray = np.array([])) -> np.ndarray:
        """Private function
        Calculates length of each elements

        The input data only intend to use when need to calculate deformed
        elements length.

        Args:
            xyz2calc (np.ndarray, optional): Elements connection data based on
            cartesian coordinate. Defaults to np.array([]).

        Returns:
            np.ndarray: Calculated length of each elements.
        """

        # If there was not given user input, copy valuable from class
        if xyz2calc.size == 0:
            xyz2calc = self._xyz

        # Initialize to hold calculated elements length
        out_l: np.ndarray = np.zeros([self._num_elem, 1])

        # Calculate length of each elements
        for i in range(self._num_elem):
            # Calculate for each direction (XYZ coordinate)
            for j in range(self._dim):
                out_l[i] += (xyz2calc[j, i, 1] - xyz2calc[j, i, 0]) ** 2
            out_l[i] = np.sqrt(out_l)

        return out_l

    def __set_elem_property(
        self, elem_prop: int | float | list[int] | list[float]
    ) -> np.ndarray:

        # Initialize array to hold each elements property
        prop_tmp: np.ndarray = np.zeros([self._num_elem, 1])

        if isinstance(elem_prop, int) or isinstance(elem_prop, float):
            prop_tmp[prop_tmp == 0] = elem_prop

        else:
            for tmp_loop in elem_prop:
                prop_tmp[tmp_loop[0]] = tmp_loop[1]  # type: ignore

                prop_tmp[prop_tmp == 0] = 1

        return prop_tmp

    def __clear_deform_data(self) -> None:
        """Private function.
        Reset deformed system information. This function is intend to use only
        when set_node and set_elements functions are called.
        """

        self._node_deform = np.array([])
        self._xyz_deform = np.array([])
        self._elem_l_deform = np.array([])
        self._elem_l_diff = np.array([])

    def _to_numpy_arr(
        self, arr2check: list[int] | list[float] | np.ndarray
    ) -> np.ndarray:
        """Private function
        Check if input list is in numpy array, if it is not convert to numpy
        array.

        Args:
            arr2check (list[int] | list[float] | np.ndarray): Input list or
            array to convert

        Returns:
            np.ndarray: Array that converted to numpy
        """

        return (
            arr2check
            if isinstance(arr2check, np.ndarray)
            else np.array(arr2check)
        )

    def set_nd_elem(
        self,
        node: list[int] | list[float] | np.ndarray,
        element: list[int] | np.ndarray,
        elem_area: int | float | list[int] | list[float],
        elastic_m: int | float | list[int] | list[float],
    ) -> None:
        """Public function.
        Initialize class valuables based on node and elements input.

        Args:
            node (list[int] | list[float] | np.ndarray): Node data
            element (list[int] | np.ndarray): Elements data
        """

        self._node = self.__check_arr_shape(self._to_numpy_arr(node), 3)
        self._elements = self.__check_arr_shape(self._to_numpy_arr(element), 2)
        self._dim = self._node.shape[1]
        self.node_header = self.__ND_HEAD[: self._dim]
        self._num_elem = self._elements.shape[0]
        self._xyz = self.__set_xyz()
        self._elem_l = self.__calc_len()
        self._elem_area = self.__set_elem_property(elem_area)
        self._elem_elastic = self.__set_elem_property(elastic_m)
        self._internal_e = self._elem_elastic * self._elem_area

    def update_area(self, lo_elem: int, area: int | float) -> None:
        self._elem_area[lo_elem] = area

    def update_elastic(self, lo_elem: int, ela_m: int | float) -> None:
        self._elem_elastic[lo_elem] = ela_m

    def deformed(self, elongation: np.ndarray) -> None:
        """Receive shifted location of each node and update deformed body
        data in to class valuable.

        Args:
            elongation (np.ndarray): Shift node data
        """

        # Flag that class has deformed body information
        self.__flag_deform = True

        # Initialize node_deform valuable
        self._node_deform = np.zeros(self._node.shape)

        # Mapping elongation information into node data format
        for i in range(self._node.shape[0]):
            po: int = i * self._dim  # Staring position
            po_diff: int = po + self._dim  # End position
            self._node_deform[i] = elongation[po:po_diff].reshape(1, self._dim)

        # Calculate new node coordinate
        self._node_deform += self._node

        # Calculate elongated element coordinate and length
        self._xyz_deform = self.__set_xyz(self._node_deform)
        self._elem_l_deform = self.__calc_len(self._xyz_deform)
        self._elem_l_diff = self._elem_l_diff - self._elem_l

    @property
    def dim(self) -> int:
        return self._dim

    @property
    def node(self) -> np.ndarray:
        return self._node

    @property
    def node_deform(self) -> np.ndarray:
        if self.__flag_deform:
            return self._node_deform
        else:
            return np.array([])

    @node.setter
    def set_node(self, node: list[int] | list[float] | np.ndarray) -> None:
        self._node = self.__check_arr_shape(self._to_numpy_arr(node), 3)
        self._dim = self._node.shape[1]
        self.node_header = self.__ND_HEAD[: self._dim]
        self.__clear_deform_data()

    @property
    def elements(self) -> dict[str, np.ndarray]:
        tmp_elem: dict[str, np.ndarray] = {
            "elem": self._elements,
            "elem_len": self._elem_l,
        }

        if self.__flag_deform:
            tmp_elem.update(
                {
                    "len_deform": self._elem_l_deform,
                    "len_diff": self._elem_l_diff,
                }
            )

        return tmp_elem

    @elements.setter
    def set_elements(self, element: list[int] | np.ndarray):
        self._elements = self.__check_arr_shape(self._to_numpy_arr(element), 2)
        self._num_elem = self._elements.shape[0]
        self._xyz = self.__set_xyz()
        self._elem_l = self.__calc_len()
        self.__clear_deform_data()

    @property
    def area(self) -> np.ndarray:
        return self._elem_area

    @property
    def elastic_modules(self) -> np.ndarray:
        return self._elem_elastic

    @property
    def xyz(self) -> np.ndarray:
        return self._xyz

    @property
    def xyz_deform(self) -> np.ndarray:
        return self._xyz_deform
