import imageio
import matplotlib.pyplot as plt
from numpy import amax, amin, prod, sqrt, zeros
from numpy.random import randn
from pygifsicle import optimize
from scipy.linalg import qr
from sklearn.metrics import mean_squared_error
from tqdm import tqdm

from file_utils import create_folder_if_absent, folder_path, get_all_files
from visualizer import write_gif_from_pics


def godec(M, rank=1, card=None, iterated_power=1, max_iter=100, tol=0.001):
    """
    GoDec - Go Decomposition (Tianyi Zhou and Dacheng Tao, 2011) 
    The algorithm estimate the low-rank part L and the sparse part S of a matrix M = L + S + G with noise G.
    Code from https://github.com/andrewssobral/godec.git

    Parameters
    ----------
    M : array-like, shape (n_features, n_samples), which will be decomposed into a sparse matrix S 
        and a low-rank matrix L.
    
    rank : int >= 1, optional
        The rank of low-rank matrix. The default is 1.
    
    card : int >= 0, optional
        The cardinality of the sparse matrix. The default is None (number of array elements in M).
    
    iterated_power : int >= 1, optional
        Number of iterations for the power method, increasing it lead to better accuracy and more time cost. The default is 1.
    
    max_iter : int >= 0, optional
        Maximum number of iterations to be run. The default is 100.
    
    tol : float >= 0, optional
        Tolerance for stopping criteria. The default is 0.001.
    ----------
    
    Returns
    -------
    L : array-like, low-rank matrix.
    S : array-like, sparse matrix.
    LS : array-like, reconstruction matrix.
    RMSE : root-mean-square error.
    ----------
    """
    iter = 1
    RMSE = []
    card = prod(M.shape) if card is None else card
    
    # Initialization of L and S
    L = M
    S = zeros(M.shape)
    LS = zeros(M.shape)
    m, n = M.shape
    
    while True:
        # Update of L
        Y2 = randn(n, rank)
        for i in range(iterated_power):
            Y1 = L.dot(Y2)
            Y2 = L.T.dot(Y1)
        Q, R = qr(Y2, mode='economic')
        L_new = (L.dot(Q)).dot(Q.T)
        
        # Update of S
        T = L - L_new + S
        L = L_new
        T_vec = T.reshape(-1)
        S_vec = S.reshape(-1)
        idx = abs(T_vec).argsort()[::-1]
        S_vec[idx[:card]] = T_vec[idx[:card]]
        S = S_vec.reshape(S.shape)        
        # Reconstruction
        LS = L + S
        
        # Stopping criteria
        error = sqrt(mean_squared_error(M, LS))
        RMSE.append(error)
        
        print("iter: ", iter, "error: ", error)
        if (error <= tol) or (iter >= max_iter):
            break
        else:
            iter = iter + 1

    return L, S, LS, RMSE



"""
Godec Plots
"""

def init_godec_plot(M, LS, L, S, width, height, preview=False):
    M_frame = M[:, 0].reshape(width, height).T
    L_frame = L[:, 0].reshape(width, height).T
    S_frame = S[:, 0].reshape(width, height).T
    LS_frame = LS[:, 0].reshape(width, height).T
    fig, axs = plt.subplots(2, 2)
    axs[0, 0].set_title('Input')
    axs[0, 1].set_title('Reconstruction')
    axs[1, 0].set_title('Low-rank')
    axs[1, 1].set_title('Sparse')
    im1 = axs[0, 0].imshow(M_frame,  cmap='hot', interpolation='nearest')
    im2 = axs[0, 1].imshow(LS_frame,  cmap='hot', interpolation='nearest')
    im3 = axs[1, 0].imshow(L_frame,  cmap='hot', interpolation='nearest')
    im4 = axs[1, 1].imshow(S_frame,  cmap='hot', interpolation='nearest')
    if preview:
        plt.show()
    return im1, im2, im3, im4

def get_reshaped_frames(matrixes, i, width=32, height=24):
    return [matrix[:, i+1].reshape(width, height).T for matrix in matrixes]

def set_data(ims, frames):
    for i in range(len(ims)):
        ims[i].set_data(frames[i])


def plot_godec(M, LS, L, S, folder_path, width=32, height=24, length=None, preview=False):
    length = M.shape[1] if length is None else length
    ims = init_godec_plot(M, LS, L, S, width, height, preview)
    matrixes = (M, LS, L, S)
    create_folder_if_absent(folder_path)
    for i in tqdm(range(length-1)):
        frames = get_reshaped_frames(matrixes, i, width, height)
        set_data(ims, frames)
        if preview:
            plt.pause(.01) # required for very small datasets for previewing
        plt.draw()
        pic_name = '{}/{}.png'.format(folder_path, i)
        plt.savefig(pic_name)
        
"""
Plots for after removing noise obtained from Godec
"""

def init_godec_trained_plot(M, N, R, width=32, height=24):
    M_frame = M[:, 0].reshape(width, height).T
    N_frame = N[:, 0].reshape(width, height).T
    R_frame = R[:, 0].reshape(width, height).T
    fig, axs = plt.subplots(1, 3)
    axs[0].set_title('Input')
    axs[1].set_title('Noise')
    axs[2].set_title('Result')
    im1 = axs[0].imshow(M_frame,  cmap='hot', interpolation='nearest')
    im2 = axs[1].imshow(N_frame,  cmap='hot', interpolation='nearest')
    im3 = axs[2].imshow(R_frame,  cmap='hot', interpolation='nearest')
    return im1, im2, im3

def plot_bs_results(M, N, R, folder_path, width=32, height=24, length=None, preview=False):
    length = M.shape[1] if length is None else length
    ims = init_godec_trained_plot(M, N, R, width, height)
    matrixes = (M, N, R)
    create_folder_if_absent(folder_path)
    if preview:
        plt.show()
    for i in tqdm(range(length-1)):
        frames = get_reshaped_frames(matrixes, i, width, height)
        set_data(ims, frames)
        if preview:
            plt.pause(.01) # required for very small datasets for previewing
        plt.draw()
        pic_name = '{}/{}.png'.format(folder_path, i)
        plt.savefig(pic_name)
