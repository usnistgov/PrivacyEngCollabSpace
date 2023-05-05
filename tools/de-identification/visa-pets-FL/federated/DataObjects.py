/*
*   Copyright 2022-2023 Visa
*
*   This code is licensed under the Creative Commons
*   Attribution-NonCommercial 4.0 International Public License 
*   (https://creativecommons.org/licenses/by-nc/4.0/legalcode).
*/
import numpy as np
import pandas as pd
pd.set_option("display.max_columns", None)
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import torch
from torch.utils.data import Dataset, DataLoader
import pickle

class CustomDatasetTrain(Dataset):
    def __init__(self, paths):
        [train_data_path, train_label_path, scaler_path] = paths
        raw_data = pd.read_csv(train_data_path, index_col="MessageId")
        col = raw_data.columns
        print(col)

        id_cols = ["Sender", "Receiver", "OrderingAccount", "BeneficiaryAccount"]
        ids = raw_data[id_cols]
        self.ids = ids.values.tolist()
        data = raw_data.drop(columns=id_cols)
        self.data = data.values
        print(self.data.shape)

        scaler = StandardScaler()
        scaler.fit(self.data)
        self.data = scaler.transform(self.data)
        with open(scaler_path, "wb") as f:
            pickle.dump(scaler, f)

        label = pd.read_csv(train_label_path, index_col="MessageId")
        self.label = label.values

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        ids = self.ids[idx]
        tensor = torch.from_numpy(self.data[idx])
        class_id = torch.tensor(self.label[idx][-1])
        return ids, tensor, class_id


class CustomDatasetTest(Dataset):
    def __init__(self, paths):
        [test_data_path, test_label_path, scaler_path] = paths
        raw_data = pd.read_csv(test_data_path, index_col="MessageId")
        col = raw_data.columns
        print(col)

        id_cols = ["Sender", "Receiver", "OrderingAccount", "BeneficiaryAccount"]
        ids = raw_data[id_cols]
        self.ids = ids.values.tolist()
        data = raw_data.drop(columns=id_cols)
        self.data = data.values
        print(self.data.shape)

        with open(scaler_path, "rb") as f:
            scaler = pickle.load(f)
        self.data = scaler.transform(self.data)
        if test_label_path:
            label = pd.read_csv(test_label_path, index_col="MessageId")
            self.label = label.values
            self.is_submission = False
        else:
            self.is_submission = True

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        ids = self.ids[idx]
        tensor = torch.from_numpy(self.data[idx])
        if self.is_submission:
            return ids, tensor
        class_id = torch.tensor(self.label[idx][-1])
        return ids, tensor, class_id
