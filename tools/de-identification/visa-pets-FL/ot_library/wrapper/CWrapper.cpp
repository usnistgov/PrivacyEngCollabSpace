/*
*   Copyright 2022-2023 Visa
*
*   This code is licensed under the Creative Commons
*   Attribution-NonCommercial 4.0 International Public License 
*   (https://creativecommons.org/licenses/by-nc/4.0/legalcode).
*/
#include <iostream>
#include "frontend/main.cpp"
#include <vector>
#include <fcntl.h>
#include "diskhash/diskhash.hpp"


extern "C"
{

    using HTBlock = std::array<int64_t,2>;


    void decrypt(char* hashTableFilePath, char* accountIds, int* accountIdLengths, int maxAccountIdLength, int totalNumberOfAccountIds, int* encryptedZeroGradList_, int* encryptedOneGradList_, int tensorsPerAccount, int* unencryptedGradList_, int *choicesArray)
    {
        dht::DiskHash<HTBlock> ht(hashTableFilePath, maxAccountIdLength+1, dht::DHOpenRW);

        std::vector<block> buffer;

        buffer.resize( ( (tensorsPerAccount * sizeof(oc::block) ) / sizeof(int32_t) ));

        
        
        auto unencryptedGradList = span<int>(unencryptedGradList_, totalNumberOfAccountIds * tensorsPerAccount);

        auto encryptedZeroGradList = span<int>(encryptedZeroGradList_, totalNumberOfAccountIds * (tensorsPerAccount+4));
        auto encryptedOneGradList = span<int>(encryptedOneGradList_, totalNumberOfAccountIds * (tensorsPerAccount+4));

        auto unencIter = unencryptedGradList.begin();
        
        auto encZeroIter = encryptedZeroGradList.begin();
        auto encOneIter = encryptedOneGradList.begin();

        std::string subbuff;
        for (u64 i = 0; i < totalNumberOfAccountIds; ++i)
        {

            // Getting the two keys
            subbuff.clear();
            subbuff.append(accountIds, accountIdLengths[i]);
            accountIds += accountIdLengths[i];

            // std::cout << "The subbuff is " << subbuff << std::endl;

            auto ptr = ht.lookup(subbuff.c_str());
            if(ht.lookup(subbuff.c_str()) == nullptr)
            {
                std::cout << "missing key in hash table: " << subbuff << std::endl;
                throw RTE_LOC;
            }


            block tempKey;
            memcpy(&tempKey, ptr, sizeof(block));

            // Decryption Starts Here
            oc::AES aes(tempKey);

            block idx;
            memcpy(&idx, encZeroIter, sizeof(block) );

            encZeroIter = encZeroIter + 4;
            encOneIter = encOneIter + 4;

            aes.ecbEncCounterMode(idx, buffer.size(), buffer.data());

            int32_t* xorPointer = ( int32_t *) &buffer[0];

            for(int j=0; j<tensorsPerAccount; j++)
            {

                if(choicesArray[i] == 0)
                {
                    *unencIter++ = *xorPointer ^ *encZeroIter++;
                    encOneIter++;
                }
                else
                {
                    *unencIter++ = *xorPointer ^ *encOneIter++;
                    encZeroIter++;
                }                
                xorPointer++;
            }

        }


    }

    void encrypt(char* hashTableFilePath, char* accountIds, int* accountIdLengths, int maxAccountIdLength, int totalNumberOfAccountIds, int* zeroGradList_, int* oneGradList_, int tensorsPerAccount, int* encryptedZeroGradList_, int* encryptedOneGradList_)
    {
        // std::cout << "In encrypt function for " << hashTableFilePath << std::endl;
        dht::DiskHash<std::array<HTBlock,2>> ht(hashTableFilePath, maxAccountIdLength+1, dht::DHOpenRW);

        
        std::vector<block> bufferZeroGrad, bufferOneGrad;

        bufferZeroGrad.resize( ( (tensorsPerAccount * sizeof(oc::block) ) / sizeof(int32_t) ));
        bufferOneGrad.resize( ( (tensorsPerAccount * sizeof(oc::block) ) / sizeof(int32_t) ));

        auto zeroGradList = span<int>(zeroGradList_, totalNumberOfAccountIds * tensorsPerAccount);
        auto oneGradList = span<int>(oneGradList_, totalNumberOfAccountIds * tensorsPerAccount);

        auto encryptedZeroGradList = span<int>(encryptedZeroGradList_, totalNumberOfAccountIds * (tensorsPerAccount+4));
        auto encryptedOneGradList = span<int>(encryptedOneGradList_, totalNumberOfAccountIds * (tensorsPerAccount+4));

        auto zeroIter = zeroGradList.begin();
        auto oneIter = oneGradList.begin();
        
        auto encZeroIter = encryptedZeroGradList.begin();
        auto encOneIter = encryptedOneGradList.begin();

        std::string subbuff;


        for (u64 i = 0; i < totalNumberOfAccountIds; ++i)
        {

            // Getting the two keys
            subbuff.clear();
            subbuff.append(accountIds, accountIdLengths[i]);
            accountIds += accountIdLengths[i];

            std::array<block, 2> tempKeys;

            auto ptr = *ht.lookup(subbuff.c_str());
            if(ht.lookup(subbuff.c_str()) == nullptr)
            {
                std::cout << "missing key in hash table: " << subbuff << std::endl;
                throw RTE_LOC;
            }


            tempKeys[0] = ptr[0];
            tempKeys[1] = ptr[1];

            // Encryption starts here
            oc::AES aesZeroGrad(tempKeys[0]);
            oc::AES aesOneGrad(tempKeys[1]);

            PRNG prng(oc::sysRandomSeed());
            block idx = prng.get();

            aesZeroGrad.ecbEncCounterMode(idx, bufferZeroGrad.size(), bufferZeroGrad.data());
            aesOneGrad.ecbEncCounterMode(idx, bufferOneGrad.size(), bufferOneGrad.data());

            int32_t* xorZeroPointer = ( int32_t *) &bufferZeroGrad[0];
            int32_t* xorOnePointer = ( int32_t *) &bufferOneGrad[0];

            // Pushing the counter mode index
            *encZeroIter++ = idx.get<int32_t>(0);
            *encOneIter++ = idx.get<int32_t>(0);

            *encZeroIter++ = idx.get<int32_t>(1);
            *encOneIter++ = idx.get<int32_t>(1);

            *encZeroIter++ = idx.get<int32_t>(2);
            *encOneIter++ = idx.get<int32_t>(2);

            *encZeroIter++ = idx.get<int32_t>(3);
            *encOneIter++ = idx.get<int32_t>(3);



            for(int j=0; j<tensorsPerAccount; j++)
            {
            
                // std::cout << currentEncryptedTensorLocation << " 0 > " << x << " + " << v << " -> ";
                // Encrypting Zero Gradient
                *encZeroIter++ = *xorZeroPointer ^ *zeroIter++;
                xorZeroPointer++;


                // Encrypting One Gradient
                *encOneIter++ = *xorOnePointer ^ *oneIter++;
                xorOnePointer++;                

            }
            
        }
    }

    void deleteState( long long state)
    {
        auto pointer = (std::vector<u8>*) state;
        delete pointer;
    }
    
    unsigned char* senderSetup1(char* stateDirPointer, char* bankIDPointer, int* returnedPointerSize, long long* state )
    {
        Ot ot;
        
        std::string stateDir(stateDirPointer);
        std::string bankID(bankIDPointer);
    
        std::vector<u8>* returnvalue = new std::vector<u8>{ ot.sender_Setup1(stateDir,bankID ) } ;
        // std::cout << "senderSetup1 called completed" << " BankID " << bankID << "\n";

        *returnedPointerSize = returnvalue->size();


        oc::RandomOracle hash(16);
        hash.Update(returnvalue->data(), returnvalue->size());
        oc::block h; 
        hash.Final(h);
			
			
        // std::cout << "In Sender Setup 1 Byte Hash is  " << " " << h << " BankID " << bankID << "\n";
        
        *state = (long long)returnvalue;

        return returnvalue->data();

    }


    unsigned char* recverSetup(char* stateDirPointer, char* bankIDPointer, char* senderSetup1ReturnValue, int senderSetup1ReturnSize, int* returnedPointerSize, long long* state)
    {
        Ot ot;

        std::string stateDir(stateDirPointer);
        std::string bankID(bankIDPointer);

        span<u8> input{(u8*)senderSetup1ReturnValue, size_t(senderSetup1ReturnSize) };

        oc::RandomOracle hash(16);
        hash.Update(senderSetup1ReturnValue, size_t(senderSetup1ReturnSize));
        oc::block h; 
        hash.Final(h);

        // std::cout << "In Receiver Setup 1 Byte Hash is  " << " " << h << " BankID " << bankID << "\n";

        std::vector<u8>* returnvalue = new std::vector<u8>{ ot.recver_Setup(stateDir, bankID, input ) } ;        
        // std::cout << "recverSetup called completed" << " BankID " << bankID << "\n";


        *returnedPointerSize = returnvalue->size();
        *state = (long long)returnvalue;


        oc::RandomOracle hash1(16);
        hash1.Update(returnvalue->data(), returnvalue->size());
        oc::block h1; 
        hash1.Final(h1);

        // std::cout << "In Receiver Setup 1 Byte Hash is  " << " " << h1 << " BankID " << bankID << "\n";
        
        return returnvalue->data();
    }

    void senderSetup2(char* stateDirPointer, char* bankIDPointer, u8* recverSetupReturnValue, int recverSetupReturnSize)
    {
        Ot ot;
        std::string stateDir(stateDirPointer);
        std::string bankID(bankIDPointer);

        // std::cout << "recverSetupReturnSize is " <<  recverSetupReturnSize << std::endl;
        oc::RandomOracle hash(16);
        hash.Update(recverSetupReturnValue, size_t(recverSetupReturnSize));
        oc::block h; 
        hash.Final(h);

        // std::cout << "In Sender Setup2 Byte Hash is  " << " " << h << " BankID " << bankID << "\n";

        span<u8> input{recverSetupReturnValue, size_t(recverSetupReturnSize) };

        ot.sender_Setup2(stateDir, bankID, input );
        // std::cout << "senderSetup2 called completed" << " BankID " << bankID << "\n";

    }

    
    unsigned char* recverGenerateKeys(char* stateDirPointer, char* bankIDPointer, char* hashTableFilePath,int *choicesArray, int choiceslength ,int* returnedPointerSize, long long* state, char* accountIds, int* accountIdLengths, int maxAccountIdLength)
    {

        Ot ot;
        std::string stateDir(stateDirPointer);
        std::string bankID(bankIDPointer);

        // std::cout << "In Receiver Key Gen for BankID = " << bankID << std::endl;

        // output keys
        std::vector<block> recverKeys(choiceslength);

        // Construct a zero initialized BitVector of size choiceslength
        oc::BitVector choices(choiceslength);

        // std::cout << "Choices length is" << choiceslength << std::endl;

        for (u64 i=0; i < choiceslength; i++) 
        {
            
            if(choicesArray[i] == 1)
                choices[i] = 1;
            // std::cout << choices[i] << " " << std::endl;
        }

        // std::cout << "Choices BitVector is initiazed" << std::endl;

        std::vector<u8>* returnvalue = new std::vector<u8>{ ot.recver_generateKeys(stateDir, bankID, recverKeys, choices) } ;        
        // std::cout << "Receiver Keys Generator completed" << std::endl;


        *returnedPointerSize = returnvalue->size();
        *state = (long long)returnvalue;


        oc::RandomOracle hash1(16);
        hash1.Update(returnvalue->data(), returnvalue->size());
        oc::block h1; 
        hash1.Final(h1);

        dht::DiskHash<HTBlock> ht(hashTableFilePath, maxAccountIdLength+1, dht::DHOpenRW);

        std::string subbuff;
        // subbuff.reserve(maxAccountIdLength);
        for (u64 i = 0; i < choiceslength; ++i)
        {
            subbuff.clear();
            subbuff.append(accountIds, accountIdLengths[i]);
            accountIds += accountIdLengths[i];

            // MyFile << "recver{" << recverKeys[i] << ", " << choices[i] << "} " << subbuff << std::endl;
            
            const bool isInserted = ht.insert(subbuff.c_str(), recverKeys[i].get<int64_t>());
            if(isInserted == 0)
            {
                std::cout << " subbuff is not inserted " << subbuff <<std::endl;
                throw RTE_LOC;
            }
        }
        // std::cout << "After all insertion " << something << ", " << " BankID" << bankID << " subbuff is " << tempsubbuff<<std::endl;

        return returnvalue->data();
    }
    
    void senderGenerateKeys(char* stateDirPointer, char* bankIDPointer, char* hashTableFilePath, u8* recverGenKeyBytes, int recverGenKeySize, int choiceslength, char* accountIds, int* accountIdLengths, int maxAccountIdLength)
    {

        Ot ot;
        std::string stateDir(stateDirPointer);
        std::string bankID(bankIDPointer);

        // std::cout << "recverGenKeySize is " <<  recverGenKeySize << " BankID " << bankID << "\n";
        oc::RandomOracle hash(16);
        hash.Update(recverGenKeyBytes, size_t(recverGenKeySize));
        oc::block h; 
        hash.Final(h);
        // std::cout << "In Sender Key Gen Byte Hash is  " << " " << h << " BankID " << bankID << "\n";


        span<u8> input{recverGenKeyBytes, size_t(recverGenKeySize) };


        std::vector<std::array<block, 2>> senderKeys(choiceslength);
        dht::DiskHash<std::array<HTBlock,2>> ht(hashTableFilePath, maxAccountIdLength+1, dht::DHOpenRW);

        ot.sender_generateKeys(stateDir, bankID, input, senderKeys);

        std::string subbuff;
        for (u64 i = 0; i < choiceslength; ++i)
        {
            subbuff.clear();
            subbuff.append(accountIds, accountIdLengths[i]);
            accountIds += accountIdLengths[i];

            std::array<HTBlock,2> tempBlock {
                senderKeys[i][0].get<int64_t>(), 
                senderKeys[i][1].get<int64_t>()
                };

            ht.insert(subbuff.c_str(),tempBlock);
            
        }

    }

}