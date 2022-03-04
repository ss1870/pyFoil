import numpy as np
import math


# from numba import jit


# @jit(nopython=True)
def eval_biot_savart(xcp, xnode1, xnode2, gamma, l0):
    xcp = xcp.reshape(-1, 1, 3)  # xcp shape (ncp, 1, 3)
    r1 = xcp - xnode1  # r1 shape (ncp, nvl, 3)
    r2 = xcp - xnode2  # r2 shape (ncp, nvl, 3)

    r1_norm = np.sqrt(np.sum(r1 ** 2, axis=2))  # r1_norm shape = (ncp, nvl)
    r1_norm = r1_norm.reshape(r1_norm.shape + (1,))  # add 3rd dimension
    r2_norm = np.sqrt(np.sum(r2 ** 2, axis=2))  # r2_norm shape = (ncp, nvl)
    r2_norm = r2_norm.reshape(r2_norm.shape + (1,))  # add 3rd dimension

    cross_r1r2 = np.cross(r1, r2)
    dotr1r2 = np.sum(r1 * r2, axis=2)
    dotr1r2 = dotr1r2.reshape(dotr1r2.shape + (1,))  # add 3rd dimension
    r1r2 = r1_norm * r2_norm

    numer = gamma * (r1_norm + r2_norm) * cross_r1r2
    denom = 4 * math.pi * r1r2 * (r1r2 + dotr1r2) + (0.025 * l0) ** 2
    u_gamma = numer / denom

    return u_gamma


def LL_residual(gamma, rho, u_BV, u_FV, u_motion, dl, a1, a3, cl_spline, dA):
    # gamma:    (nseg,)
    # u_BV:     (nseg, nseg*4, 3)
    # u_motion: (3,)
    # u_FV, dl, a1, a3, dA: (nseg, 3)
    # cl_spline = callable object to compute lift coefficient

    # multiply gamma * velocity component due to bound vorticity
    gamma1 = np.tile(gamma.reshape(1, -1, 1), (len(gamma), 4, 3))
    u_BV = np.sum(u_BV * gamma1, axis=1)  # resulting size (nseg, 3)

    # sum up all velocity components at the CPs
    u_cp = u_motion.reshape(1, 3) + u_BV + u_FV  # (nseg, 3)

    # compute lift due to circulation
    cross_ucp_dl = np.cross(u_cp, dl)
    dot_a1 = np.sum(cross_ucp_dl * a1, axis=1)
    dot_a3 = np.sum(cross_ucp_dl * a3, axis=1)
    L_gamma = rho * gamma * np.sqrt(dot_a1 ** 2 + dot_a3 ** 2) # (nseg,)

    # compute lift due to strip theory
    dot_ucp_a1 = np.sum(u_cp * a1, axis=1)
    dot_ucp_a3 = np.sum(u_cp * a3, axis=1)
    alpha_cp = np.arctan(dot_ucp_a3 / dot_ucp_a1)
    cl = cl_spline.__call__(alpha_cp * 180 / np.pi)
    L_alpha = cl * 0.5 * rho * (dot_ucp_a1 ** 2 + dot_ucp_a3 ** 2) * dA/ 1e6

    # difference between two methods = residual
    R = L_alpha - L_gamma
    return R


def rotation_matrix(w, angle, deg=True):
    # w is the axis to rotate about, size (3,)
    # angle is the angle to rotate by in radian
    if deg == True:
        angle = angle * np.pi / 180
    c = np.cos(angle)
    s = np.sin(angle)
    R = np.array([[w[0] ** 2 * (1 - c) + c, w[0] * w[1] * (1 - c) - w[2] * s, w[0] * w[2] * (1 - c) + w[1] * s, 0],
                  [w[1] * w[0] * (1 - c) + w[2] * s, w[1] ** 2 * (1 - c) + c, w[1] * w[2] * (1 - c) - w[0] * s, 0],
                  [w[2] * w[0] * (1 - c) - w[1] * s, w[2] * w[1] * (1 - c) + w[0] * s, w[2] ** 2 * (1 - c) + c, 0],
                  [0, 0, 0, 1]])

    return R


def apply_rotation(R, vec, dim):
    # R is rotation matrix size (4,4)
    # vec is set of vectors (m,3), or (3,m)
    # dim is the dimension that the vector is in: 0 or 1

    if dim == 0:
        vec = np.vstack((vec, np.ones((1, vec.shape[1]))))
        vec_rot = np.dot(R, vec)
        vec_rot = vec_rot[0:3, :]
    elif dim == 1:
        vec = np.hstack((vec, np.ones((vec.shape[0], 1)))).T
        vec_rot = np.dot(R, vec).T
        vec_rot = vec_rot[:, 0:3]

    return vec_rot


def translation_matrix(t):
    T = np.array([[1, 0, 0, t[0]],
                  [0, 1, 0, t[1]],
                  [0, 0, 1, t[2]],
                  [0, 0, 0, 1]])
    return T
