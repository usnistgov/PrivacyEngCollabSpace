/*
*   Copyright 2022-2023 Visa
*
*   This code is licensed under the Creative Commons
*   Attribution-NonCommercial 4.0 International Public License 
*   (https://creativecommons.org/licenses/by-nc/4.0/legalcode).
*/
import torch
from torch import nn

class NeuralNetwork(nn.Module):
    def __init__(self, input_dim):
        super(NeuralNetwork, self).__init__()
        self.flatten = nn.Flatten()
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(input_dim, 128),
            #nn.ReLU(),
            #nn.Linear(256, 64),
            nn.ReLU(),
            nn.Linear(128, 16),
            nn.ReLU(),
            nn.Linear(16, 2)
        )

    def forward(self, x):
        x = self.flatten(x)
        logits = self.linear_relu_stack(x)
        return logits
