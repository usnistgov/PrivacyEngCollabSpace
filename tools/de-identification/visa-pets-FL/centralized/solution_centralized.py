/*
*   Copyright 2022-2023 Visa
*
*   This code is licensed under the Creative Commons
*   Attribution-NonCommercial 4.0 International Public License 
*   (https://creativecommons.org/licenses/by-nc/4.0/legalcode).
*/
from pathlib import Path

import pandas as pd

import src.DNNCentralizedModule as DNNUtils

from src.DataPrepUtils import (prepare_data_train,
                           prepare_data_test,
                           prepare_bank_data)

def fit(processor_data_path: Path, bank_data_path: Path, model_dir: Path):
    prepare_data = True
    processor_data_path, bank_data_path, model_dir = str(processor_data_path), str(bank_data_path), str(model_dir)
    if prepare_data:
        prepare_data_train(processor_data_path, model_dir)
        prepare_bank_data(bank_data_path, model_dir)
    n_epochs = 20
    final_model_name = model_dir + "model"
    DNNUtils.fit(model_dir, model_dir, model_dir, final_model_name, n_epochs=n_epochs)


def predict(
    processor_data_path: Path,
    bank_data_path: Path,
    model_dir: Path,
    preds_format_path: Path,
    preds_dest_path: Path,
):
    prepare_data = True
    processor_data_path = str(processor_data_path)
    bank_data_path = str(bank_data_path)
    model_dir = str(model_dir)
    preds_format_path = str(preds_format_path)
    preds_dest_path = str(preds_dest_path)
    if prepare_data:
        prepare_data_test(processor_data_path, model_dir)
        prepare_bank_data(bank_data_path, model_dir)
    model_name = model_dir + "model"
    DNNUtils.predict(model_dir, model_dir, model_dir, model_name, preds_dest_path, preds_format_path)

