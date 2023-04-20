#include "IknpOtExt.h"

#include <cryptoTools/Common/Timer.h>
#include <cryptoTools/Crypto/RandomOracle.h>


#include "cryptoTools/Network/IOService.h"
#include "cryptoTools/Network/Session.h"
#include "cryptoTools/Common/TestCollection.h"
#include "Tools.h"
#include <thread>
#include <sstream>

#define OTE_RANDOM_ORACLE 1
#define OTE_DAVIE_MEYER_AES 2
#define OTE_KOS_HASH OTE_DAVIE_MEYER_AES 

namespace dropOt
{


    void IknpOtExtSender::setUniformBaseOts(span<block> baseRecvOts, const BitVector & choices)
    {
        mPrngIdx = 0;
        mBaseChoiceBits = choices;
        mGens.setKeys(baseRecvOts);
    }

    void IknpOtExtSender::sendRoundOne_r(
        span<std::array<block, 2>> messages,
        PRNG& prng,
        span<u8>& buffer)
    {

        if (hasBaseOts() == false)
            panic("IknpOtExtSender has no base OTs");

        auto numOtExt = u64{};
        auto numBlocks = u64{};
        auto step = u64{};
        auto blkIdx = u64{};
        auto t = oc::AlignedUnVector<block>{ 128 };
        auto u = oc::AlignedUnVector<block>(128 * commStepSize);
        auto choiceMask = oc::AlignedArray<block, 128>{};
        auto delta = block{};
        auto recvView = span<u8>{};
        auto mIter = span<std::array<block, 2>>::iterator{};
        auto uIter = (block*)nullptr;
        auto tIter = (block*)nullptr;
        auto cIter = (block*)nullptr;
        auto uEnd = (block*)nullptr;

        // round up 
        numOtExt = roundUpTo(messages.size(), 128);
        numBlocks = (numOtExt / 128);
        //u64 numBlocks = numBlocks * superBlkSize;


        delta = *(block*)mBaseChoiceBits.data();

        for (u64 i = 0; i < 128; ++i)
        {
            if (mBaseChoiceBits[i]) choiceMask[i] = oc::AllOneBlock;
            else choiceMask[i] = oc::ZeroBlock;
        }

        mIter = messages.begin();
        uEnd = u.data() + u.size();
        uIter = uEnd;

        for (blkIdx = 0; blkIdx < numBlocks; ++blkIdx)
        {
            tIter = (block*)t.data();
            cIter = choiceMask.data();

            if (uIter == uEnd)
            {
                step = std::min<u64>(numBlocks - blkIdx, (u64)commStepSize);
                step *= 128 * sizeof(block);
                recvView = span<u8>((u8*)u.data(), step);
                uIter = u.data();

                std::copy(buffer.begin(), buffer.begin() + recvView.size(), recvView.begin());
                buffer = buffer.subspan(recvView.size());
            }

            mGens.ecbEncCounterMode(mPrngIdx, tIter);
            ++mPrngIdx;

            // transpose 128 columns at at time. Each column will be 128 * superBlkSize = 1024 bits long.
            for (u64 colIdx = 0; colIdx < 128 / 8; ++colIdx)
            {
                uIter[0] = uIter[0] & cIter[0];
                uIter[1] = uIter[1] & cIter[1];
                uIter[2] = uIter[2] & cIter[2];
                uIter[3] = uIter[3] & cIter[3];
                uIter[4] = uIter[4] & cIter[4];
                uIter[5] = uIter[5] & cIter[5];
                uIter[6] = uIter[6] & cIter[6];
                uIter[7] = uIter[7] & cIter[7];

                tIter[0] = tIter[0] ^ uIter[0];
                tIter[1] = tIter[1] ^ uIter[1];
                tIter[2] = tIter[2] ^ uIter[2];
                tIter[3] = tIter[3] ^ uIter[3];
                tIter[4] = tIter[4] ^ uIter[4];
                tIter[5] = tIter[5] ^ uIter[5];
                tIter[6] = tIter[6] ^ uIter[6];
                tIter[7] = tIter[7] ^ uIter[7];

                cIter += 8;
                uIter += 8;
                tIter += 8;
            }

            // transpose our 128 columns of 1024 bits. We will have 1024 rows,
            // each 128 bits wide.
            transpose128(t.data());


            auto mEnd = mIter + std::min<u64>(128, messages.end() - mIter);

            tIter = t.data();
            if (mEnd - mIter == 128)
            {
                for (u64 i = 0; i < 128; i += 8)
                {
                    mIter[i + 0][0] = tIter[i + 0];
                    mIter[i + 1][0] = tIter[i + 1];
                    mIter[i + 2][0] = tIter[i + 2];
                    mIter[i + 3][0] = tIter[i + 3];
                    mIter[i + 4][0] = tIter[i + 4];
                    mIter[i + 5][0] = tIter[i + 5];
                    mIter[i + 6][0] = tIter[i + 6];
                    mIter[i + 7][0] = tIter[i + 7];
                    mIter[i + 0][1] = tIter[i + 0] ^ delta;
                    mIter[i + 1][1] = tIter[i + 1] ^ delta;
                    mIter[i + 2][1] = tIter[i + 2] ^ delta;
                    mIter[i + 3][1] = tIter[i + 3] ^ delta;
                    mIter[i + 4][1] = tIter[i + 4] ^ delta;
                    mIter[i + 5][1] = tIter[i + 5] ^ delta;
                    mIter[i + 6][1] = tIter[i + 6] ^ delta;
                    mIter[i + 7][1] = tIter[i + 7] ^ delta;

                }

                mIter += 128;

            }
            else
            {
                while (mIter != mEnd)
                {
                    (*mIter)[0] = *tIter;
                    (*mIter)[1] = *tIter ^ delta;

                    tIter += 1;
                    mIter += 1;
                }
            }
        }


        {

#ifdef IKNP_SHA_HASH
            RandomOracle sha;
            u8 hashBuff[20];
            u64 doneIdx = 0;


            u64 bb = (messages.size() + 127) / 128;
            for (u64 blockIdx = 0; blockIdx < bb; ++blockIdx)
            {
                u64 stop = std::min<u64>(messages.size(), doneIdx + 128);

                for (u64 i = 0; doneIdx < stop; ++doneIdx, ++i)
                {
                    // hash the message without delta
                    sha.Reset();
                    sha.Update((u8*)&messages[doneIdx][0], sizeof(block));
                    sha.Final(hashBuff);
                    messages[doneIdx][0] = *(block*)hashBuff;

                    // hash the message with delta
                    sha.Reset();
                    sha.Update((u8*)&messages[doneIdx][1], sizeof(block));
                    sha.Final(hashBuff);
                    messages[doneIdx][1] = *(block*)hashBuff;
                }
            }
#else

            oc::mAesFixedKey.hashBlocks((block*)messages.data(), messages.size() * 2, (block*)messages.data());
        }
#endif
    }

    IknpOtExtReceiver::IknpOtExtReceiver(span<std::array<block, 2>> baseOTs)
    {
        setUniformBaseOts(baseOTs);
    }

    void IknpOtExtReceiver::setUniformBaseOts(span<std::array<block, 2>> baseOTs)
    {
        mPrngIdx = 0;
        for (u64 j = 0; j < 2; ++j)
        {
            block buff[gOtExtBaseOtCount];
            for (u64 i = 0; i < gOtExtBaseOtCount; i++)
                buff[i] = baseOTs[i][j];

            mGens[j].setKeys(buff);
        }

        mHasBase = true;
    }

    void IknpOtExtReceiver::receiveRoundOne_s(
        const BitVector& choices,
        span<block> messages,
        PRNG& prng,
        std::vector<u8>& buffer)
    {
        if (hasBaseOts() == false)
            panic("base OTs for receiver not set");

        if (choices.size() != messages.size())
            throw RTE_LOC;

        auto numOtExt = u64{};
        auto numBlocks = u64{};
        auto blkIdx = u64{};
        auto step = u64{};
        auto choiceBlocks = span<block>{};
        auto t0 = oc::AlignedUnVector<block>{ 128 };
        auto mIter = span<block>::iterator{};
        auto uIter = (block*)nullptr;
        auto tIter = (block*)nullptr;
        auto cIter = (block*)nullptr;
        auto uEnd = (block*)nullptr;
        auto uBuff = oc::AlignedUnVector<block>{};

        // we are going to process OTs in blocks of 128 * superBlkSize messages.
        numOtExt = roundUpTo(choices.size(), 128);
        numBlocks = (numOtExt / 128);

        choiceBlocks = { choices.blocks(), choices.sizeBlocks() };

        // the index of the OT that has been completed.
        //u64 doneIdx = 0;

        mIter = messages.begin();

        step = std::min<u64>(numBlocks, (u64)commStepSize);
        uBuff.resize(step * 128);

        // get an array of blocks that we will fill. 
        uIter = (block*)uBuff.data();
        uEnd = uIter + uBuff.size();

        // NOTE: We do not transpose a bit-matrix of size numCol * numCol.
        //   Instead we break it down into smaller chunks. We do 128 columns 
        //   times 8 * 128 rows at a time, where 8 = superBlkSize. This is done for  
        //   performance reasons. The reason for 8 is that most CPUs have 8 AES vector  
        //   lanes, and so its more efficient to encrypt (aka prng) 8 blocks at a time.
        //   So that's what we do. 
        for (blkIdx = 0; blkIdx < numBlocks; ++blkIdx)
        {

            // this will store the next 128 rows of the matrix u

            tIter = (block*)t0.data();
            cIter = choiceBlocks.data() + blkIdx;

            mGens[0].ecbEncCounterMode(mPrngIdx, tIter);
            mGens[1].ecbEncCounterMode(mPrngIdx, uIter);
            ++mPrngIdx;

            for (u64 colIdx = 0; colIdx < 128 / 8; ++colIdx)
            {
                uIter[0] = uIter[0] ^ cIter[0];
                uIter[1] = uIter[1] ^ cIter[0];
                uIter[2] = uIter[2] ^ cIter[0];
                uIter[3] = uIter[3] ^ cIter[0];
                uIter[4] = uIter[4] ^ cIter[0];
                uIter[5] = uIter[5] ^ cIter[0];
                uIter[6] = uIter[6] ^ cIter[0];
                uIter[7] = uIter[7] ^ cIter[0];

                uIter[0] = uIter[0] ^ tIter[0];
                uIter[1] = uIter[1] ^ tIter[1];
                uIter[2] = uIter[2] ^ tIter[2];
                uIter[3] = uIter[3] ^ tIter[3];
                uIter[4] = uIter[4] ^ tIter[4];
                uIter[5] = uIter[5] ^ tIter[5];
                uIter[6] = uIter[6] ^ tIter[6];
                uIter[7] = uIter[7] ^ tIter[7];

                uIter += 8;
                tIter += 8;
            }

            if (uIter == uEnd)
            {
                // send over u buffer
                auto begin = buffer.size();
                buffer.resize(begin + uBuff.size() * sizeof(block));
                std::copy((u8*)uBuff.data(), (u8*)(uBuff.data() + uBuff.size()), buffer.begin() + begin);

                u64 step = std::min<u64>(numBlocks - blkIdx - 1, (u64)commStepSize);

                if (step)
                {
                    uBuff.resize(step * 128);
                    uIter = (block*)uBuff.data();
                    uEnd = uIter + uBuff.size();
                }
            }

            // transpose our 128 columns of 1024 bits. We will have 1024 rows, 
            // each 128 bits wide.
            transpose128(t0.data());


            auto mEnd = mIter + std::min<u64>(128, messages.end() - mIter);


            tIter = t0.data();

            memcpy(mIter, tIter, (mEnd - mIter) * sizeof(block));
            mIter = mEnd;

#ifdef IKNP_DEBUG
            ... fix this
                u64 doneIdx = mStart - messages.data();
            block* msgIter = messages.data() + doneIdx;
            chl.send(msgIter, sizeof(block) * 128 * superBlkSize);
            cIter = choiceBlocks.data() + superBlkSize * blkIdx;
            chl.send(cIter, sizeof(block) * superBlkSize);
#endif
            //doneIdx = stopIdx;
        }

        {

#ifdef IKNP_SHA_HASH
            RandomOracle sha;
            u8 hashBuff[20];
            u64 doneIdx = (0);

            u64 bb = (messages.size() + 127) / 128;
            for (u64 blockIdx = 0; blockIdx < bb; ++blockIdx)
            {
                u64 stop = std::min<u64>(messages.size(), doneIdx + 128);

                for (u64 i = 0; doneIdx < stop; ++doneIdx, ++i)
                {
                    // hash it
                    sha.Reset();
                    sha.Update((u8*)&messages[doneIdx], sizeof(block));
                    sha.Final(hashBuff);
                    messages[doneIdx] = *(block*)hashBuff;
                }
            }
#else
            oc::mAesFixedKey.hashBlocks(messages.data(), messages.size(), messages.data());
#endif

        }
    }




    namespace tests
    {


        void OtExt_Iknp_Buff_test()
        {
            PRNG prng0(toBlock(4253465, 3434565));
            PRNG prng1(toBlock(233465, 334565));

            u64 numOTs = 1<<17;

            std::vector<block> recvMsg(numOTs), baseRecv(128);
            std::vector<std::array<block, 2>> sendMsg(numOTs), baseSend(128);
            BitVector choices(numOTs), baseChoice(128);
            choices.randomize(prng0);
            baseChoice.randomize(prng0);

            for (u64 i = 0; i < 128; ++i)
            {
                baseSend[i][0] = prng0.get<block>();
                baseSend[i][1] = prng0.get<block>();
                baseRecv[i] = baseSend[i][baseChoice[i]];
            }

            IknpOtExtSender sender;
            IknpOtExtReceiver recv;
            recv.setUniformBaseOts(baseSend);
            sender.setUniformBaseOts(baseRecv, baseChoice);

            recv.mPrngIdx = 42;
            sender.mPrngIdx = 42;

            std::stringstream rss, sss;
            recv.serialize(rss);
            recv = {};
            recv.deserialize(rss);
            if (recv.mPrngIdx != 42)
                throw RTE_LOC;


            sender.serialize(rss);
            sender = {};
            sender.deserialize(rss);
            if (sender.mPrngIdx != 42)
                throw RTE_LOC;

            std::vector<u8> buffer;
            recv.receiveRoundOne_s(choices, recvMsg, prng0, buffer);
                
            span<u8> bSpan = buffer;
            sender.sendRoundOne_r(sendMsg, prng1, bSpan);

            for (u64 i = 0; i < choices.size(); ++i)
            {
                u8 choice = choices[i];
                const block& revcBlock = recvMsg[i];
                const block& senderBlock = sendMsg[i][choice];

                if (neq(revcBlock, senderBlock))
                    throw oc::UnitTestFail();

                if (eq(revcBlock, sendMsg[i][1 ^ choice]))
                    throw oc::UnitTestFail();
            }
        }
    }
}

