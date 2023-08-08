#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 13 12:11:05 2020

@author: boyah
"""
# Imports: 

import numpy as np
from math import *
import pylab
import sys
import matplotlib.colors
from scipy.io import loadmat
import scipy.linalg
import scipy.io as sio
import matplotlib.pyplot as plt
from cmath import sin, cos, exp, pi, log, polar, rect, phase, sqrt
import scipy.ndimage.filters
import time 
from sklearn.metrics.pairwise import rbf_kernel,laplacian_kernel,sigmoid_kernel,polynomial_kernel
from sklearn import preprocessing
from sklearn.preprocessing import KernelCenterer
from sklearn.metrics.pairwise import chi2_kernel

from sklearn.metrics import pairwise_distances
from sklearn.metrics.pairwise import pairwise_kernels
from sklearn.gaussian_process.kernels import (RBF, Product,ConstantKernel)
from sklearn.preprocessing import MinMaxScaler
from scipy.spatial import distance


def scale2dim(X):
    dimX = X.shape[1]
    Xscale = np.zeros(np.shape(X))
    for i in range(dimX):
        maxval = np.max(X[:,i])
        Xscale[:,i] = X[:,i]/maxval
    return Xscale

def scale(X):
    dimX = X.shape[1]
    Xscale = np.zeros(np.shape(X))
    Xscale[:,0] = X[:,0]
    Xscale[:,1] = X[:,1]/2
    return Xscale
#(2.2) ======= OnLINE Construction  ======= 
def getKappa(Dict,x, sigmalist,etalist):
    Kappa=np.zeros((len(Dict[:,0]),len(x[:,0])))
    kappa0=np.zeros((len(Dict[:,0]),len(x[:,0])))  #(N(D),N(X))
    for sigma0,eta0 in zip(sigmalist,etalist): 
        kappa0 = rbf_kernel(Dict,x,gamma=1.0/(2.0*sigma0**2))
        Kappa += eta0 * kappa0      
    return Kappa

#(2).1 ======= OnLINE Construction  ======= 
def getTensor(Dict, N_kernel,sigmalist):
    nd = Dict.shape[0]
    Dict_tensor=np.zeros((nd,nd,N_kernel))
    for k in range(N_kernel):
        sigma = sigmalist[k]
        Dict_tensor[:,:,k] = rbf_kernel(Dict,gamma=1.0/(2.0*sigma**2))        
    return Dict_tensor

#(2.3) ======= OnLINE kernel value evaluation  ======= 
def get_kappa_val(x,y,sigmalist,etalist):
    kapp_val = 0
    for sigma0,eta0 in zip(sigmalist,etalist): 
        xx = np.reshape(x,(1, -1))
        yy = np.reshape(y,(1, -1))
        kapp = rbf_kernel(xx,yy,gamma=1.0/(2*sigma0**2))
        kapp_val += eta0 * kapp      
    return kapp_val


#========== Coherence criterion ==================
def getDelta(Dict,x,sigmalist,etalist):
    Kappa = np.zeros((len(Dict[:,0]),1))
    kappa0=np.zeros((len(Dict[:,0]),1)) #(N(D),N(X))
    for sigma0,eta0 in zip(sigmalist,etalist): 
        kappa0 = rbf_kernel(Dict,x,gamma=1.0/(2*sigma0**2))
        Kappa += eta0 * kappa0 
    deltat = np.max(Kappa)
    return deltat


#==============================================
def sk_kerTensor(X, Y, N_kernel,sigmalist):
    nx = len(X[:,0])
    KXX_tensor=np.zeros((nx,nx,N_kernel))
    KXY_tensor=np.zeros((nx,nx,N_kernel))
    for k in range(N_kernel):
        sigma = sigmalist[k]
        KXX_tensor[:,:,k] = rbf_kernel(X,gamma=1/sigma**2)
        KXY_tensor[:,:,k] = rbf_kernel(X,Y,gamma=1/sigma**2)
    print('*** Finished Construcing Kernel Tensors ***')         
    return KXX_tensor, KXY_tensor
        
def generate_kerTensor(X, Y, N_kernel,sigmalist):
    # f(x,z) = exp(-1/(sigma) ||x-z||2^2) 
    nx = len(X[:,0])
    KXX_tensor=np.zeros((nx,nx,N_kernel))
    KXY_tensor=np.zeros((nx,nx,N_kernel))
    
    print()
    print('*** Computing Kernel Tensors ***')
    for k in range(N_kernel):
        sigma = sigmalist[k]
        for i in range(len(X[:,0])):
            for j in range(len(X[:,0])):
                KXX_tensor[i,j,k] = np.exp( -1.0/(np.power(sigma,2))*np.power( np.linalg.norm(X[j,:] - Y[i,:]),2))
                KXY_tensor[i,j,k] = np.exp( -1.0/(np.power(sigma,2))*np.power( np.linalg.norm(X[j,:] - X[i,:]),2))
        if np.mod(i,100)==0:
            print(('finished', i, 'of', len(X[:,0])))
            
    print('*** Finished Construcing Kernel Tensors ***')         
    return KXX_tensor, KXY_tensor
#==============================================
def compute_Khat(Sig, Q, Ahat):
	# Utilizes original Khat from Matthew William's paper (2015) 
	SigPseu = np.diag(1.0/np.sqrt(Sig))
	Khat = np.matmul(np.matmul(np.matmul(np.matmul(SigPseu, Q.T), Ahat), Q), SigPseu)
	return Khat, SigPseu



