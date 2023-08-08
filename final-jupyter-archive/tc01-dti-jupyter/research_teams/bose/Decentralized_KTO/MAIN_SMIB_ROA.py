#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  2 13:32:15 2021

Simulation SMIB

@author: boyah
"""

import os
from sys import getsizeof
import numpy as np
import pandas as pd
from math import *
import matplotlib.colors
from scipy.io import loadmat
import scipy.sparse as sp
import scipy.linalg
import scipy.io as sio
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from cmath import sin, cos, exp, pi, log, polar, rect, phase, sqrt
from sklearn.metrics.pairwise import rbf_kernel,laplacian_kernel,sigmoid_kernel,polynomial_kernel
from sklearn import preprocessing
import warnings
warnings.filterwarnings('ignore')
# For color bar
def fmt(x, pos):
    a, b = '{:.1e}'.format(x).split('e')
    b = int(b)
    return r'${} \times 10^{{{}}}$'.format(a, b)
from kedmd_func import *
from fnc_compress import *
# =============================================================================
# Initiate
# =============================================================================
X0= np.load('X-1500.npy')
Y0= np.load('Y-1500.npy')
X = scale(X0)
Y = scale(Y0)
#%% =============================================================================
# Construct a dictionary: New snapshots arrived, update dictionary (ADL)  
# ===========================================================================
# RBF parameter: 
dxx = distance.pdist(X, 'euclidean')
dx = np.median(dxx)
print('Mean of distance',dx)
print()
sigma_st = np.sqrt(dx)
M_data = X.shape[0]
N_kernel = 1
sigmalist = [sigma_st/4]
etalist = [1]
print("Printing list of sigmas ",sigmalist)
print("Intial kernel weight ",etalist)    
print()
#%% =============================================================================
# Construct a dictionary: New snapshots arrived, update dictionary (ADL)  
# ===========================================================================
delta_tol = 1
Dx,Dy = compressD(X,Y,delta_tol,sigmalist,etalist)        
D_data = Dx.shape[0]        
print('Final shape of Dictionary :',D_data)        
print()    
#%% =============================================================================
#   Main
# =============================================================================
# Kernel tensors
KXX_tensor,KXY_tensor,KYY_tensor = rbfTensor(Dx, Dy, N_kernel,sigmalist)
KXX = np.zeros((D_data,D_data))
KXY = np.zeros((D_data,D_data))
KYY = np.zeros((D_data,D_data))
for e in range(N_kernel):
    KXX+= etalist[e] * KXX_tensor[:,:,e]
    KXY+= etalist[e] * KXY_tensor[:,:,e]        
    KYY+= etalist[e] * KYY_tensor[:,:,e]
## Construct Koopman matrix and find eigenpairs 
eps = -0.20
ve = 1e-10 * D_data**eps 
# New
# get alpha^\star:
rcond_val = 1e-5
rcond_value = 1e-5#1e-5
Gmat_a = np.multiply(KYY,KXX) 
Gmat_axx = np.multiply(KXX,KXX) 
g_a = getveck(Y,X,Dy,Dx, sigmalist,etalist)
g_axx = getveckxx(X,Dx, sigmalist,etalist) 
alpha_yx = np.matmul(scipy.linalg.pinv(Gmat_a,rcond=rcond_value),g_a) 
alpha_xx = np.matmul(scipy.linalg.pinv(Gmat_axx,rcond=rcond_value),g_axx) 
Ayx = np.diag(alpha_yx) * D_data
Axx = np.diag(alpha_xx) * D_data
#
AGxx = np.matmul(Axx,KXX) + ve*np.eye(D_data) 
AGyx = np.matmul(Ayx,KXY.T)
U = scipy.linalg.pinv(AGxx,rcond=rcond_val) @ AGyx
# Construct Koopman matrix and find eigenpairs 
lambdas,Vright = scipy.linalg.eig(U, left=False, right=True)
idx2 = lambdas.argsort()[::-1]   
lambdaK = lambdas[idx2]
Vr = Vright[:,idx2]
# Plot leading eigenvalues
plt.figure(figsize=(7,5))
plt.scatter(np.real(lambdaK), np.imag(lambdaK), marker='o')  
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)  
plt.xlabel('Real', fontsize=18)
plt.ylabel('Imag', fontsize=18) 
plt.title('Eigenvalues',fontsize=20)
plt.show()

# =============================================================================
# Compute eigenfunctions: only real eigenvalues
# =============================================================================

selected = np.nonzero((np.imag(lambdaK)==0)&(lambdaK<= 1+5e-2)&(lambdaK>= 1-5e-2))
lambdalead = lambdaK[selected]
#print('Leading eigenvalues are \n',lambdalead)
#print()
#print('Magnitude of Leading eigenvalues are \n',np.abs(lambdalead))
#print()
# Leading eigenfunctions
Vlead = Vr[:,selected[0]] #the column

# =============================================================================       
def find_eigenfunctions(x):
    kappa=np.zeros((len(x[:,0]),len(Dx[:,0])))
    kappa0=np.zeros((len(x[:,0]),len(Dx[:,0])))
    for sigma0,eta0 in zip(sigmalist,etalist): 
        kappa0 = rbf_kernel(x,Dx,gamma=1.0/(2*sigma0**2))
        kappa += eta0 * kappa0
    eigfn_val = kappa @ Vlead
    return eigfn_val

#%% Plotting results: 
# meshgrid    
N1 = 100
N2 = 100
Ns = N1 * N2
xx = np.linspace(-4,4,N1)
yy = np.linspace(-8,8,N2)
x1g,x2g = np.meshgrid(xx,yy)
xg1 = np.reshape(x1g,(Ns,1))
xg2 = np.reshape(x2g,(Ns,1))
xg = np.append(xg1,xg2,1)    
phi_vec = np.zeros((Ns,len(selected)))
print('Evaluating eigenfunctions ...')
xgs = scale(xg)
phi_vec = find_eigenfunctions(xgs)      
print('Finished Evaluating eigenfunctions')
## plot
for l in range(len(selected[0])):
    plt.figure(figsize=(7,5))
    phi_l = np.reshape(phi_vec[:,l],(N1,N2))
    plt.figure()
    plt.pcolormesh(x1g,x2g,np.abs(phi_l), cmap='seismic')
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)    
    plt.title('|lambda| = '+ str(round(np.abs(lambdalead[l]),3)) + 'l:'+str(l),fontsize=20)
#    plt.savefig("duffing" + str(l) +".png", format="PNG")
    plt.show()
print('Number of figures:',len(selected[0]))
print('******************') 
print('Final shape of Dictionary :',D_data)        
print() 
#%% =============================================================================
#save figure
l=0
fig = plt.figure(figsize=(7,5))
phi_l = np.reshape(phi_vec[:,l],(N1,N2))
plt.figure()
plt.pcolormesh(x1g,x2g,np.abs(phi_l), cmap='seismic')
#plt.xticks(np.arange(-5, 5, 1),fontsize=16)
#plt.yticks(np.arange(-8, 8, 1),fontsize=16)   
#cbar = plt.colorbar(ticks=[1e-2,2e-2, 3e-2, 4e-2,5e-2])
#cbar.ax.tick_params(labelsize=20)
#plt.savefig('SMIB_1500.png', format="PNG")
plt.show()
#%%
from scipy.io import savemat
savemat("magPhi.mat",{'magPhi' : np.abs(phi_l)})