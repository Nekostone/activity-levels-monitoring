import matplotlib.pyplot as plt

from numpy import mean

def play_2d_results(M, LS, L, S, width, height, length=None):
    # Check length
    length = M.shape[1] if length is None else length
    # Reshape
    M_frame = M[:, 0].reshape(width, height).T
    L_frame = L[:, 0].reshape(width, height).T
    S_frame = S[:, 0].reshape(width, height).T
    LS_frame = LS[:, 0].reshape(width, height).T
    # Play
    fig, axs = plt.subplots(2, 2)
    axs[0, 0].set_title('Input')
    axs[0, 1].set_title('Reconstruction')
    axs[1, 0].set_title('Low-rank')
    axs[1, 1].set_title('Sparse')
    im1 = axs[0, 0].imshow(M_frame,  cmap='hot', interpolation='nearest')
    im2 = axs[0, 1].imshow(LS_frame,  cmap='hot', interpolation='nearest')
    im3 = axs[1, 0].imshow(L_frame,  cmap='hot', interpolation='nearest')
    im4 = axs[1, 1].imshow(S_frame,  cmap='hot', interpolation='nearest')
    fig.show()
    for i in range(length-1):
        print(i)
        M_frame = M[:, i+1].reshape(width, height).T
        L_frame = L[:, i+1].reshape(width, height).T
        S_frame = S[:, i+1].reshape(width, height).T
        LS_frame = LS[:, i+1].reshape(width, height).T
        im1.set_data(M_frame)
        im2.set_data(LS_frame)
        im3.set_data(L_frame)
        im4.set_data(S_frame)
        plt.pause(.01)
        plt.draw()


def plot_2d_results(M, LS, L, S, width, height, index=0):
    # Mean calculation
    M_frame = M[:, index].reshape(width, height).T
    L_frame = L[:, index].reshape(width, height).T
    S_frame = S[:, index].reshape(width, height).T
    LS_frame = LS[:, index].reshape(width, height).T
    # Plot results
    subplot_2x2(M_frame, LS_frame, L_frame, S_frame)


def plot_2d_results_mean(M, LS, L, S, width, height):
    # Mean calculation
    M_mean = mean(M, axis=1).reshape(width, height).T
    L_mean = mean(L, axis=1).reshape(width, height).T
    S_mean = mean(S, axis=1).reshape(width, height).T
    LS_mean = mean(LS, axis=1).reshape(width, height).T
    # Plot results
    subplot_2x2(M_mean, LS_mean, L_mean, S_mean)


def subplot_2x2(M, LS, L, S):
    # Plot results
    fig, axs = plt.subplots(2, 2)
    axs[0, 0].set_title('Input')
    axs[0, 0].imshow(M,  cmap='hot', interpolation='nearest')
    axs[0, 1].set_title('Reconstruction')
    axs[0, 1].imshow(LS,  cmap='hot', interpolation='nearest')
    axs[1, 0].set_title('Low-rank')
    axs[1, 0].imshow(L,  cmap='hot', interpolation='nearest')
    axs[1, 1].set_title('Sparse')
    axs[1, 1].imshow(S,  cmap='hot', interpolation='nearest')
    plt.show()
