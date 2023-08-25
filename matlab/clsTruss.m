classdef clsTruss < handle
    % clsTruss
    % Author: Min Kim
    % Date: 10/25/21
    % Last edit: 12/13/2021
    % FileName: clasTrStif.m
    % Simulates truss by using FEM.
    %
    % Properties (Public):
    %
    % Methods (Public):
    %

    properties (Access = private)
        T = {}; % Transpose matrix
        Kl = {}; % Local stiffness matrix
        comFlag = false; % Falg that check if calculation is completed
        comFlagSig = false; % Falg that if stress is calculated
        knBC = []; % Known boundery condition
        bcF = []; % Boundery condition of force
        bcDisp = []; % Boundry condition of direction
        E = []; % Elastic modules of each node
        A = []; % Area of each element
        bcFlag = false % Flag that if there is boundery condition input
    end % End of properties (Private)

    properties (Access = private, Constant)
        tmpK = [1, -1; -1, 1];
    end % End of properties (Private, constant)

    properties
        nd = []; % Node
        elem = []; % Element
        dim; % Dimention of the system
        numElem; % Number of the element
        Kg = {}; % Global stiffness matrix
        Ks = []; % System stiffness matrix
        L = []; % length of each elemnt
        eng = []; % Internal Entergy
        nodalDisp = []; %Nodal displacements
        F = []; % Force on each node
        sig = [];
    end % End of propertires

    methods (Access = private)
        function setEng(st, E, A)
            % Set up interal energy for each elements
            %
            % Input:
            % - E: Set up interal energy for each elements
            % - A: Area of each elements

            % Initialzie the internal energy of the system
            if size(E, 1) == 1
                st.E = ones(st.numElem, 1) .* E;
            else
                st.E = E;
            end % End of if
            if size(A, 1) == 1
                st.A = ones(st.numElem, 1) .* A;
            else
                st.A = A;
            end % End of if
            % Set up class variable
            st.eng = st.E .* st.A;
        end % End of function

        function [bc, knBC] = setBC_BG(st, tmpIn)
            % Set up boundery condition
            %
            % Input:
            % - tmpIn: Boundery input variable
            %
            % Output:
            % - bc: Boundery condition
            % - knBC: logical array that indicate with node has input

            % Initialize the returen variable
            bc = zeros(st.dim * size(st.nd, 1), 1);
            knBC = zeros(st.dim * size(st.nd, 1), 1);
            % Check if we need to map input varues or not
            if size(tmpIn, 2) ~= 1
                % Set flag to be true
                st.bcFlag = true;
                % Map input as n x 1 matrix
                for i = 1:size(tmpIn, 1)
                    % End location to map input to Boundery condtion structure
                    map = tmpIn(i, 1) * st.dim;
                    % Satarting position of map
                    mapDiff = map - (st.dim - 1);
                    % Temperatly holds the value that what to map
                    tmpHold = tmpIn(i, 2:st.dim + 1).';
                    % Check is there only one know BC
                    flag = isnan(tmpHold);
                    if any(flag == true); tmpHold(flag) = 0; end
                    % Mapping to system variable
                    bc(mapDiff:map) = tmpHold;
                    knBC(mapDiff:map) = ~flag;
                end % End of for
            end % End of if
        end % End of function

        function out = getXYZ (st, tmpND, tmpElem)
            % Get x, y and z for each elemtns
            %
            % input:
            %  - tmpElem: The elemt matrix that what to get coordinate
            %
            % output;
            % - out: strucure of coordinate.
            %        - out.x: x coordinate of node
            %        - out.y: y coordinate of node
            %        - out.z: z coordinate of node (only if 3D space)

            out.x = [tmpND(tmpElem(1), 1), tmpND(tmpElem(2), 1)];
            if st.dim == 2 || st.dim == 3
                out.y = [tmpND(tmpElem(1), 2), tmpND(tmpElem(2), 2)];
            end % End of if
            if st.dim == 3
                out.z = [tmpND(tmpElem(1), 1), tmpND(tmpElem(2), 3)];
            end % End of if
        end % End of function

        function setL(st)
            % Calculate length of elemts based on the node coordinate

            for i = 1:st.numElem
                if st.dim == 1 % Case 1D
                    st.L(i) = st.nd(st.elem(i, 2)) - st.nd(st.elem(i, 1));
                else
                    xyz = st.getXYZ(st.nd, st.elem(i, :));
                    if st.dim == 2 % Case 2D
                        st.L(i) = sqrt((xyz.x(2) - xyz.x(1))^2 ...
                            + (xyz.y(2) - xyz.y(1))^2);
                    else % case 3D
                        st.L(i) = sqrt((xyz.x(2) - xyz.x(1))^2 ...
                            + (xyz.y(2) - xyz.y(1))^2 ...
                            + (xyz.z(2) - xyz.z(1))^2);
                    end % End of if
                end % End of if
            end % End of for
        end % End of function

        function calcKlg(st)
            % Calculate local and golbal stiffness matrix

            for i = 1:st.numElem
                if st.dim == 1 % Case for 1D
                    st.Kl{i} = st.eng(i) / st.L(i) * st.tmpK;
                    st.Kg{i} = st.Kl{i};
                    st.T{i} = 1;
                else
                    xyz = st.getXYZ(st.nd, st.elem(i, :));
                    cHold = zeros(1, st.dim);
                    if st.dim == 2 % Case for 2D
                        c = [xyz.x(2) - xyz.x(1), xyz.y(2) - xyz.y(1)] ...
                            / st.L(i);
                    else
                        c = [xyz.x(2) - xyz.x(1), xyz.y(2) - xyz.y(1), ...
                            xyz.z(2) - xyz.z(1)];
                    end % End of if
                    st.T{i} = [c, cHold; cHold, c];
                    st.Kl{i} = st.eng(i) / st.L(i) * st.tmpK;
                    st.Kg{i} = st.T{i}.' * st.Kl{i} * st.T{i};
                end % End of if
            end % End of for loop
        end

        function pltFig(st, tmpName, flag)
            % Setting up figure to plot truss
            %
            % input:
            % - tmpName: Name of figure and title of the plot

            f = figure('Name', tmpName, 'Position', [200, 200, 1000, 600]);
            if flag; f.Visible = false; end
            hold on; grid on; title(tmpName);
            if st.dim == 3; view(gca, 3); end
        end

        function pltBG(st, xyz, color)
            if st.dim == 1
                plot(xyz.x, [0, 0], color, 'LineWidth', 1.5);
            elseif st.dim == 2
                plot(xyz.x, xyz.y, color, 'LineWidth', 1.5);
            else
                plot3(xyz.x, xyz.y, xyz.z, color, 'LineWidth', 1.5);
            end % End of if
        end % End of function

        function ptrBG(~, tmpM)
            % Set up and print matrix in format
            %
            % input:
            % - tmpM: Matrix that what to print

            if islogical(tmpM)
                disp(tmpM)
            else
                arg = "";
                for i = 1:size(tmpM, 2)
                    arg = arg + "%12.3e";
                end
                arg = arg + "\n";
                fprintf(arg, tmpM);
            end % End of if
        end % End of function

        function prtBG_FM(~, name)
            % Print function background to formation and print string
            %
            % input:
            % - name: text to print

            fprintf('\n\t%s\n', name);
        end % End of fucntion

        function out = setOutCh(st, tmpName, numNd)
            % Set up output format for excel
            %
            % input:
            % - tmpName: Name of value
            % - numNd: Number of node
            %
            % outpu:
            % - out: String array that hold value compoents

            tmpName = tmpName + string(numNd);
            out = tmpName + 'x';
            if st.dim == 2 || st.dim == 3; out = [out; tmpName + 'y']; end
            if st.dim == 3; out = [out; tmpName + 'z']; end
        end % End of function
    end % End of method (private)

    methods
        function st = clsTruss(nd, elem, E, A, F, dispVec)
            % Constructor
            %
            % Input
            % - nd: node
            % - elem: elements
            % - E: Elastic modulus
            % - A: Area of each elements
            % - F: boundert condition of force
            % - dispVec: boundery condition of displacement
            %
            % Output
            % - st: Class object

            % Initializing class variable
            st.nd = nd;
            st.elem = elem;
            st.dim = size(nd, 2);
            st.numElem = size(elem, 1);
            st.L = zeros(st.numElem, 1);
            st.setEng(E, A)
            st.T = cell(st.numElem, 1);
            st.Ks = zeros(st.dim * size(nd, 1), st.dim * size(nd, 1));
            st.Kl = cell(st.numElem, 1);
            st.Kg = cell(st.numElem, 1);
            % Initialize boundery condition
            st.setBC(F, dispVec)
        end % End of function

        function setBC(st, F, dispVec)
            % Setup of boundery condition. It also can called if it was not
            % given as construction
            % function
            %
            % input:
            % - F: boundert condition of force
            % - dispVec: boundery condition of displacement

            % Initialize boundery condition
            st.knBC = zeros(st.dim * size(st.nd, 1), 2);
            % Displacement bc
            [st.bcDisp, st.knBC(:, 1)] = st.setBC_BG(dispVec);
            % Force bc
            [st.bcF, st.knBC(:, 2)] = st.setBC_BG(F);
            st.knBC = logical(st.knBC);
            st.knBC(:, 2) = ~st.knBC(:, 1);
        end

        function out = getBC(st, flag)
            % Get fucntion, for deduging
            %
            % input:
            % - flag: True for print reasult, false to not print
            %
            % output:
            % - out: Retun boundery condtions to user
            %        - out.kn: Logical matrix that true for bc input
            %        - out.bcU: Boundery condition of displacement
            %        - out.bcF: boundery condition of force

            out.kn = st.knBC;
            out.bcU = st.bcDisp;
            out.bcF = st.bcF;
            if flag
                st.prtBG_FM("Input flag for boundery donction [disp, force]")
                st.prtMarix(st.knBC)
                st.prtBG_FM("Input deflection [disp, force]")
                st.prtMarix(st.bcDisp)
                st.prtBG_FM("Input Force [disp, force]")
                st.prtMarix(st.bcF)
            end % end of function
        end % End of function

        function calcAll(st, flagPRT)
            % Calls all functions to simulate truss and print reasult.
            %
            % Input
            % - flagBC: True for calculate reasulent force and elongation
            % - flagPRT: Print reasult of FEM

            st.calcKs();
            % To calculate force, elongation and stress
            if st.bcFlag; st.calcBC(); st.calcSig(); end
            % Print reasult
            if flagPRT; st.prtRts(); end
        end % End of function

        function calcKs(st)
            % Calculate system stiffness matrix

            % Calculates lenght of each element
            st.setL();
            % Calculates local and global stifness
            st.calcKlg();
            % Calculates system stifness
            for i = 1:st.numElem
                if st.dim == 1
                    cr1 = st.elem(i, 1); cr2 = st.elem(i, 2);
                    % n1 of the system
                    st.Ks(cr1, cr1) = st.Ks(cr1, cr1) + st.Kg{i}(1, 1);
                    st.Ks(cr1, cr2) = st.Ks(cr1, cr2) + st.Kg{i}(1, 2);
                    % n2 of that system
                    st.Ks(cr2, cr1) = st.Ks(cr2, cr1) + st.Kg{i}(2, 1);
                    st.Ks(cr2, cr2) = st.Ks(cr2, cr2) + st.Kg{i}(2, 2);
                else
                    cr1_1 = st.dim * st.elem(i, 1) - (st.dim - 1);
                    cr1_2 = st.dim * st.elem(i, 1);
                    cr2_1 = st.dim * st.elem(i, 2) - (st.dim - 1);
                    cr2_2 = st.dim * st.elem(i, 2);
                    % n1 of the system
                    st.Ks(cr1_1:cr1_2, cr1_1:cr1_2) = ...
                        st.Ks(cr1_1:cr1_2, cr1_1:cr1_2) ...
                        + st.Kg{i}(1:st.dim, 1:st.dim);
                    st.Ks(cr1_1:cr1_2, cr2_1:cr2_2) = ...
                        st.Ks(cr1_1:cr1_2, cr2_1:cr2_2) ...
                        + st.Kg{i}(1:st.dim, st.dim + 1:st.dim + st.dim);
                    % n2 of the system
                    st.Ks(cr2_1:cr2_2, cr1_1:cr1_2) = ...
                        st.Ks(cr2_1:cr2_2, cr1_1:cr1_2) ...
                        + st.Kg{i}(st.dim + 1:st.dim + st.dim, 1:st.dim);
                    st.Ks(cr2_1:cr2_2, cr2_1:cr2_2) = ...
                        st.Ks(cr2_1:cr2_2, cr2_1:cr2_2) ...
                        + st.Kg{i}(st.dim + 1:st.dim + st.dim, ...
                        st.dim + 1:st.dim + st.dim);
                end % End of if
            end % End of for
        end % End of function

        function calcBC(st)
            % Calvulates elongation and force based on input

            st.comFlag = true;
            tmpKs = st.Ks;
            tmpF = st.bcF(st.knBC(:, 2));
            % Set part of stiffness matrix that needs for calculation
            tmpKs(:, st.knBC(:, 1)) = [];
            tmpKs(~st.knBC(:, 2), :) = [];
            % To cover case when displacement BC is not zero
            for i = 1:size(st.bcDisp)
                if st.knBC(i, 1)
                    tmpF = tmpF - (st.Ks(st.knBC(:, 2), i) * st.bcDisp(i));
                end % End of if
            end % End of for
            % Find elongation of each element
            st.nodalDisp = st.bcDisp;
            st.nodalDisp(~st.knBC(:, 1)) = tmpKs \ tmpF;
            % Find forces each node
            st.F = st.Ks * st.nodalDisp;
        end % End of function

        function calcSig(st)
            % Calculates strees at each node
            st.comFlagSig = true;
            st.sig = zeros(st.numElem, 1);
            for i = 1:st.numElem
                map = st.elem(i, :) .* st.dim;
                mapDiff = map - (st.dim - 1);
                tmpHold = [ ...
                    st.nodalDisp(mapDiff(1):map(1)); ...
                    st.nodalDisp(mapDiff(2):map(2)); ...
                    ];
                st.sig(i) = st.E(i) * [-1 / st.L(i), 1 / st.L(i)] ...
                    * st.T{i} * tmpHold;
            end % End of for
        end % End of function

        function save2xlsx(st)
            % Save stiffness matrix into xcel file

            % Creating folder
            if ~exist('./out', 'dir'); mkdir('./out'); end
            tmpFU = strings(st.numElem, 2);
            tmpSig = strings(st.numElem, 1);
            for i = 1:size(st.nd, 1)
                map = i * st.dim;
                mapDiff = map - (st.dim - 1);
                tmpFU(mapDiff:map, 1) = st.setOutCh('F', i);
                tmpFU(mapDiff:map, 2) = st.setOutCh('U', i);
            end % End of for
            for i = 1:st.numElem
                tmpSig(i) = "Element" + string(i) + " (" ...
                    + string(st.elem(i, 1)) + ", " ...
                    + string(st.elem(i, 2)) + ")";
            end % End of for
            % writing to the file
            name = "./out/SystemStiffness.xlsx";
            writematrix(tmpFU(:, 1), name, 'Range', 'A2');
            writematrix(tmpFU(:, 2).', name, 'Range', 'B1');
            writematrix(st.Ks, name, 'Range', 'B2');
            if st.comFlag
                name = "./out/Elongation.xlsx";
                writematrix(tmpFU(:, 2), name, 'Range', 'A1');
                writematrix(st.nodalDisp, name, 'Range', 'B1');
                name = "./out/Force.xlsx";
                writematrix(tmpFU(:, 1), name, 'Range', 'A1');
                writematrix(st.F, name, 'Range', 'B1');
            end % End of if
            if st.comFlagSig
                name = "./out/Stress.xlsx";
                writematrix(tmpSig, name, 'Range', 'A1');
                writematrix(st.sig, name, 'Range', 'B1');
            end % End of if
        end % End of function

        function prtMarix(st, tmpM)
            % Print matrix in format
            %
            % input:
            % - tmpM: matrix that what to print
            st.ptrBG(tmpM)
        end

        function prtRts(st)
            % Format and print reault automatically

            % Ptint system stiffness matrix
            st.prtBG_FM("System stiffness matrix Ks");
            st.ptrBG(st.Ks)
            if st.comFlag
                % Print reasultent force
                st.prtBG_FM("Force at each node")
                st.ptrBG(st.F);
                % Print nodal displacement
                st.prtBG_FM("Nodal displacement at each node")
                st.ptrBG(st.nodalDisp);
            end % End of if
            if st.comFlagSig
                % Print stress at each elements
                st.prtBG_FM("Stress of each elements")
                st.ptrBG(st.sig);
            end % End of if
        end % End of function

        function pltTruss(st, viFlag)
            % Plot truss
            %
            % Input:
            % - viFlag: True for save figure without display

            if ~(st.comFlag)
                name = 'Input Truss';
            else
                name = 'Input and Reasultent Truss';
            end
            st.pltFig(name, viFlag)
            if ~(st.comFlag)
                for i = 1:st.numElem
                    xyz = st.getXYZ(st.nd, st.elem(i, :));
                    st.pltBG(xyz, 'b*-');
                end % End of for
            else
                tmpNode = zeros(size(st.nd));
                for i = 1:size(st.nd, 1)
                    map = i * st.dim;
                    tmpNode(i, 1) = st.nodalDisp(map - (st.dim - 1));
                    if st.dim == 2 || st.dim == 3
                        tmpNode(i, 2) = st.nodalDisp(map - (st.dim - 2));
                    end % End of if
                    if st.dim == 3; tmpNode(i, 3) = st.nodalDisp(map); end
                end % End of for
                tmpNode = st.nd + tmpNode;
                for i = 1:st.numElem
                    % Original truss
                    xyz = st.getXYZ(st.nd, st.elem(i, :));
                    st.pltBG(xyz, 'b*--');
                    % Output truss
                    xyz = st.getXYZ(tmpNode, st.elem(i, :));
                    st.pltBG(xyz, 'r*-');
                end % End of for
                % Add legend
                legend({'Input Truss', 'Output Truss'}, ...
                    'Orientation', 'horizontal', ...
                    'Location', 'southoutside');
                legend('boxoff')
            end % End of if
            % Save plotted garph as png
            if viFlag
                % Check if output foler is exist, if not create one
                tmpDir = "./outPic/";
                if ~exist(tmpDir, 'dir'); mkdir(tmpDir); end
                if ~st.comFlag; tmpOut = "I_tr"; else; tmpOut = "IR_tr"; end
                saveas(gcf, tmpDir + tmpOut, 'png');
            end % End of if
            hold off;
        end % End of function
    end % End of methos
end % End of class
