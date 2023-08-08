#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 24 16:28:56 2022

Functions for sparse learning

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


#======= RBF kernel ======= 
def rbfTensor(X, Y, N_kernel,sigmalist):
    nx = len(X[:,0])
    ny = len(Y[:,0])
    KXX_tensor=np.zeros((nx,nx,N_kernel))
    # KXY_tensor=np.zeros((nx,ny,N_kernel))
    KYY_tensor=np.zeros((ny,ny,N_kernel))
    for k in range(N_kernel):
        sigma = sigmalist[k]
        KXX_tensor[:,:,k] = rbf_kernel(X,gamma=1.0/(2.0*sigma**2))
        # KXY_tensor[:,:,k] = rbf_kernel(X,Y,gamma=1.0/(2.0*sigma**2))
        KYY_tensor[:,:,k] = rbf_kernel(Y,gamma=1.0/(2.0*sigma**2))
#    print('*** Finished Construcing RBF Kernels ***')         
    # return KXX_tensor, KXY_tensor,KYY_tensor
    return KXX_tensor, KYY_tensor


#========== Coherence criterion ==================
def getDeltaxy(Dictx,Dicty,x,y,sigmalist,etalist):
    Kappax = np.zeros((len(Dictx[:,0]),1))
    kappax0=np.zeros((len(Dictx[:,0]),1)) 
    for sigma0,eta0 in zip(sigmalist,etalist): 
        kappax0 = rbf_kernel(Dictx,x,gamma=1.0/(2*sigma0**2))
        Kappax += eta0 * kappax0 
    Kappay = np.zeros((len(Dicty[:,0]),1))
    kappay0= np.zeros((len(Dicty[:,0]),1)) 
    for sigma0,eta0 in zip(sigmalist,etalist): 
        kappay0 = rbf_kernel(Dicty,y,gamma=1.0/(2*sigma0**2))
        Kappay += eta0 * kappay0 
    deltat = np.max(np.multiply(Kappax,Kappay))
    return deltat
#============== Sparse dictionary===================
def compressD(X,Y,delta_tol,sigmalist,etalist):
    dict_inds = []
    M_data = X.shape[0]
    Dx = X[:2,:]
    Dy = Y[:2,:]
    dict_inds.append(0)
    dict_inds.append(1)
    for t in range(2,M_data):
        xt = X[t,:]
        yt = Y[t,:]
        # if t % 200 == 0:
        #     print('Current shape of Dictionary :',D_data)
        Dx_old = Dx
        Dy_old = Dy
        D_data = Dx_old.shape[0]
        xtt = np.reshape(xt,(1, -1))
        ytt = np.reshape(yt,(1, -1))
        deltat = getDeltaxy(Dx_old,Dy_old,xtt,ytt, sigmalist,etalist)
        if deltat <= delta_tol:
            Dx = np.vstack((Dx_old,X[t,:])) 
            Dy = np.vstack((Dy_old,Y[t,:]))   
            dict_inds.append(t)       
    D_data = Dx.shape[0]               
    return Dx,Dy,dict_inds
#============= alpha^star====================
def getveck(X,Y,Dx,Dy, sigmalist,etalist):
    M = X.shape[0]  
    D = Dx.shape[0] 
    K = np.zeros((D,M))
    kvec = np.zeros((D,1))
    kx = np.zeros((D,M))
    kx0= np.zeros((D,M))
    ky = np.zeros((D,M))
    ky0= np.zeros((D,M))
    for sigma0,eta0 in zip(sigmalist,etalist): 
        kx0 = rbf_kernel(Dx,X,gamma=1.0/(2*sigma0**2))
        kx += eta0 * kx0 
        ky0 = rbf_kernel(Dy,Y,gamma=1.0/(2*sigma0**2))
        ky += eta0 * ky0 
    K = np.multiply(kx,ky)
    kvec = K.sum(axis=1)/M
    return kvec

def getveckxx(X,Dx,sigmalist,etalist):
    M = X.shape[0]  
    D = Dx.shape[0] 
    K = np.zeros((D,M))
    kvec = np.zeros((D,1))
    kx = np.zeros((D,M))
    kx0= np.zeros((D,M))
    for sigma0,eta0 in zip(sigmalist,etalist): 
        kx0 = rbf_kernel(Dx,X,gamma=1.0/(2*sigma0**2))
        kx += eta0 * kx0 
    K = np.multiply(kx,kx)
    kvec = K.sum(axis=1)/M
    return kvec
#================= Sparse weight ====================

def simpleGram(X, Y, N_kernel,sigmalist,etalist):
    KXX_tensor,KXY_tensor,KYY_tensor = rbfTensor(X, Y, N_kernel,sigmalist)
    D_data = X.shape[0]
    KXX = np.zeros((D_data,D_data))
    KXY = np.zeros((D_data,D_data))
    for e in range(N_kernel):
        KXX+= etalist[e] * KXX_tensor[:,:,e]
        KXY+= etalist[e] * KXY_tensor[:,:,e]        
    return KXX,KXY

def Grams(X, Y, N_kernel,sigmalist,etalist):
    # KXX_tensor,KXY_tensor,KYY_tensor = rbfTensor(X, Y, N_kernel,sigmalist)
    KXX_tensor,KYY_tensor = rbfTensor(X, Y, N_kernel,sigmalist)
    D_data = X.shape[0]
    KXX = np.zeros((D_data,D_data))
    # KXY = np.zeros((D_data,D_data))
    KYY = np.zeros((D_data,D_data))
    for e in range(N_kernel):
        KXX+= etalist[e] * KXX_tensor[:,:,e]
        # KXY+= etalist[e] * KXY_tensor[:,:,e]        
        KYY+= etalist[e] * KYY_tensor[:,:,e]
    Gmat_ayx = np.multiply(KYY,KXX) 
    Gmat_axx = np.multiply(KXX,KXX) 
    return Gmat_ayx,Gmat_axx

def tempGrams(X,Y,Dx,Dy,sigmalist,etalist): 
    N_kernel = len(sigmalist)
    nx = len(X[:,0])
    nDx = len(Dx[:,0])
    KDX = np.zeros((nDx,nx))
    KDY = np.zeros((nDx,nx))
    for k in range(N_kernel):
        sigma = sigmalist[k]
        KDX+= etalist[k] * rbf_kernel(Dx,X,gamma=1.0/(2.0*sigma**2))
        KDY+= etalist[k] * rbf_kernel(Dy,Y,gamma=1.0/(2.0*sigma**2))       
    Gmat_ayx = np.multiply(KDY,KDX) 
    Gmat_axx = np.multiply(KDX,KDX) 
    return Gmat_ayx,Gmat_axx

def weightAverage(localY,localX,localDy,localDx,sigmalist,etalist,rcond_value):
    N_kernel = len(sigmalist)
    Gmat_ayx,Gmat_axx = Grams(localDx,localDy, N_kernel,sigmalist,etalist)
    g_ayx = getveck(localY,localX,localDy,localDx, sigmalist,etalist)
    g_axx = getveckxx(localX,localDx, sigmalist,etalist) 
    alpha_yx = np.matmul(scipy.linalg.pinv(Gmat_ayx,rcond=rcond_value),g_ayx) 
    alpha_xx = np.matmul(scipy.linalg.pinv(Gmat_axx,rcond=rcond_value),g_axx) 
    return alpha_yx,alpha_xx
