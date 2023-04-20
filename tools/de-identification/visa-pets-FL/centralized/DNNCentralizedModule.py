/*
*   Copyright 2022-2023 Visa
*
*   This code is licensed under the Creative Commons
*   Attribution-NonCommercial 4.0 International Public License 
*   (https://creativecommons.org/licenses/by-nc/4.0/legalcode).
*/
from pathlib import Path
import numpy as np
import pandas as pd

### Libraries for Algorithms
from sklearn.model_selection import train_test_split, KFold, ShuffleSplit, StratifiedKFold, StratifiedShuffleSplit
from sklearn.model_selection import cross_val_score
from sklearn import metrics
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import StandardScaler, MinMaxScaler

import torch
from torch.utils.data import Dataset, DataLoader
from torch import nn
import torch.nn.functional as F
from src.NeuralNet import NeuralNetwork
from src.DataObjects import CustomDatasetTrain, CustomDatasetTest
import time


BATCH_SIZE_TRAIN = 4096
USE_BANK_INFO = True
device = "cuda"
print("Using {} device".format(device))


def get_flags(idx, X, BankFlagDict):
    # Get bank flag by the status of the receiver bank.
    # The 2nd and 4th item list in idx contains the bid, uid of the receiver bank.
    bankflags = [BankFlagDict[item] if item in BankFlagDict else False for item in zip(idx[1], idx[3])]
    bankflags = [int(item) for item in bankflags]
    bankflags = np.array(bankflags).reshape([-1, 1])
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

def train(dataloader, model, loss_fn, optimizer, bank_flag_dict=None):
    size = len(dataloader.dataset)
    model.train()
    for batch, (idx, X, y) in enumerate(dataloader):
        if USE_BANK_INFO:
            X = get_flags(idx, X, bank_flag_dict)
        X, y = X.to(device), y.to(device)
        pred = model(X.float())
        loss =loss_fn(pred, y)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if (batch%(len(dataloader)//10)) == 0:
            loss, current = loss.item(), batch*len(X)
            print(f"loss: {loss:>7f} [{current:>5d}/{size:>5d}]")
    return model

def test(dataloader, model, loss_fn, bank_flag_dict=None):
    size = len(dataloader.dataset)
    num_batches = len(dataloader)
    model.eval()
    test_loss, correct = 0, 0
    with torch.no_grad():
        for idx, X in dataloader:
            if USE_BANK_INFO:
                X = get_flags(idx, X, bank_flag_dict)
            X = X.to(device)
            pred = model(X.float())
            probs = F.softmax(pred, dim=1)

    return probs

import opacus
import time
from opacus.grad_sample import GradSampleModule
from opacus.grad_sample import register_grad_sampler
from sklearn import metrics

def fit(processor_path, bank_path, model_path, final_model_name, n_epochs=1):
    ### Setup Dataset Path
    train_data_path = processor_path + "train_data_processor.csv"
    train_label_path = processor_path + "train_label.csv"
    bank_flag_dict_path = bank_path + "bank_flag_dict"
    scaler_path = model_path + "scaler"
    
    # load bank flag dictionary
    import pickle
    with open(bank_flag_dict_path, "rb") as f:
        BankFlagDict = pickle.load(f)
    
    dataset_train = CustomDatasetTrain([train_data_path, train_label_path, scaler_path])
    train_dataloader = DataLoader(dataset_train, batch_size=BATCH_SIZE_TRAIN, shuffle=True)
    print("Done! Loading Payment Processor Training")
    
    ### Retrieve Input Dimension for Neural Nets
    X = dataset_train.data
    USE_BANK_INFO = True
    INPUT_DIM = (X.shape)[1]
    if USE_BANK_INFO:
        INPUT_DIM +=1
    print("NN Input Dimension is {}".format(INPUT_DIM))
    
    ### Specify GPU/CPU
    device = "cuda"
    print("Using {} device".format(device))
    model = NeuralNetwork(INPUT_DIM).to(device)
    loss_fn = nn.CrossEntropyLoss()
    
    for t in range(n_epochs):
        print(f"Epoch {t+1}\n-------------------------")
        lr_init = (5e-2/8192)*BATCH_SIZE_TRAIN
        lr = lr_init/np.sqrt(t+1)
        optimizer = torch.optim.SGD(model.parameters(), lr=lr, weight_decay=5e-4)
        t_start = time.time()
        model = train(train_dataloader, model, loss_fn, optimizer, BankFlagDict)
        t_end = time.time()
        print("Training time", t_end - t_start)
        
        # test model save/load
        modelname = model_path+"model"+str(t)
        torch.save(model.state_dict(), modelname)
        pred_model = NeuralNetwork(INPUT_DIM).to(device)
        pred_model.load_state_dict(torch.load(modelname))
        pred_model.to(device)
        
        import gc
        gc.collect()
        
        torch.save(model.state_dict(), final_model_name)
        print("Done")


def predict(processor_path, bank_path, model_path, model_name, res_path, format_path):
        ### Setup Dataset Path
        test_data_path = processor_path + "test_data_processor.csv"
        test_label_path = None
        bank_flag_dict_path = bank_path + "bank_flag_dict"
        scaler_path = model_path + "scaler"
        # load bank flag dictionary
        import pickle
        with open(bank_flag_dict_path, "rb") as f:
                BankFlagDict = pickle.load(f)

        dataset = CustomDatasetTest([test_data_path, test_label_path, scaler_path])
        test_dataloader = DataLoader(dataset, batch_size=len(dataset), shuffle=False)
        print("Done! Loading Payment Processor Test")


        ### Retrieve Input Dimension for Neural Nets
        X = dataset.data
        USE_BANK_INFO = True
        INPUT_DIM = (X.shape)[1]
        if USE_BANK_INFO:
                INPUT_DIM +=1
        print("NN Input Dimension is {}".format(INPUT_DIM))

        ### Specify GPU/CPU
        device = "cuda"
        print("Using {} device".format(device))

        loss_fn = nn.CrossEntropyLoss()

        labelpath = test_data_path
        label_df = pd.read_csv(labelpath)

        label_format = pd.read_csv(format_path)

        pred_model = NeuralNetwork(INPUT_DIM).to(device)
        pred_model.load_state_dict(torch.load(model_name))
        pred_model.to(device)
        pred_model.eval()
        probs = test(test_dataloader, pred_model, loss_fn, BankFlagDict)
        y_score = probs[:, 1].cpu().numpy().tolist()
        label_df["Score"] = y_score
        print(label_df.columns)
        final_res = label_format.merge(label_df, on="MessageId", how="left")
        print(label_df.columns, label_format.columns, final_res.columns)
        final_res = final_res.fillna(1e-8)
        final_res = final_res.rename(columns={"Score_y":"Score"})
        print(final_res.columns)
        final_res[["MessageId", "Score"]].to_csv(res_path, index=False)
        print("Done")

