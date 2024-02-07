import numpy as np
import pandas as pd


class NdElem:
    # Class attribute
    fs_name_de: list[str, str] = ["nodes", "elements"]  # Default file name
    fs_type_de: str = "csv"  # Default file extention
    # Initializing None type, so it can check None type inside of is in case it
    # needed
    _NoneType = type(None)

    # Class constructor
    def __init__(
        self,
        node: list[list[int]] | list[list[float]] | np.ndarray = None,
        elem: list[int] | np.ndarray = None,
        project_path: str = None,
        fs_name: list[str] = None,
        fs_type: str = None
    ) -> None:

        # Instance attributes
        self.dim: int  # Dimention of the system
        self.nd: np.ndarray  # Node (coordinate of each node in XYZ)
        # Second set of node (after calcualtion)
        self.nd2: np.ndarray = None
        self.elem: np.ndarray  # Element (connection between node)
        self.num_elem: int  # Number of elements
        self.L: np.ndarray  # Lenght of each elements
        # Second set of lenght of each elements (after calculation)
        self.L2: np.ndarray = None
        self.diff_L: np.ndarray = None  # Difference between lenght set 1 & 2
        self.xyz: np.ndarray  # XYZ coordinate of elements
        # Second set of XYZ coordinate of elements
        self.xyz2: np.ndarray = None

        if project_path != None:
            self.set_by_files(project_path, fs_name, fs_type)
        elif not isinstance(node, self._NoneType) and \
                not isinstance(elem, self._NoneType):
            self.set_by_inputs(node, elem)

    def __arr_ck_shape(
        self, tmp_arr: np.ndarray, num_max_row: int
    ) -> np.ndarray:
        """
        Private function. 
        It transpose matirx if row of input matrix is larger the "num_max_row"

        Args:
            tmp_arr (np.ndarray): Input array(matrix) to check
            num_max_col (int): Max numer of row

        Returns:
            np.ndarray: Transposed matrix if row excced max row input
        """
        return tmp_arr if tmp_arr.shape[1] <= num_max_row \
            else np.transpose(tmp_arr)

    def __set_xyz(self, nd_in: list = None) -> np.ndarray:
        """
        Private function
        Initializes elements into cartesian coordinate(XYZ-axis) based on node
        inputs.

        Output data format:
            [
                [
                    [x1, x2], ....
                ],
                [
                    [y1, y2], ....
                ], 
                [
                    [z1, z2], ....
                ]
            ]
            The data will be in the multidimensional matrix that each index 
            set(as example, output[dim, element number, :]) is represent 
            cartesian coordinate of the each element ar each axis

        Args:
            nd (list, optional): Node that need to map. Defaults to None.

        Returns:
            np.ndarray: Multidimensional numpy matrix that is inixialized 
        """
        # In case there is no input node, use class attribute
        if isinstance(nd_in, self._NoneType):
            nd_in = self.nd
        # Initializing matrix into data format
        tmp_xyz: np.ndarray = np.zeros(
            [
                2 if self.dim < 3 else 3, self.num_elem, 2
            ]
        )
        # Mapping coordinate data input mtrix
        for i in range(self.num_elem):
            tmp_elem: int = self.elem[i] - 1  # To correctly map index location
            for j in range(self.dim):
                tmp_xyz[j, i, :] = [
                    nd_in[tmp_elem[0], j], nd_in[tmp_elem[1], j]
                ]
        return tmp_xyz

    def __calc_Len(self, tmp_xyz: np.ndarray = None) -> np.ndarray:
        """
        Calculate lenght of each elements

        Args:
            tmp_xyz (np.ndarray, optional): Carcesian coordinate of each
                elements. See __set_XYZ function to check data format.
                Defaults to None.

        Returns:
            np.ndarray: Calculated lenght of each elements
        """
        # Case when after FEM calculation, setting second set of node lenght
        if not isinstance(tmp_xyz, self._NoneType):
            tmp_shape = tmp_xyz.shape
            dim: int = tmp_shape[0]
            num_elem: int = tmp_shape[1]
        else:
            tmp_xyz = self.xyz
            dim = self.dim
            num_elem: int = self.num_elem
        tmp_L: np.ndarray = np.zeros([num_elem, 1])
        # calcualte each elements lenght
        for i in range(num_elem):
            tmp_L[i] = tmp_xyz[0, i, 1] - tmp_xyz[0, i, 0]
            if dim >= 1:
                tmp_L[i] = tmp_L[i] ** 2 + \
                    (tmp_xyz[1, i, 1] - tmp_xyz[1, i, 0]) ** 2
                if dim == 3:
                    tmp_L[i] += (tmp_xyz[2, i, 1] - tmp_xyz[2, i, 0]) ** 2
            tmp_L[i] = np.sqrt(tmp_L[i])
        return tmp_L

    def _to_numpy_arr(
        self,
        tmp_in: list[float] | list[int] | np.ndarray
    ) -> np.ndarray:
        """
        Private to class and inheritence
        Checks input array is numpy matrix. If it is no, convert to 
        numpy array.

        Args:
            tmp_in (list[floaft] | list[int] | np.ndarray): Array that might
                need to convert to numpy array(matrix)

        Returns:
            np.ndarray: Converted numpy array(matrix)
        """
        return tmp_in if isinstance(tmp_in, np.ndarray) else np.asarray(tmp_in)

    def set_by_inputs(
        self,
        nd: list[int] | list[float] | np.ndarray,
        elem: list[int] | np.ndarray
    ) -> None:
        """Construction function for class instance

        Args:
            nd (list[int] | list[float] | np.ndarray): Node input
            elem (list[int] | np.ndarray): Elements inputs
        """
        self.nd = self.__arr_ck_shape(self._to_numpy_arr(nd), 3)
        self.elem = self.__arr_ck_shape(self._to_numpy_arr(elem), 2)
        self.dim = self.nd.shape[1]
        self.num_elem = self.elem.shape[0]
        self.xyz = self.__set_xyz()
        self.L = self.__calc_Len()

    def set_by_files(
        self, in_path: str, fs_name: list = None, fs_type: str = "csv"
    ) -> None:
        """
        Under construction
        """
        # # Check which slash symbol it uses
        # fs_format = "\\" if "\\" in in_path else "/"
        # # Check if there is file name input, then process it
        # """
        # Need to add functionavility that when user gave file name with
        # extention
        # """
        # # Checking if there is file name input
        # if fs_name == None:
        #     fs_name = self.fs_name_de
        # else:
        #     # Chekcking there is more then 2 file name
        #     if len(fs_name) > 2:
        #         raise IndexError("More then two file names")
        # if fs_type == None:
        #     fs_type = self.fs_type_de
        # # Setting in_path for data files, and varlidates if file excist
        # for i in range(len(fs_name)):
        #     tmp_in_path = in_path + fs_format + fs_name[i] + "." + fs_type
        #     if in_path(tmp_in_path).is_file():
        #         fs_name[i] = in_path(tmp_in_path)
        #     else:
        #         msg_err = fs_name[i] + fs_type + " is not exist."
        #         raise ValueError(msg_err)
        # # Read data files and set to node and element
        # if fs_type == "csv":
        #     tmp_nd = pd.read_csv(fs_name[0]).to_numpy()
        #     tmp_elem = pd.read_csv(fs_name[1]).to_numpy()
        # else:
        #     tmp_nd = pd.read_excel(fs_name[0]).to_numpy()
        #     tmp_elem = pd.read_excel(fs_name[1]).to_numpy()
        # self.set_by_inputs(tmp_nd, tmp_elem)

    # Adding new node after deformation
    def new_nd(self, elongation: np.ndarray) -> None:
        """Adding new set of node, lenght and xyz coolfinate based on
        enlingation. Which is how muuch system has been elningated after
        deformation.

        Args:
            elongation (np.ndarray): Elongation of each node on the system
        """

        self.nd2 = np.zeros(self.nd.shape)
        # Temperatly mapping elongation into node set2
        for i in range(self.nd.shape[0]):
            po = i * self.dim
            po_diff = po + self.dim
            self.nd2[i] = elongation[po:po_diff].reshape(1, self.dim)
        self.nd2 += self.nd  # Find new node location based on original node
        # Setting xyz, it must be called before calling lenght calcualation
        self.xyz2 = self.__set_xyz(self.nd2)
        self.L2 = self.__calc_Len(self.xyz2)
        self.diff_L = self.L2 - self.L
