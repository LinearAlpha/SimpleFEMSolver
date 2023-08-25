close all;
clear;
clc;

node = [0; 1; 2];
element = [ ...
            1, 2; ...
            2, 3; ...
        ];

E = [200e9; 70e9];
A = [4e-4; 2e-4];
F = [3, -2e3];
vecU = [1, 0];
tr = clsTruss(node, element, E, A, F, vecU);
tr.calcAll(true);

