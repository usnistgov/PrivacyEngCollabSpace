/*
*   Copyright 2022-2023 Visa
*
*   This code is licensed under the Creative Commons
*   Attribution-NonCommercial 4.0 International Public License 
*   (https://creativecommons.org/licenses/by-nc/4.0/legalcode).
*/
### Libraries for Data Handling

from pathlib import Path
import numpy as np
import pandas as pd
import copy


pd.set_option("display.max_columns", None)

### Libraries for Algorithms
from sklearn.model_selection import train_test_split, KFold, ShuffleSplit, StratifiedKFold, StratifiedShuffleSplit
from sklearn.model_selection import cross_val_score
from sklearn import metrics
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import sklearn.utils
import pickle
import time

def prepare_data_train(path, work_dir):

    # Load train/test data from csv
    train = pd.read_csv(path)
    train.to_csv(work_dir+'train_copy.csv', index=False)
    train["Timestamp"] = train["Timestamp"].astype("datetime64[ns]")

    train = train.set_index("UETR")
    train = train.sort_values(by=['Timestamp'])
   
    # Frequency for each sender
    
    senders = train["Sender"].unique()
    
    # Frequency for each receiver
    receivers = train["Receiver"].unique()
    
    # If instructed/settled in the same currency
    train["same_currency"] = train.apply(lambda row: int(row['InstructedCurrency']==row['SettlementCurrency']), axis=1)
 
    # Normalize the transaction amount by exchange rate
    exchange_rate = {'GBP':1.22,'EUR':1.08, 'USD':1, 'JPY':0.0078,
                     'CAD':0.75, 'INR':0.012, 'AUD':0.7, 'NZD':0.64,
                     'DKK':0.14,'IDR':0.000066,'MXN':0.054,'ZAR':0.059,
                     'KES':0.0081,'ILS':0.29,'THB':0.03,'TND':0.33,
                     'TRY':0.053, 'SGD':0.76, 'MAD':0.098, 'AED':0.27,
                     'SEK':0.096, 'CHF':1.08, 'SAR':0.27, 'PLN':0.23,
                     'BHD':2.65, "CZK":0.045, "NAD":0.059, "NOK":0.10,
                     "HKD":0.13, "HUF":0.0027, "MYR":0.23, "LKR":0.0027,
                     "CNY":0.15, "EGP":0.034, "KRW":0.00081, "HRK":0.143122,
                     "BDT":0.0096, "PHP":0.018, "BOB":0.14, "RON":0.22,
                     "OMR":2.6, "KWD":3.28, "NPR":0.0076, "FJD":0.46,
                     "MUR":0.023, "JOD":1.41, "VND":0.000043, "ISK":0.0070,
                     "BRL":0.2, "TWD":0.033, "QAR":0.27, "XOF":0.0017,
                     "RSD":0.0092, "COP":0.00021, "BGN":0.55, "RUB":0.015,
                     "BWP":0.078, "TZS":0.00043, "BAM":0.55
            }


    train["exchange_rate"] = train["InstructedCurrency"].map(exchange_rate)
    train["NormalizedAmount"] = train["InstructedAmount"]*train["exchange_rate"]
    train.drop(columns="exchange_rate", inplace=True)

    # Hour
    train["hour"] = train["Timestamp"].dt.hour
    train["day"] = train["Timestamp"].dt.day

    
    join_keys = ['UETR', 'Timestamp']

    start_time = time.time()

    keys = ["OrderingName", "BeneficiaryName", "InstructedCurrency", "SettlementCurrency"]
    fields = ["MessageId", "Timestamp"]
    df = train.groupby(keys)[fields].rolling('28D', closed="left", on="Timestamp").count()
    rename_dict = {item:"sr_currency_pair_avg_count" for item in fields if item not in ["Timestamp"]}
    df = df.rename(rename_dict, axis="columns")
    train = train.merge(df, left_on=join_keys, right_on=join_keys, how="left")
    train["sr_currency_pair_avg_count"] = train["sr_currency_pair_avg_count"]/train["day"]

    print("Feature takes {}".format(time.time()-start_time))
    start_time=time.time()

    df = train.groupby(keys)[fields].rolling('1H', closed="left", on="Timestamp").count()
    rename_dict = {item:"sr_currency_pair_hour_freq" for item in fields if item not in ["Timestamp"]}
    df = df.rename(rename_dict, axis="columns")
    train = train.merge(df, left_on=join_keys, right_on=join_keys, how="left")

    print("Feature takes {}".format(time.time()-start_time))
    start_time=time.time()


    fields = ["SettlementAmount", "Timestamp"]
    df = train.groupby(keys)[fields].rolling(20, min_periods=1 , on="Timestamp").mean()
    rename_dict = {item:item+"sr_pair_avg_settlement_last_20" for item in fields if item not in ["Timestamp"]}
    df = df.rename(rename_dict, axis="columns")
    train = train.merge(df, left_on=join_keys, right_on=join_keys, how="left")

    print("Feature takes {}".format(time.time()-start_time))
    start_time=time.time()


    fields = ["InstructedAmount", "Timestamp"]
    df = train.groupby(keys)[fields].rolling(20, min_periods=1, on="Timestamp").mean()
    rename_dict = {item:item+"sr_pair_avg_instructed_last_20" for item in fields if item not in ["Timestamp"]}
    df = df.rename(rename_dict, axis="columns")
    train = train.merge(df, left_on=join_keys, right_on=join_keys, how="left")


    print("Feature takes {}".format(time.time()-start_time))
    start_time=time.time()


    keys = ["OrderingName", "BeneficiaryName"]
    fields = ["MessageId", "Timestamp"]
    df = train.groupby(keys)[fields].rolling('7D', closed="left", on="Timestamp").count()
    rename_dict = {item:item+"sr_pair_count_last_7d" for item in fields if item not in ["Timestamp"]}
    df = df.rename(rename_dict, axis="columns")
    train = train.merge(df, left_on=join_keys, right_on=join_keys, how="left")


    print("Feature takes {}".format(time.time()-start_time))
    start_time=time.time()


    keys = ["OrderingName"]
    fields = ["NormalizedAmount", "Timestamp"]
    df = train.groupby(keys)[fields].rolling(20, min_periods=1, closed="left", on="Timestamp").mean()
    rename_dict = {item:item+"sender_avg_last_20" for item in fields if item not in ["Timestamp"]}
    df = df.rename(rename_dict, axis="columns")
    train = train.merge(df, left_on=join_keys, right_on=join_keys, how="left")


    print("Feature takes {}".format(time.time()-start_time))
    start_time=time.time()


    keys = ["BeneficiaryName"]
    fields = ["NormalizedAmount", "Timestamp"]
    df = train.groupby(keys)[fields].rolling(20, min_periods=1, closed="left", on="Timestamp").mean()
    rename_dict = {item:item+"receiver_avg_last_20" for item in fields if item not in ["Timestamp"]}
    df = df.rename(rename_dict, axis="columns")
    train = train.merge(df, left_on=join_keys, right_on=join_keys, how="left")

    print("Feature takes {}".format(time.time()-start_time))
    start_time=time.time()


    print(train.columns[train.isna().any()].tolist())

    train.drop(columns=["day", "hour"], inplace=True)
    train = train.fillna(0)
    # Exclude below categorical columns for training and testing
    columns_to_drop = [
		#"UETR",
		"TransactionReference",
		"OrderingName",
		"OrderingStreet",
		"OrderingCountryCityZip",
		"BeneficiaryName",
		"BeneficiaryStreet",
		"BeneficiaryCountryCityZip",
		"SettlementDate",
		"SettlementCurrency",
		"InstructedCurrency",
		"Timestamp"
        ]

    train = train.drop(columns_to_drop, axis=1)

    print("train columns are", train.columns)
    train[train.select_dtypes(include=['number']).columns] = train[train.select_dtypes(include=['number']).columns].clip(-1e20, 1e20)

    pd_train = train
    pd_train['Label'].to_csv(work_dir+"train_label.csv")

    from sklearn.utils import resample
    pd_majority = pd_train[pd_train.Label==0]
    pd_minority = pd_train[pd_train.Label==1]

    print(len(pd_majority), len(pd_minority))

    pd_minority_upsampled = resample(pd_minority,
		                     replace=True,
		                     n_samples=int(len(pd_majority)),
		                     random_state=42)
    
    print(len(pd_majority), len(pd_minority_upsampled))
    pd_train = pd.concat([pd_majority, pd_minority_upsampled])
    DOWNSAMPLE_FACTOR = 1

    pd_train_subset = resample(pd_train,
		               replace=False,
		               n_samples=int(len(pd_train)/DOWNSAMPLE_FACTOR),
		               random_state=42)

    pd_train_temp = pd_train_subset
    pd_train_temp = pd_train_temp.fillna(0)
    columns_to_drop = ["Label"]
    pd_train_temp[['MessageId', 'Label']].to_csv(work_dir+'train_label.csv', index=False)
    pd_train_temp.drop(columns=columns_to_drop, inplace=True)
    pd_train_temp.to_csv(work_dir+'train_data_processor.csv', index=False)



def prepare_data_test(path, work_dir):

    TEST_MODE = False
    test = pd.read_csv(path)
    actual_test = copy.deepcopy(test)
    train = pd.read_csv(work_dir+'train_copy.csv')
    test["Timestamp"] = test["Timestamp"].astype("datetime64[ns]")
    train["Timestamp"] = train["Timestamp"].astype("datetime64[ns]")
    actual_test["Timestamp"] = actual_test["Timestamp"].astype("datetime64[ns]")
    if TEST_MODE:
        test = pd.concat([train, test.drop(columns=["Label"])])
    else:
        test = pd.concat([train, test])
    test = test.set_index('UETR')
    test["Timestamp"] = test["Timestamp"].astype("datetime64[ns]")

    test = test.sort_values(by=['Timestamp'])
    test["same_currency"] = test.apply(lambda row: int(row['InstructedCurrency']==row['SettlementCurrency']), axis=1)

    exchange_rate = {'GBP':1.22,'EUR':1.08, 'USD':1, 'JPY':0.0078,
                     'CAD':0.75, 'INR':0.012, 'AUD':0.7, 'NZD':0.64,
                     'DKK':0.14,'IDR':0.000066,'MXN':0.054,'ZAR':0.059,
                     'KES':0.0081,'ILS':0.29,'THB':0.03,'TND':0.33,
                     'TRY':0.053, 'SGD':0.76, 'MAD':0.098, 'AED':0.27,
                     'SEK':0.096, 'CHF':1.08, 'SAR':0.27, 'PLN':0.23,
                     'BHD':2.65, "CZK":0.045, "NAD":0.059, "NOK":0.10,
                     "HKD":0.13, "HUF":0.0027, "MYR":0.23, "LKR":0.0027,
                     "CNY":0.15, "EGP":0.034, "KRW":0.00081, "HRK":0.143122,
                     "BDT":0.0096, "PHP":0.018, "BOB":0.14, "RON":0.22,
                     "OMR":2.6, "KWD":3.28, "NPR":0.0076, "FJD":0.46,
                     "MUR":0.023, "JOD":1.41, "VND":0.000043, "ISK":0.0070,
                     "BRL":0.2, "TWD":0.033, "QAR":0.27, "XOF":0.0017,
                     "RSD":0.0092, "COP":0.00021, "BGN":0.55, "RUB":0.015,
                     "BWP":0.078, "TZS":0.00043, "BAM":0.55
            }
    
    test["exchange_rate"] = test["InstructedCurrency"].map(exchange_rate)
    test["NormalizedAmount"] = test["InstructedAmount"]*test["exchange_rate"]
    test.drop(columns="exchange_rate", inplace=True)

    test["hour"] = test["Timestamp"].dt.hour
    test["day"] = test["Timestamp"].dt.day


    join_keys = ['UETR', 'Timestamp']

    keys = ["OrderingName", "BeneficiaryName", "InstructedCurrency", "SettlementCurrency"]
    fields = ["MessageId", "Timestamp"]
    df = test.groupby(keys)[fields].rolling('28D', closed="left", on="Timestamp").count()
    rename_dict = {item:"sr_currency_pair_avg_count" for item in fields if item not in ["Timestamp"]}
    df = df.rename(rename_dict, axis="columns")
    test = test.merge(df, left_on=join_keys, right_on=join_keys, how="left")
    test["sr_currency_pair_avg_count"] = test["sr_currency_pair_avg_count"]/test["day"]


    df = test.groupby(keys)[fields].rolling('1H', closed="left", on="Timestamp").count()
    rename_dict = {item:"sr_currency_pair_hour_freq" for item in fields if item not in ["Timestamp"]}
    df = df.rename(rename_dict, axis="columns")
    test = test.merge(df, left_on=join_keys, right_on=join_keys, how="left")

    fields = ["SettlementAmount", "Timestamp"]
    df = test.groupby(keys)[fields].rolling(20, min_periods=1, on="Timestamp").mean()
    rename_dict = {item:item+"sr_pair_avg_settlement_last_20" for item in fields if item not in ["Timestamp"]}
    df = df.rename(rename_dict, axis="columns")
    test = test.merge(df, left_on=join_keys, right_on=join_keys, how="left")

    fields = ["InstructedAmount", "Timestamp"]
    df = test.groupby(keys)[fields].rolling(20, min_periods=1, on="Timestamp").mean()
    rename_dict = {item:item+"sr_pair_avg_instructed_last_20" for item in fields if item not in ["Timestamp"]}
    df = df.rename(rename_dict, axis="columns")
    test = test.merge(df, left_on=join_keys, right_on=join_keys, how="left")


    keys = ["OrderingName", "BeneficiaryName"]
    fields = ["MessageId", "Timestamp"]
    df = test.groupby(keys)[fields].rolling('7D', closed="left", on="Timestamp").count()
    rename_dict = {item:item+"sr_pair_count_last_7d" for item in fields if item not in ["Timestamp"]}
    df = df.rename(rename_dict, axis="columns")
    test = test.merge(df, left_on=join_keys, right_on=join_keys, how="left")

    keys = ["OrderingName"]
    fields = ["NormalizedAmount", "Timestamp"]
    df = test.groupby(keys)[fields].rolling(20, min_periods=1, closed="left", on="Timestamp").mean()
    rename_dict = {item:item+"sender_avg_last_20" for item in fields if item not in ["Timestamp"]}
    df = df.rename(rename_dict, axis="columns")
    test = test.merge(df, left_on=join_keys, right_on=join_keys, how="left")

    keys = ["BeneficiaryName"]
    fields = ["NormalizedAmount", "Timestamp"]
    df = test.groupby(keys)[fields].rolling(20, min_periods=1, closed="left", on="Timestamp").mean()
    rename_dict = {item:item+"receiver_avg_last_20" for item in fields if item not in ["Timestamp"]}
    df = df.rename(rename_dict, axis="columns")
    test = test.merge(df, left_on=join_keys, right_on=join_keys, how="left")

    test.drop(columns=["day", "hour"], inplace=True)
    test = test.fillna(0)
    
    print(test.columns[test.isna().any()].tolist())

    test = test.reset_index()
    test = test.rename(columns={'index':'UETR'})
    test = actual_test[['UETR']].merge(test, left_on=["UETR"], right_on=["UETR"], how="left")

    # Exclude below categorical columns for training and testing
    columns_to_drop = [
		"UETR",
		"TransactionReference",
		"OrderingName",
		"OrderingStreet",
		"OrderingCountryCityZip",
		"BeneficiaryName",
		"BeneficiaryStreet",
		"BeneficiaryCountryCityZip",
		"SettlementDate",
		"SettlementCurrency",
		"InstructedCurrency",
		"Timestamp"
                ]

    test = test.drop(columns_to_drop, axis=1)
 
    print("test columns:", test.columns)
    test[test.select_dtypes(include=['number']).columns] = test[test.select_dtypes(include=['number']).columns].clip(-1e20, 1e20)
    print(test.columns)
    
    from sklearn.utils import resample
    DOWNSAMPLE_FACTOR = 1
    pd_test = test
    pd_test = resample(pd_test,
		       replace=False,
		       n_samples=int(len(pd_test)/DOWNSAMPLE_FACTOR)
		      )
    pd_test = pd_test.fillna(0)

    if TEST_MODE:
        pd_test.to_csv(work_dir+'test_data_processor.csv', index=False)
    else:
        columns_to_drop = ["Label"]
        pd_test[['MessageId','Label']].to_csv(work_dir+'test_label.csv', index=False)
        pd_test.drop(columns=columns_to_drop, inplace=True)
        pd_test.to_csv(work_dir+'test_data_processor.csv', index=False)


def prepare_bank_data(bank_path, work_dir):
    ### Bank Data
    data_bank = pd.read_csv(bank_path)
    data_bank.columns
    data_bank.head(1)

    BankFlagDict = {}
    for i in range(len(data_bank)):
        row = data_bank.loc[i]
        BankFlagDict[(row["Bank"], row["Account"])] = (row["Flags"]==0)

    import pickle
    with open(work_dir+"bank_flag_dict", "wb") as f:
        pickle.dump(BankFlagDict, f)



def explore_dataset(datapaths):
    [train_path, test_path] = datapaths
    train = pd.read_csv(train_path)
    test = pd.read_csv(test_path)
    print(train.columns, test.columns)
    print(train["SettlementDate"].unique(), test["SettlementDate"].unique())
    print(train["InstructedCurrency"].unique(), test["InstructedCurrency"].unique())
    print(train["SettlementCurrency"].unique(), test["SettlementCurrency"].unique())
    lst1 = (train["Sender"]+train["OrderingAccount"]).unique().tolist()
    lst2 = (test["Sender"]+test["OrderingAccount"]).unique().tolist()
    print(len(lst1), len(lst2))
    lst_diff = list(set(lst2)-set(lst1))
    print(len(lst_diff))
    lst_diff = list(set(lst1)-set(lst2))
    print(len(lst_diff))
