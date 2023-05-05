/*
*   Copyright 2022-2023 Visa
*
*   This code is licensed under the Creative Commons
*   Attribution-NonCommercial 4.0 International Public License 
*   (https://creativecommons.org/licenses/by-nc/4.0/legalcode).
*/
import ctypes as ct
from pathlib import Path
import sys
import torch

clib_path = Path(sys.modules[__name__].__file__).parent.joinpath("libwrapper.so")
clib = ct.CDLL(str(clib_path))

def senderSetup1(stateDir, bankID):
    #return 0, 0
    clib.senderSetup1.argtypes = [ct.c_char_p, ct.c_char_p, ct.POINTER(ct.c_int), ct.POINTER(ct.c_longlong)]
    #clib.senderSetup1.restype  = ct.c_char_p
    clib.senderSetup1.restype = ct.POINTER(ct.c_char)
    senderSetup1ByteSize = ct.c_int()
    senderSetup1State = ct.c_longlong()

    senderSetup1Bytes = clib.senderSetup1(stateDir.encode('utf-8'), bankID.encode('utf-8'), ct.byref(senderSetup1ByteSize), ct.byref(senderSetup1State))

    # ct.cast(senderSetup1ReturnValue , ct.)
    # uchar_p = ct.cast(senderSetup1ReturnValue, ct.POINTER(ct.c_ubyte))
    #print(ct.string_at(senderSetup1ReturnValue, senderSetup1ReturnSize.value) , end='')
    # print(bytes(uchar_p[:size]), end='')

    print(senderSetup1ByteSize.value)
    p = ct.string_at(senderSetup1Bytes, senderSetup1ByteSize.value)
    clib.deleteState(senderSetup1State)
    return p, senderSetup1ByteSize.value

def receiverSetup(stateDir, bankID, p, p_size):
    #return 0, 0
    b_stateDir = stateDir.encode('utf-8')
    b_bankID = bankID.encode('utf-8')
    #### Receiver Setup1 starts here
    clib.recverSetup.argtypes = [ct.c_char_p, ct.c_char_p, ct.POINTER(ct.c_char), ct.c_int, ct.POINTER(ct.c_int), ct.POINTER(ct.c_longlong)]
    clib.recverSetup.restype  = ct.POINTER(ct.c_char)

    recverSetupBytesSize = ct.c_int()
    recverSetupState = ct.c_longlong()

    recverSetupBytes = clib.recverSetup(b_stateDir, b_bankID, p, p_size, ct.byref(recverSetupBytesSize), ct.byref(recverSetupState) )
    print(recverSetupBytesSize.value)
    q = ct.string_at(recverSetupBytes, recverSetupBytesSize.value)
    clib.deleteState(recverSetupState)
    return q, recverSetupBytesSize.value

def senderSetup2(stateDir, bankID, q, q_size):
    #return 0, 0
    b_stateDir = stateDir.encode('utf-8')
    b_bankID = bankID.encode('utf-8')
    #### Sender Setup2 starts here

    clib.senderSetup2.argtypes = [ct.c_char_p, ct.c_char_p, ct.POINTER(ct.c_char), ct.c_int]
    clib.senderSetup2( b_stateDir, b_bankID, q, q_size)
    return

def receiverGenKeys(stateDir, bankID, choices, accountIds, max_length):
    #d = dict(zip(accountIds, choices))
    #torch.save(d, stateDir+"ot.pl")
    #return 0, 0

    b_stateDir = stateDir.encode('utf-8')
    b_bankID = bankID.encode('utf-8')
    b_bankHashTableFilePath = (stateDir + "/" + bankID).encode('utf-8')
    #### Receiver passing the choices & generating the keys
    clib.recverGenerateKeys.argtypes = [ct.c_char_p, ct.c_char_p,ct.c_char_p, ct.POINTER(ct.c_uint), ct.c_int, ct.POINTER(ct.c_int), ct.POINTER(ct.c_longlong), ct.c_char_p, ct.POINTER(ct.c_int), ct.c_int]
    clib.recverGenerateKeys.restype = ct.POINTER(ct.c_char)

    
    cChoices = (ct.c_uint * len(choices)) (*choices)
    accountIdLengths = [len(accountId) for accountId in accountIds]
    assert(max(accountIdLengths) <= max_length)
    cAccountIdLengths = (ct.c_int * len(accountIdLengths)) (*accountIdLengths)
    b_accountIds = "".join(accountIds).encode('utf-8')

    recverGenKeySize = ct.c_int()
    recverGenKeyState = ct.c_longlong()

    cAccountIdLengths = (ct.c_int * len(accountIdLengths)) (*accountIdLengths)
    recverGenKeyBytes = clib.recverGenerateKeys(b_stateDir, b_bankID, b_bankHashTableFilePath, cChoices, len(choices), ct.byref(recverGenKeySize), ct.byref(recverGenKeyState), b_accountIds, cAccountIdLengths , max_length)
    r = ct.string_at(recverGenKeyBytes, recverGenKeySize.value)
    clib.deleteState(recverGenKeyState)
    return r, recverGenKeySize.value

def senderGenKeys(stateDir, bankID, accountIds, r, r_size, max_length):
    #return 
    b_stateDir = stateDir.encode('utf-8')
    b_bankID = bankID.encode('utf-8')
    b_hashTableFilePath = (stateDir+ "/PROCESSOR" + bankID).encode('utf-8')

    accountIdLengths = [len(accountId) for accountId in accountIds]
    cAccountIdLengths = (ct.c_int * len(accountIdLengths)) (*accountIdLengths)
    b_accountIds = "".join(accountIds).encode('utf-8')

    clib.senderGenerateKeys.argtypes = [ct.c_char_p, ct.c_char_p, ct.c_char_p, ct.POINTER(ct.c_char), ct.c_int, ct.c_int, ct.c_char_p, ct.POINTER(ct.c_int), ct.c_int]
    clib.senderGenerateKeys( b_stateDir, b_bankID, b_hashTableFilePath, r, r_size, len(accountIds), b_accountIds, cAccountIdLengths, max_length)
    return

def senderEncrypt(accountIds, g0, g1, stateDir: str, partitionID, gradient_length, max_length):
    #return g0, g1

    b_hashTableFilePath = (stateDir + "/PROCESSOR" + partitionID).encode('utf-8')
    assert(g0.shape == g1.shape)
    samples, grad_len = g0.shape
    assert(grad_len == gradient_length)
    assert(samples == len(accountIds))

    encryptedZeroGradient = torch.zeros( len(accountIds) * (gradient_length+4))
    encryptedOneGradient = torch.zeros( len(accountIds) * (gradient_length+4))
    g0 = torch.flatten(g0)
    g1  = torch.flatten(g1)
    print(g0.shape)

    g0.to(torch.int32)
    g1.to(torch.int32)
    encryptedZeroGradient = encryptedZeroGradient.to(torch.int32)
    encryptedOneGradient = encryptedOneGradient.to(torch.int32)

    accountIds = [accountId[0] + accountId[1] for accountId in accountIds]
    accountIdLengths = [len(accountId) for accountId in accountIds]
    b_accountIds = "".join(accountIds).encode('utf-8')
    cAccountIdLengths = (ct.c_int * len(accountIdLengths)) (*accountIdLengths)



    clib.encrypt.argtypes = [ct.c_char_p, ct.c_char_p, ct.POINTER(ct.c_int), ct.c_int, ct.c_int, ct.c_longlong, ct.c_longlong, ct.c_int, ct.c_longlong, ct.c_longlong]
    clib.encrypt(b_hashTableFilePath, b_accountIds, cAccountIdLengths, max_length, len(accountIds), g0.data_ptr(), g1.data_ptr(), gradient_length, encryptedZeroGradient.data_ptr(), encryptedOneGradient.data_ptr())
    shape = (len(accountIds), gradient_length+4)
    return torch.reshape(encryptedZeroGradient, shape), torch.reshape(encryptedOneGradient, shape)

def receiverDecrypt(accountIds, enc0, enc1, stateDir: str, partitionID, gradient_length, choices, max_length):
    #accountIds = [accountId[0] + accountId[1] for accountId in accountIds]
    #d = torch.load(stateDir+"ot.pl")
    #unencryptedGradient = [enc0[i] if d[accountIds[i]] == 0 else enc1[i] for i in range(len(accountIds))]
    #unencryptedGradient = torch.stack(unencryptedGradient, axis=0)
    #return unencryptedGradient


    b_bankHashTableFilePath = (stateDir + "/" + partitionID).encode('utf-8')
    
    accountIds = [accountId[0] + accountId[1] for accountId in accountIds]
    accountIdLengths = [len(accountId) for accountId in accountIds]
    b_accountIds = "".join(accountIds).encode('utf-8')
    cAccountIdLengths = (ct.c_int * len(accountIdLengths)) (*accountIdLengths)
    cChoices = (ct.c_uint * len(choices)) (*choices)
    unencryptedGradient = torch.zeros( len(accountIds) * gradient_length)
    unencryptedGradient = unencryptedGradient.to(torch.int32)
    enc0 = torch.flatten(enc0)
    enc1 = torch.flatten(enc1)

    clib.decrypt.argtypes = [ct.c_char_p, ct.c_char_p, ct.POINTER(ct.c_int), ct.c_int, ct.c_int, ct.c_longlong, ct.c_longlong, ct.c_int, ct.c_longlong,  ct.POINTER(ct.c_uint)]
    clib.decrypt(b_bankHashTableFilePath, b_accountIds, cAccountIdLengths, max_length, len(accountIds), enc0.data_ptr(), enc1.data_ptr(), gradient_length, unencryptedGradient.data_ptr(), cChoices )
    
    unencryptedGradient = torch.reshape(unencryptedGradient, (len(accountIds), gradient_length))
    return unencryptedGradient
