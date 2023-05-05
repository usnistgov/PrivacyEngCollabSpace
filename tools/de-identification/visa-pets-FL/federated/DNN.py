/*
*   Copyright 2022-2023 Visa
*
*   This code is licensed under the Creative Commons
*   Attribution-NonCommercial 4.0 International Public License 
*   (https://creativecommons.org/licenses/by-nc/4.0/legalcode).
*/
import numpy as np
import torch
from torch import nn
import torch.nn.functional as F

from .NeuralNet import NeuralNetwork
from opacus.grad_sample import GradSampleModule

def pad_flags(X, flag=0):
    # Pad a column of one or zero bank flag.
    n_elem = (X.shape)[0]
    bankflags = np.ones((n_elem, 1))*flag
    bankflags = torch.tensor(bankflags)
    return torch.concat([X, bankflags], axis=1)


def norm_clipping(X, max_norm=1.0):
    # Norm clipping 
    X_norm = torch.norm(X, dim=1)
    X_norm = torch.clamp(X_norm/max_norm, min=1.0)
    X_norm = X_norm.unsqueeze(1).repeat(1, (X.shape)[1])
    return X/X_norm

def to_int(X, factor=1e6, dtype=torch.int32):
    return (X*factor).to(dtype)

def to_float(X, factor=1e6, dtype=torch.float):
    return (X.to(dtype))/factor

def get_aggregated_grads(X):
    return torch.sum(X, axis=0)

def get_noise(shape, device, dtype=torch.int32):
    if dtype==torch.int32:
        low, high = -2147483648, 2147483648 
    return torch.randint(low, high, shape, dtype=dtype, device=device)

def flatten_grads(model):
    grads_flat = []
    param_shapes = []
    for i, p in enumerate(model.parameters()):
        param_shapes.append(p.grad.shape)
        grads_flat.append(torch.flatten(p.grad_sample, start_dim=1))
    grads_flat = torch.cat(grads_flat, axis=1)
    grads_flat = torch.nan_to_num(grads_flat)
    return grads_flat, param_shapes


def expand_flattened_grads(model, grads_flat, param_shapes):
    curr_pos = 0
    for i, p in enumerate(model.parameters()):
        param_shape = param_shapes[i]
        n_param = np.prod(param_shape)
        end_pos = curr_pos+n_param
        p.grad = grads_flat[curr_pos:end_pos].reshape(param_shape)
        curr_pos = end_pos

def clear_per_sample_grad(model):
    for i, p in enumerate(model.parameters()):
        p.grad_sample = None


def prepare_serialization(g, device, scale=1e3, dtype=torch.int32):

    # Convert the input to integer value
    g = to_int(g, factor=scale, dtype=dtype)

    # Split the gradients with flag 0 and 1
    s = (g.shape)[0]//2
    g0, g1 = g[:s, :], g[s:, :]

    eps = get_noise(g0.shape, device=device)
    eps_sum = torch.sum(eps, axis=0, dtype=torch.int32)
    g0 = (g0+eps).to(torch.int32)
    g1 = (g1+eps).to(torch.int32)

    
    return g0, g1, eps

def prepare_serialization_with_rounding(g, device, dtype=torch.int32):

    # Split the gradients with flag 0 and 1
    s = (g.shape)[0]//2
    g0, g1 = g[:s, :], g[s:, :]
    g0 = torch.argmax(g0, dim=1)
    g1 = torch.argmax(g1, dim=1)
    
    eps = get_noise(g0.shape, device=device)
    #eps = torch.zeros(g0.shape)
    eps_sum = torch.sum(eps, axis=0, dtype=torch.int32)
    g0 = (g0+eps).to(torch.int32)
    g1 = (g1+eps).to(torch.int32)

    
    return g0, g1, eps

def complete_deserialization(g, eps, 
                             scale=1e3, 
                             dtype_int=torch.int32, 
                             dtype_float=torch.float):
    
    # Subtract the random int used for OT
    g = (g-eps).to(dtype_int)
    # Convert back to real value after OT
    g = to_float(g, factor=scale, dtype=dtype_float)
    return g

def init_learning(device, 
               batch_size,
               i_epoch, model=None,
               INPUT_DIM=9):
    if model==None:
        model = GradSampleModule(NeuralNetwork(INPUT_DIM).to(device), force_functorch=True)
    loss_fn = nn.CrossEntropyLoss()
    batch_size = batch_size
    lr_init = (5e-2/8192)*batch_size
    lr = lr_init/np.sqrt(i_epoch+1)
    optimizer = torch.optim.SGD(model.parameters(), lr=lr, weight_decay=1e-5)
    return model, optimizer, loss_fn