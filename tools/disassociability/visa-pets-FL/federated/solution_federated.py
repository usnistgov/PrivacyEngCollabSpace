/*
*   Copyright 2022-2023 Visa
*
*   This code is licensed under the Creative Commons
*   Attribution-NonCommercial 4.0 International Public License 
*   (https://creativecommons.org/licenses/by-nc/4.0/legalcode).
*/
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import flwr as fl
from flwr.common import FitIns, FitRes, Parameters
from flwr.server import ClientManager
from flwr.server.client_proxy import ClientProxy
from loguru import logger
import numpy as np
import pandas as pd
import pickle
import itertools
import traceback
import torch
import os
from torch.utils.data import DataLoader
from hashlib import sha256
import torch.nn.functional as F

from .DataPrepUtils import (
    prepare_data_train,
    prepare_data_test,
    prepare_bank_data
)

from .DataObjects import (
    CustomDatasetTest,
    CustomDatasetTrain
)

from .DNN import *

from .ot import (
    senderSetup1,
    receiverSetup, 
    senderSetup2,
    receiverGenKeys, 
    senderGenKeys,
    senderEncrypt,
    receiverDecrypt
)

STAGE_UPCYCLE = 1
STAGE_DOWNCYCLE = 2
STAGE_SENDING = 3
STAGE_WAIT_FOR_GRADIENT = 4
STAGE_FINISHED_SENDING = 5
STAGE_DONE = 6

SAMPLES_PER_ROUND_LIMIT = 2400
DEFAULT_FLAG = 0

TRAIN_ROUNDS = 250 #350
TEST_ROUNDS = 2

NOISE_MEAN = 0
NOISE_SCALE = .1
NOISE_MULTIPLIER = 1e3

DEVICE = "cpu"
#DEVICE = "cuda"
TRAIN_BATCH_SIZE = 8192*10

def empty_parameters() -> Parameters:
    """Utility function that generates empty Flower Parameters dataclass instance."""
    return fl.common.ndarrays_to_parameters([])


def df_to_ndarrays(
    df: pd.DataFrame, labels: bool = True
) -> List[np.ndarray]:
    """Utility function that converts a pandas DataFrame of data to a list of
    numpy arrays, which the expected format for communication between a Flower
    NumPyClient and a Flower Strategy."""
    cols = [
        "FinalReceiver",
        "BeneficiaryAccount",
    ]
    if labels:
        cols.append("Label")
    # Need .astype("U") because pandas uses 'object' for string columns by default
    # 'object' arrays are not serializable without pickle.
    return [
        # Index
        df.index.values.astype("U"),
        # Transactions: Join keys and label
        df[cols].values.astype("U"),
    ]


def ndarrays_to_df(
    index: np.ndarray, transactions: np.ndarray, labels: bool = True
) -> pd.DataFrame:
    """Utility function that converts a list of numpy arrays, which the expected format
    for communication between a Flower NumPyClient and a Flower Strategy, back to a
    pandas DataFrame"""
    cols = [
        "FinalReceiver",
        "BeneficiaryAccount",
    ]
    if labels:
        cols.append("Label")
    return pd.DataFrame(
        data=transactions,
        index=pd.Series(index, name="MessageId"),
        columns=cols,
    )

def checkTensor(tensor):
    return (tensor[0], tensor[1], tensor[-1], tensor[-2])

class TrainingClient(fl.client.NumPyClient):
    def __init__(
        self, cid: str, data_path: Path, client_dir: Path
    ):
        super().__init__()
        self.cid = cid
        self.data_path = data_path
        self.client_dir = client_dir
        self.ot_dir = Path.joinpath(self.client_dir, "ot")
        if not os.path.isdir(self.ot_dir):
            os.mkdir(self.ot_dir)

    def init_stage(self, n_batches):
        stage = STAGE_UPCYCLE
        batch_index = 0
        epoch_index = 0
        d = {"stage": stage, "batch": batch_index, "epoch": epoch_index, "n": n_batches}
        torch.save(d, Path.joinpath(self.client_dir, "stage.pl"))
    
    def load_stage(self):
        d = torch.load(Path.joinpath(self.client_dir, "stage.pl"))
        return (d["stage"], d["batch"], d["epoch"], d["n"])
    
    def save_stage(self, stage, batch_index, epoch_index, n_batches):
        d = {"stage": stage, "batch": batch_index, "epoch": epoch_index, "n": n_batches}
        torch.save(d, Path.joinpath(self.client_dir, "stage.pl"))

    def fit(self, parameters: List[np.ndarray], config: dict):
        round = config["round"]
        #logger.info("CID: {}, ROUND: {}", self.cid, round)
        metrics = {}
        try:
            if round == 1:
                prepare_data_train(self.data_path, self.client_dir)
                train_data_path = Path.joinpath(self.client_dir, 'train_data_processor.csv')
                train_label_path = Path.joinpath(self.client_dir, 'train_label.csv')
                scaler_path = Path.joinpath(self.client_dir, "scaler")
                dataset_train = CustomDatasetTrain([train_data_path, train_label_path, scaler_path])
                train_dataloader = DataLoader(dataset_train, batch_size=TRAIN_BATCH_SIZE, shuffle=True)
                print("Done! Loading Payment Processo Training")
                for batch, (idx, X, y) in enumerate(train_dataloader):
                    torch.save({"idx":idx, "X":X, "y":y}, Path.joinpath(self.client_dir, str(batch)))
                n_batches = len(train_dataloader)
                self.init_stage(n_batches)
                return [], 1, metrics
            elif round == 2:
                partitions:Dict = pickle.loads(config["banks"])
                bank_dict = {}
                partition_ids = []
                setups = {}
                for partition, banks in partitions.items():
                    partition_ids.append(partition)
                    setups[partition] = senderSetup1(str(self.ot_dir), partition)
                    bank_dict.update(zip(banks, itertools.repeat(partition)))
                torch.save(partition_ids, Path.joinpath(self.client_dir, "pids.pl"))
                torch.save(bank_dict, Path.joinpath(self.client_dir, "bank_dict.pl"))
                unknown_accounts = pd.read_csv(Path.joinpath(self.client_dir, "unknown_accounts.csv"))
                maxAccountLen = max((unknown_accounts["Receiver"] + unknown_accounts["BeneficiaryAccount"]).str.len())
                #logger.info("MAX ACCOUNT LEN: {}", maxAccountLen)
                torch.save(maxAccountLen, Path.joinpath(self.client_dir, "max.pl"))
                unknown_accounts['partition'] = unknown_accounts['Receiver'].map(bank_dict)
                #logger.info(unknown_accounts.head())
                accounts = {k: zip(df["Receiver"], df["BeneficiaryAccount"]) for k, df in unknown_accounts.groupby("partition")}
                for partition_id in partition_ids:
                    if(accounts.get(partition_id)):
                        metrics[partition_id] = pickle.dumps((setups[partition_id][0], setups[partition_id][1], accounts.get(partition_id), maxAccountLen))
                for account in accounts.keys():
                    accounts[account] = set(accounts[account])
                torch.save(accounts, Path.joinpath(self.client_dir, "unknown_accounts.pl"))

                return [], 1, metrics
            elif round == 3:
                return [], 1, {}
            elif round == 4:
                partition_ids = torch.load(Path.joinpath(self.client_dir, "pids.pl"))
                accounts = torch.load(Path.joinpath(self.client_dir, "unknown_accounts.pl"))
                maxAccountLen = torch.load(Path.joinpath(self.client_dir, "max.pl"))

                for partition_id in partition_ids:
                    if(config.get(partition_id)):
                        q, q_size, r, r_size = pickle.loads(config[partition_id])
                        senderSetup2(str(self.ot_dir), partition_id, q, q_size)
                        acc = sorted(accounts[partition_id])
                        acc = [a[0] + a[1] for a in acc]

                        senderGenKeys(str(self.ot_dir), partition_id, acc, r, r_size, maxAccountLen)
                
            stage, batch_index, epoch_index, n_batches = self.load_stage()
            self.n_batches = n_batches
            if stage == STAGE_WAIT_FOR_GRADIENT:
                stage = STAGE_DOWNCYCLE
            if stage == STAGE_FINISHED_SENDING:
                stage = STAGE_WAIT_FOR_GRADIENT
            if stage == STAGE_DOWNCYCLE:
                noisy_gradient = pickle.loads(config["noisy_gradient"])
                self.train_down_cycle(noisy_gradient, batch_index, epoch_index)
                batch_index += 1
                if batch_index >= n_batches:
                    batch_index = 0
                    epoch_index += 1
                stage = STAGE_UPCYCLE
            if stage == STAGE_UPCYCLE:
                self.train_up_cycle(batch_index, epoch_index)
                stage = STAGE_SENDING
            if stage == STAGE_SENDING:
                finished, can_send = self.send()
                if finished:
                    stage = STAGE_FINISHED_SENDING
                else:
                    stage = STAGE_SENDING
                for p in can_send:
                    metrics[p] = pickle.dumps(can_send[p])
            metrics["stage"] = stage
            self.save_stage(stage, batch_index, epoch_index, n_batches)
            return [], 1, metrics

        except Exception:
            traceback.print_exc()
            
        return [], 1, {}

    def send(self):
        partition_results: dict = torch.load(Path.joinpath(self.client_dir, "tosend.pl"))
        can_send = {}
        sending = 0
        finished = True
        to_pop = []
        for p in partition_results.keys():
            ids, g0enc, g1enc, grad_len = partition_results[p]
            if(len(ids) > SAMPLES_PER_ROUND_LIMIT - sending):
                sendingIds = ids[:SAMPLES_PER_ROUND_LIMIT - sending]
                sending0 = g0enc[:SAMPLES_PER_ROUND_LIMIT - sending]
                sending1 = g1enc[:SAMPLES_PER_ROUND_LIMIT - sending]
                ids = ids[SAMPLES_PER_ROUND_LIMIT - sending:]
                g0enc = g0enc[SAMPLES_PER_ROUND_LIMIT - sending:]
                g1enc = g1enc[SAMPLES_PER_ROUND_LIMIT - sending:]
                partition_results[p] = (ids, g0enc, g1enc, grad_len)
                can_send[p] = (sendingIds, sending0, sending1, grad_len)
                finished = False
                break
            sending += len(ids)
            can_send[p] = (ids, g0enc, g1enc, grad_len)
            to_pop.append(p)
        for p in to_pop:
            partition_results.pop(p)
        if not finished:
            torch.save(partition_results, Path.joinpath(self.client_dir, "tosend.pl"))
        return finished, can_send



    def train_up_cycle(self,
                   i_batch=0,
                   i_epoch=0,
                   input_dim=18):
        PATH = str(self.client_dir)+'tmp'
        #TODO: Load partition_ids and bank_dict
        model, optimizer, loss_fn = init_learning(device=DEVICE, batch_size=TRAIN_BATCH_SIZE, i_epoch=i_epoch, INPUT_DIM=input_dim, model=None)
        if i_batch != 0 or i_epoch != 0:
            checkpoint = torch.load(PATH)
            model.load_state_dict(checkpoint["model_state_dict"])
            model = model.to(DEVICE)
        model.train()
        data = torch.load(Path.joinpath(self.client_dir, str(i_batch)))
        idx, X, y = data["idx"], data["X"], data["y"]
        batch_size = (X.shape)[0]
        X0, X1 = pad_flags(X, 0), pad_flags(X, 1)
        X = torch.concat([X0, X1], axis=0)
        y = torch.concat([y, y], axis=0)
        X, y = X.to(DEVICE), y.to(DEVICE)
        pred = model(X.float())
        loss = loss_fn(pred, y)

        optimizer.zero_grad()
        loss.backward()

        # Flatten the gradients
        grads_flat, param_shapes = flatten_grads(model)

        # Norm clipping 
        MAX_NORM = 1000
        grads_flat = norm_clipping(grads_flat, max_norm=MAX_NORM)

        # Prepare for serialization
        g0, g1, eps = prepare_serialization(grads_flat, device=DEVICE)
        eps_sum = torch.sum(eps, axis=0, dtype=torch.int32)
        #g0, g1 = g0.to("cpu"), g1.to("cpu") # May need to convert to cpu tensor for serialization
        data_ptr0, data_ptr1 = g0.data_ptr, g1.data_ptr
        
        bid_uid_lst = [item for item in zip(idx[1], idx[3])]
        #logger.info("SAMPLES TO ENC: {}", len(bid_uid_lst))
        partition_bid_uids = {}
        partition_grads0 = {}
        partition_grads1 = {}
        partition_results = {}
        partition_ids = torch.load(Path.joinpath(self.client_dir, "pids.pl"))
        bank_dict = torch.load(Path.joinpath(self.client_dir, "bank_dict.pl"))
        maxAccountLen = torch.load(Path.joinpath(self.client_dir, "max.pl"))

        for partition_id in partition_ids:
            partition_bid_uids[partition_id] = []
            partition_grads0[partition_id] = []
            partition_grads1[partition_id] = []

        unknown_accounts = torch.load(Path.joinpath(self.client_dir, "unknown_accounts.pl"))

        skipped = 0
        for i, id in enumerate(bid_uid_lst):
            p = bank_dict[id[0]]
            if id not in unknown_accounts[p]:
                eps_sum = torch.subtract(eps_sum, g0[i])
                skipped += 1
                continue
            partition_bid_uids[p].append(id)
            partition_grads0[p].append(g0[i])
            partition_grads1[p].append(g1[i])
        grad_len = len(g0[0])
        #logger.info("GRADIENT LENGTH: {}", grad_len)
        #logger.info("ABLE TO SKIP {} SAMPLES", skipped)
        
        for partition_id in partition_ids:
            if(len(partition_grads0[partition_id]) == 0):
                continue
            #logger.info("PARTITION {}: {} SAMPLES", partition_id, len(partition_grads0[partition_id]))
            g0 = torch.stack(partition_grads0[partition_id], axis=0)
            g1 = torch.stack(partition_grads1[partition_id], axis=0)
            ids = partition_bid_uids[partition_id]
            #logger.info("SHAPE: {}", g0.shape)
            
            #logger.info("PARTITION: {}, ID: {}, G0: {}, G1: {}", partition_id, ids[0], g0[0], g1[0])
            g0enc, g1enc = senderEncrypt(ids, g0, g1, str(self.ot_dir), partition_id, grad_len, maxAccountLen)
            partition_results[partition_id] = (ids, g0enc, g1enc, grad_len)

        torch.save(partition_results, Path.joinpath(self.client_dir, "tosend.pl"))
        torch.save({"model_state_dict": model.state_dict(),
                    "optimizer_state_dict": optimizer.state_dict(),
                    "loss": loss,
                    "grads_flat": grads_flat,
                    "eps_sum": eps_sum,
                    "param_shapes": param_shapes
                    }, PATH)
        return

    def train_down_cycle(self, noisy_gradient, i_batch=0, i_epoch=0, 
                     input_dim=18):

        model, optimizer, loss_fn = init_learning(i_epoch=i_epoch, INPUT_DIM=input_dim, device=DEVICE, batch_size=TRAIN_BATCH_SIZE)
        PATH = str(self.client_dir)+'tmp'
        checkpoint = torch.load(PATH)
        model.load_state_dict(checkpoint["model_state_dict"])
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        loss = checkpoint["loss"]
        grads_flat = checkpoint["grads_flat"].to(DEVICE)
        eps_sum = checkpoint["eps_sum"].to(torch.int32)
        param_shapes = checkpoint["param_shapes"]
        model = model.to(DEVICE)
        model.train()
        #end_time_load = time.time()
        #print("Save/load for one batch takes {}".format(end_time_load-start_time_save))

        # Get the gradients from Aggregator
        #grads_flat = get_aggregated_grads(g0.to(device))
        #grads_flat = grads_flat.to(device)

        # Deserialize the grads for backprop
        grads_flat = complete_deserialization(noisy_gradient, eps_sum)
        batch_size = TRAIN_BATCH_SIZE
        grads_flat /= batch_size

        # Reshape the flattened per-sample gradient back to gradient matrices.
        expand_flattened_grads(model, grads_flat, param_shapes)

        optimizer.step()
        clear_per_sample_grad(model)

        loss = loss.item()
        logger.info("LOSS AND CURRENT BATCH: {} {}/{}, EPOCH {}", loss, i_batch, self.n_batches, i_epoch)

        torch.save({"model_state_dict":model.state_dict()}, PATH)



class TrainingBankClient(fl.client.NumPyClient):
    def __init__(
        self, cid: str, data_path: Path, client_dir: Path
    ):
        super().__init__()
        self.cid = cid
        self.data_path = data_path
        self.client_dir = client_dir
        self.ot_dir = Path.joinpath(client_dir, "ot")
        if not os.path.isdir(self.ot_dir):
            os.mkdir(self.ot_dir)

    def fit(
        self, parameters: List[np.ndarray], config: dict
    ) -> Tuple[List[np.ndarray], int, dict]:
        round = config["round"]
        logger.info("CID: {}, ROUND: {}", self.cid, round)
        metrics = {}
        try:
            # Round 1: Send banks in this partition to strategy
            if round == 1:
                bank_ids = prepare_bank_data(self.data_path, self.client_dir)
                #logger.info("{} has {} banks", self.cid, len(bank_ids))
                metrics["banks"] = pickle.dumps(bank_ids)
                return [], 1, metrics
            elif round == 3:
                if config.get("setup"):
                    p, p_len, unknown_accounts, maxAccountLen = pickle.loads(config["setup"])
                    q, q_size = receiverSetup(str(self.ot_dir), self.cid, p, p_len)
                    bank_dict = torch.load(Path.joinpath(self.client_dir, "bank_flag_dict"))
                    unknown_accounts = sorted(set(unknown_accounts))
                    choices = [bank_dict.get(a, 0) for a in unknown_accounts]
                    unknown_accounts = [a[0] + a[1] for a in unknown_accounts]
                    #logger.info("{} ACC HASH: {}", self.cid, sha256(''.join(unknown_accounts).encode("utf-8")).digest())
                    r, r_size = receiverGenKeys(str(self.ot_dir), self.cid, choices, unknown_accounts, maxAccountLen)
                    torch.save(maxAccountLen, Path.joinpath(self.client_dir, "max.pl"))
                    metrics["qr"] = pickle.dumps((q, q_size, r, r_size)) 
                return [], 1, metrics
            else:
                if config.get("grads"):
                    ids, g0enc, g1enc, grad_len = pickle.loads(config["grads"])
                    bank_dict = torch.load(Path.joinpath(self.client_dir, "bank_flag_dict"))
                    maxAccountLen = torch.load(Path.joinpath(self.client_dir, "max.pl"))
                    choices = [bank_dict.get((x, y), 0) for (x, y) in ids]
                    #logger.info(len(choices))
                    #logger.info("SHAPE: ", g0enc.shape)
                    grad = receiverDecrypt(ids, g0enc, g1enc, str(self.ot_dir), self.cid, grad_len, choices, maxAccountLen)
                    #logger.info("PARTITION: {}, ID: {}, HASH: {}, CHOICE: {}", self.cid, ids[0], grad[0], choices[0])
                    grad = torch.sum(grad, dim=0)
                    metrics["grad"] = pickle.dumps(grad)
                return [], 1, metrics

        except Exception:
            traceback.print_exc()
        return [], 1, {}

def train_client_factory(cid, data_path: Path, client_dir: Path):
    if cid == "swift":
        return TrainingClient(
            cid, data_path=data_path, client_dir=client_dir
        )
    else:
        return TrainingBankClient(
            cid, data_path=data_path, client_dir=client_dir
        )


class TrainStrategy(fl.server.strategy.Strategy):
    def __init__(self, server_dir: Path):
        self.server_dir = server_dir
        self.labels_for_banks = None
        self.banks_dict = {}
        self.processor_param_dict = {}
        self.processor_config_dict = {}
        self.bank_config_dict = {}
        self.banks = []
        self.current_grad = None
        super().__init__()

    def initialize_parameters(self, client_manager: ClientManager) -> Parameters:
        """Do nothing. Return empty Flower Parameters dataclass."""
        client_dict: Dict[str, ClientProxy] = client_manager.all()
        self.banks = [cid for cid in client_dict.keys() if cid != "swift"]
        return empty_parameters()

    def configure_fit(
        self, server_round: int, parameters: Parameters, client_manager: ClientManager
    ) -> List[Tuple[ClientProxy, FitIns]]:
        client_dict: Dict[str, ClientProxy] = client_manager.all()
        config_dict = {"round": server_round}
        fit_config: List[Tuple[ClientProxy, FitIns]] = []
        processor_config = dict(config_dict)
        processor_parameters = empty_parameters()
        bank_cids = [cid for cid in client_dict.keys() if cid != "swift"]
        bank_parameters = {}
        bank_config = {}
        for cid in bank_cids:
            bank_parameters[cid] = empty_parameters()
            bank_config[cid] = dict(config_dict)
        if server_round == 1:
            pass
        elif server_round == 2:
            processor_config["banks"] = pickle.dumps(self.bank_config_dict)
        elif server_round == 3:
            for cid in bank_cids:
                bank_parameters[cid] = self.processor_param_dict.get(cid, empty_parameters())
                bank_config[cid].update(self.processor_config_dict.get(cid, {}))
        elif server_round == 4:
            processor_config.update(self.bank_config_dict)
        else:
            if self.stage == STAGE_WAIT_FOR_GRADIENT:
                noise = np.random.laplace(NOISE_MEAN, NOISE_SCALE, self.current_grad.shape)
                self.current_grad = self.current_grad.add(torch.multiply(torch.tensor(noise), NOISE_MULTIPLIER).int())
                processor_config["noisy_gradient"] = pickle.dumps(self.current_grad)
                self.current_grad = None
            if self.stage == STAGE_SENDING or self.stage == STAGE_FINISHED_SENDING:
                for cid in bank_cids:
                    bank_config[cid].update(self.processor_config_dict.get(cid, {}))
        
        processor_fit_ins = FitIns(parameters=processor_parameters, config=processor_config)
        fit_config += [(client_dict["swift"], processor_fit_ins)]
        for cid in bank_cids:
            this_bank_fit_ins = FitIns(
                parameters=bank_parameters[cid],
                config=bank_config[cid],
            )
            fit_config.append((client_dict[cid], this_bank_fit_ins))
        return fit_config

    def aggregate_fit(
        self, server_round: int, results: List[Tuple[ClientProxy, FitRes]], failures
    ) -> Tuple[Optional[Parameters], dict]:
        if (n_failures := len(failures)) > 0:
            raise Exception(f"Had {n_failures} failures in round {server_round}")
        self.processor_config_dict = {}
        self.processor_param_dict = {}
        self.bank_config_dict = {}
        if server_round == 1:
            for client, result in results:
                result_ndarrays = fl.common.parameters_to_ndarrays(result.parameters)
                if client.cid != "swift":
                    self.bank_config_dict[client.cid] = pickle.loads(result.metrics["banks"])
        elif server_round == 2:
            for client, result in results:
                result_ndarrays = fl.common.parameters_to_ndarrays(result.parameters)
                if client.cid == "swift":
                    for cid in self.banks:
                        if result.metrics.get(cid):
                            self.processor_config_dict[cid] = {}
                            self.processor_config_dict[cid]["setup"] = result.metrics.get(cid)
        elif server_round == 3:
            for client, result in results:
                result_ndarrays = fl.common.parameters_to_ndarrays(result.parameters)
                if client.cid != "swift":
                    if result.metrics.get("qr"):
                        self.bank_config_dict[client.cid] = result.metrics["qr"]
        else:
            for client, result in results:
                result_ndarrays = fl.common.parameters_to_ndarrays(result.parameters)
                if client.cid == "swift":
                    self.stage = result.metrics["stage"]
                    if self.stage == STAGE_SENDING or self.stage == STAGE_FINISHED_SENDING:
                        for cid in self.banks:
                            if result.metrics.get(cid):
                                self.processor_config_dict[cid] = {}
                                self.processor_config_dict[cid]["grads"] = result.metrics.get(cid)
                else:
                    if result.metrics.get("grad"):
                        if self.current_grad == None:
                            self.current_grad = pickle.loads(result.metrics["grad"])
                        else:
                            self.current_grad = torch.add(self.current_grad, pickle.loads(result.metrics["grad"]))

        return None, {}

    def configure_evaluate(self, server_round, parameters, client_manager):
        """Not running any federated evaluation."""
        return []

    def aggregate_evaluate(self, server_round, results, failures):
        """Not aggregating any evaluation."""
        return None

    def evaluate(self, server_round, parameters):
        """Not running any centralized evaluation."""
        return None


def train_strategy_factory(server_dir: Path):
    training_strategy = TrainStrategy(server_dir=server_dir)
    num_rounds = TRAIN_ROUNDS
    return training_strategy, num_rounds

def test_client_factory(
    cid: str,
    data_path: Path,
    client_dir: Path,
    preds_format_path: Path,
    preds_dest_path: Path,
):
    if cid == "swift":
        return TestProcessorClient(
            cid,
            data_path=data_path,
            client_dir=client_dir,
            preds_format_path=preds_format_path,
            preds_dest_path=preds_dest_path,
        )
    else:
        #logger.info("Initializing bank client for {}", cid)
        return TestBankClient(cid, data_path=data_path, client_dir=client_dir)


class TestProcessorClient(fl.client.NumPyClient):
    def __init__(
        self,
        cid: str,
        data_path: Path,
        client_dir: Path,
        preds_format_path: Path,
        preds_dest_path: Path,
    ):
        super().__init__()
        self.cid = cid
        self.data_path = data_path
        self.client_dir = client_dir
        self.preds_format_path = preds_format_path
        self.preds_dest_path = preds_dest_path
        self.ot_dir = Path.joinpath(client_dir, "ot_test")
        if not os.path.isdir(self.ot_dir):
            os.mkdir(self.ot_dir)

    def init_stage(self):
        stage = STAGE_UPCYCLE
        d = {"stage": stage}
        torch.save(d, Path.joinpath(self.client_dir, "stage.pl"))
    
    def load_stage(self):
        d = torch.load(Path.joinpath(self.client_dir, "stage.pl"))
        return d["stage"]
    
    def save_stage(self, stage):
        d = {"stage": stage}
        torch.save(d, Path.joinpath(self.client_dir, "stage.pl"))

    def fit(
        self, parameters: List[np.ndarray], config: dict
    ) -> Tuple[List[np.ndarray], int, dict]:
        round = config["round"]
        #logger.info("CID: {}, ROUND: {}", self.cid, round)
        metrics = {}
        try:
            if round == 1:
                prepare_data_test(self.data_path, self.client_dir)
                return [], 1, metrics
            elif round == 2:
                flags = pickle.loads(config["flags"])
                self.test_up(flags)
                return [], 1, metrics

        except Exception:
            traceback.print_exc()
            
        return [], 1, {}

    
    def test_up(self, flags):
        test_data_path = Path.joinpath(self.client_dir, 'test_data_processor.csv')
        scaler_path = Path.joinpath(self.client_dir, "scaler")
        dataset_test = CustomDatasetTest([test_data_path, None, scaler_path])
    
        model = GradSampleModule(NeuralNetwork(18).to(DEVICE), force_functorch=True)
        PATH = str(self.client_dir)+'tmp'
        checkpoint = torch.load(PATH)
        model.load_state_dict(checkpoint["model_state_dict"])
        model = model.to(DEVICE)
        model.eval()
        idx, X = dataset_test[:]
        #logger.info("SOME IDS: {}", idx[:5])
        with torch.no_grad():    
            batch_size = (X.shape)[0]
            #X = get_flags(idx, X, bank_flag_dict)
            X0, X1 = pad_flags(X, 0), pad_flags(X, 1)
            X = torch.concat([X0, X1], axis=0)
            X = X.to(DEVICE)
            pred = model(X.float())
  
        s = (pred.shape)[0]//2
        pred0, pred1 = pred[:s, :], pred[s:, :]
        
        bid_uid_lst = [(item[1], item[3]) for item in idx]

        missed = 0
        chosen = []
        for i, id in enumerate(bid_uid_lst):
            flag = flags.get(id, -1)
            if(flag == -1):
                missed += 1
                flag = 0
            if flag == 0:
                p = pred0[i]
            else:
                p = pred1[i]
            p = F.softmax(p, dim=0)
            chosen.append(p)
        
        probs = torch.stack(chosen, axis=0)
        logger.info("PROBS SHAPE: {}", probs.shape)
        logger.info("MISSED: {}", missed)
                
        test_data_path = Path.joinpath(self.client_dir, 'test_data_processor.csv')
        raw_data = pd.read_csv(test_data_path, usecols=["MessageId"])
        raw_data["Score"] = probs[:, 1].numpy().tolist()
        
        res = pd.read_csv(self.preds_format_path)
        res = res.merge(raw_data, on="MessageId", how="left")
        res = res.rename(columns={"Score_y":"Score"})
        res[["MessageId", "Score"]].to_csv(self.preds_dest_path, index=False)
            
        return



class TestBankClient(fl.client.NumPyClient):
    def __init__(self, cid, data_path: Path, client_dir: Path):
        super().__init__()
        self.cid = cid
        self.data_path = data_path
        self.client_dir = client_dir
        self.ot_dir = Path.joinpath(client_dir, "ot_test")
        if not os.path.isdir(self.ot_dir):
            os.mkdir(self.ot_dir)

    def fit(
        self, parameters: List[np.ndarray], config: dict
    ) -> Tuple[List[np.ndarray], int, dict]:
        ## Round 1: Send banks in this partition to strategy
        round = config["round"]
        #logger.info("CID: {}, ROUND: {}", self.cid, round)
        metrics = {}
        try:
            # Round 1: Send banks in this partition to strategy
            if round == 1:
                bank_ids = prepare_bank_data(self.data_path, self.client_dir)
                flagDict = torch.load(Path.joinpath(self.client_dir, "bank_flag_dict"))
                metrics["flags"] = pickle.dumps(flagDict)
                return [], 1, metrics
        except Exception:
            traceback.print_exc()
        return [], 1, {}

def test_strategy_factory(server_dir: Path):
    test_strategy = TestStrategy(server_dir=server_dir)
    num_rounds = TEST_ROUNDS
    return test_strategy, num_rounds


class TestStrategy(fl.server.strategy.Strategy):
    def __init__(self, server_dir: Path):
        self.server_dir = server_dir
        self.labels_for_banks = None
        self.banks_dict = {}
        self.processor_param_dict = {}
        self.processor_config_dict = {}
        self.bank_config_dict = {}
        self.banks = []
        self.indexes = []
        self.preds = []
        self.flags = {}
        super().__init__()

    def initialize_parameters(self, client_manager: ClientManager) -> Parameters:
        """Do nothing. Return empty Flower Parameters dataclass."""
        client_dict: Dict[str, ClientProxy] = client_manager.all()
        self.banks = [cid for cid in client_dict.keys() if cid != "swift"]
        return empty_parameters()

    def configure_fit(
        self, server_round: int, parameters: Parameters, client_manager: ClientManager
    ) -> List[Tuple[ClientProxy, FitIns]]:
        client_dict: Dict[str, ClientProxy] = client_manager.all()
        config_dict = {"round": server_round}
        fit_config: List[Tuple[ClientProxy, FitIns]] = []
        processor_config = dict(config_dict)
        processor_parameters = empty_parameters()
        bank_cids = [cid for cid in client_dict.keys() if cid != "swift"]
        bank_parameters = {}
        bank_config = {}
        for cid in bank_cids:
            bank_parameters[cid] = empty_parameters()
            bank_config[cid] = dict(config_dict)
        if server_round == 1:
            pass
        elif server_round == 2:
            processor_config["flags"] = pickle.dumps(self.flags)
        
        processor_fit_ins = FitIns(parameters=processor_parameters, config=processor_config)
        fit_config += [(client_dict["swift"], processor_fit_ins)]
        for cid in bank_cids:
            this_bank_fit_ins = FitIns(
                parameters=bank_parameters[cid],
                config=bank_config[cid],
            )
            fit_config.append((client_dict[cid], this_bank_fit_ins))
        return fit_config

    def aggregate_fit(
        self, server_round: int, results: List[Tuple[ClientProxy, FitRes]], failures
    ) -> Tuple[Optional[Parameters], dict]:
        if (n_failures := len(failures)) > 0:
            raise Exception(f"Had {n_failures} failures in round {server_round}")

        if server_round == 1:
            for client, result in results:
                result_ndarrays = fl.common.parameters_to_ndarrays(result.parameters)
                if client.cid != "swift":
                    self.flags.update(pickle.loads(result.metrics["flags"]))
        return None, {}

    def configure_evaluate(self, server_round, parameters, client_manager):
        """Not running any federated evaluation."""
        return []

    def aggregate_evaluate(self, server_round, results, failures):
        """Not aggregating any evaluation."""
        return None

    def evaluate(self, server_round, parameters):
        """Not running any centralized evaluation."""
        return None