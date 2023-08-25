from pathlib import Path
import numpy as np
import pandas as pd

class NdElem:
    # Class attribute
    fs_name_de: list = ["node", "elements"] # Default file name
    fs_type_de: str = "csv" # Default file type
    # Initializing None type, so I can use to check if list type of input 
    # is None or not
    _NoneType = type(None)

    # Class constructor
    def __init__(
            self, nd: list = None, elem: list = None, path: str = None,
            fs_name: list = None, fs_type: str = None
        ) -> None:
        """Class constructer.
        This class defaults all of the function inputs being optional since
        it can be set neither by directly plugging in node and elements 
        information by Python list nor by reading CSV or Excel files.

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

        # Instance attributes 
        self.nd: np.ndarray # Node (coordinate of each node)
        self.elem: np.ndarray # Element (connection between node)
        self.num_elem: int # Number of elements
        self.dim: int # Dimention of the problem
        self.L: np.ndarray # Lenght of each elements
        self.xyz: np.ndarray # Coordinate of elements
        self.nd_set2: np.ndarray = None# Second set of node array
        self.L_set2: np.ndarray = None # Second set of lenght array
        # Lenght difference between original and deformed lenght
        self.diff_L: np.ndarray = None
        self.xyz_set2: np.ndarray = None # Second set of xyz array

        if path != None:
            self.set_by_files(path, fs_name, fs_type)
        elif ~isinstance(nd, self._NoneType) & \
            ~isinstance(elem, self._NoneType):
            self.set_by_inputs(nd, elem)

    def __arr_ck_shape(
            self, tmp_arr: np.ndarray, num_max_row: int
        ) -> np.ndarray:
        """Private function. This function assumes user has right data, but
        filp the row and colume
        It checks input arrays row is not larger then num_max_row. If it is
        larger then max row, it takes transepose to change shape that is using
        in this class

        Args:
            tmp_arr (np.ndarray): Input array to check shape
            num_max_col (int): Max numer of row

        Returns:
            np.ndarray: Converted array
        """

        return tmp_arr if tmp_arr.shape[1] <= num_max_row \
            else np.transpose(tmp_arr)

    def _to_numpy_arr(self, tmp_in: list) -> np.ndarray:
        """Checks if input array is numpy array, if is not then conver to
        numpy array

        Args:
            tmp_in (list): Array input that need to check

        Returns:
            np.ndarray: Converted array
        """

        return tmp_in if isinstance(tmp_in, np.ndarray) else np.asarray(tmp_in)

    def __set_xyz(self, nd: list = None) -> np.ndarray:
        """Format and initialize the elements into XYZ(cartesian coordinate)
        If there is no inputs, it will use class instance attributes to
        set variable.
        Format of xyz
        [[[x1, x2], ....], [[y1, y2], ....], [[z1, z2], ....]]
        The variavle is based on elements

        Args:
            nd (list, optional): Node that need to map. Defaults to None.
        """

        # In case there is no input
        if isinstance(nd, self._NoneType):
            nd = self.nd

        # Formating each element by cartesian coordinate
        tmp_xyz: np.ndarray = np.zeros(
            [2 if self.dim < 3 else 3, self.num_elem, 2]
        )
        for i in range(self.num_elem):
            tmp_elem = self.elem[i] - 1
            for j in range(self.dim):
                tmp_xyz[j, i, :] = [nd[tmp_elem[0], j], nd[tmp_elem[1], j]]
        return tmp_xyz

    def __calc_Len(self, tmp_xyz: np.ndarray = None) -> np.ndarray:
        """Calculates lenght of each elements

        Args:
            tmp_xyz (np.ndarray, optional): _description_. Defaults to None.

        Returns:
            np.ndarray: _description_
        """

        # Case when after FEM calculation, setting second set of node lenght
        if not isinstance(tmp_xyz, self._NoneType):
            tmp_shape = tmp_xyz.shape
            dim = tmp_shape[0]
            num_elem = tmp_shape[1]
        else:
            tmp_xyz = self.xyz
            dim = self.dim
            num_elem = self.num_elem
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

    def set_by_inputs(self, nd: list, elem: list) -> None:
        """Setting Node elemtns of the system by inputs.
        The format this function used is
        nd = [[x1, y1,], [x2, y2], ...] || [[x1, y1, z1], [x2, y2, z3], ...]
        elem = [[nd1, nd2], [nd3, nd4], ...]

        Args:
            nd (list): Node of the system
            elem (list): Elements of the system
        """

        self.nd = self.__arr_ck_shape(self._to_numpy_arr(nd), 3)
        self.elem = self.__arr_ck_shape(self._to_numpy_arr(elem), 2)
        self.dim = self.nd.shape[1]
        self.num_elem = self.elem.shape[0]
        self.xyz = self.__set_xyz()
        self.L = self.__calc_Len()

    # Set node and element by file
    def set_by_files(
            self, path: str, fs_name: list = None, fs_type: str = "csv"
        ) -> None:

        # Check which slash symbol it uses 
        fs_format = "\\" if "\\" in path else "/"
        # Check if there is file name input, then process it
        """
        Need to add functionavility that when user gave file name with 
        extention
        """
        # Checking if there is file name input
        if fs_name == None:
            fs_name = self.fs_name_de        
        else:
            # Chekcking there is more then 2 file name
            if len(fs_name) > 2:
                raise IndexError("More then two file names")
        if fs_type == None:
            fs_type = self.fs_type_de
        # Setting path for data files, and varlidates if file excist
        for i in range(len(fs_name)):
            tmp_path = path + fs_format + fs_name[i] + "." + fs_type
            if Path(tmp_path).is_file():
                fs_name[i] = Path(tmp_path)
            else:
                msg_err = fs_name[i] + fs_type + " is not exist."
                raise ValueError(msg_err)
        # Read data files and set to node and element
        if fs_type == "csv":
            tmp_nd = pd.read_csv(fs_name[0]).to_numpy()
            tmp_elem = pd.read_csv(fs_name[1]).to_numpy()
        else:
            tmp_nd = pd.read_excel(fs_name[0]).to_numpy()
            tmp_elem = pd.read_excel(fs_name[1]).to_numpy()
        self.set_by_inputs(tmp_nd, tmp_elem)

    # Adding new node after deformation
    def new_nd(self, elongation: np.ndarray) -> None:
        """Adding new set of node, lenght and xyz coolfinate based on
        enlingation. Which is how muuch system has been elningated after
        deformation.

        Args:
            elongation (np.ndarray): Elongation of each node on the system
        """

        self.nd_set2 = np.zeros(self.nd.shape)
        # Temperatly mapping elongation into node set2
        for i in range(self.nd.shape[0]):
            po = i * self.dim
            po_diff = po + self.dim
            self.nd_set2[i] = elongation[po:po_diff].reshape(1, self.dim)
        self.nd_set2 += self.nd # Find new node location based on original node
        # Setting xyz, it must be called before calling lenght calcualation
        self.xyz_set2 = self.__set_xyz(self.nd_set2)
        self.L_set2 = self.__calc_Len(self.xyz_set2)
        self.diff_L = self.L_set2 - self.L
