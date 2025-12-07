# LAMMPS Include File
# Licensed under CC BY 4.0
# A Set of Tutorials for the LAMMPS Simulation Package (LiveCoMS, 2025)
# By Simon Gravelle, Cecilia M. S. Alvares, Jacob R. Gissinger, and Axel Kohlmeyer
# Please cite doi.org/10.33011/livecoms.6.1.3037
# Find more on GitHub: https://github.com/lammpstutorials

pair_coeff 1 1 0.066 3.4
bond_coeff 1 469 1.4 # equilibrium xdistance of 1.4 of atom 1 spring constant 469
angle_coeff 1 63 120 #agle at 120 degrees 63 spring constant, use harmonic K(theta - theta_0)^2
dihedral_coeff 1 0 7.25 0 0 #cosine series potential --> torsioin
improper_coeff 1 5 180 # maintains planarity
