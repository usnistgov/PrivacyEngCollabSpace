/*
*   Copyright 2022-2023 Visa
*
*   This code is licensed under the Creative Commons
*   Attribution-NonCommercial 4.0 International Public License 
*   (https://creativecommons.org/licenses/by-nc/4.0/legalcode).
*/
#pragma once
#include "drop-ot/Defines.h"
#include <array>
#include "cryptoTools/Crypto/RandomOracle.h"

namespace dropOt {


    const u64 commStepSize(512);
    const u64 gOtExtBaseOtCount(128);

    class IknpOtExtSender
    {
    public:

        u64 mPrngIdx = 0;
        oc::MultiKeyAES<gOtExtBaseOtCount> mGens;
        BitVector mBaseChoiceBits;

        IknpOtExtSender() = default;
        IknpOtExtSender(const IknpOtExtSender&) = delete;
        IknpOtExtSender(IknpOtExtSender&&) = default;

        IknpOtExtSender(
            span<block> baseRecvOts,
            const BitVector& choices)
        {
            setUniformBaseOts(baseRecvOts, choices);
        }

        void operator=(IknpOtExtSender&& v)
        {
            mGens = std::move(v.mGens);
            mBaseChoiceBits = std::move(v.mBaseChoiceBits);
        }

        // return true if this instance has valid base OTs. 
        bool hasBaseOts() const
        {
            return mBaseChoiceBits.size() > 0;
        }

        // Returns a independent instance of this extender which can 
        // be executed concurrently. The base OTs are derived from the
        // original base OTs.
        //IknpOtExtSender split();

        // Sets the base OTs which must be peformed before calling split or send.
        // See frontend/main.cpp for an example. 
        void setUniformBaseOts(
            span<block> baseRecvOts,
            const BitVector& choices);


        // The first round of the OT-sender protocol. This will receive a 
        // message and send a message. 
        // This function can return early with a code::suspend error in which
        // case the caller should perform io and call the function again.
        // @messages, output: the random messages that will be returned.
        // @prng, input: the randomness source.
        // @chl, input: the io buffer/socket.
        void sendRoundOne_r(
            span<std::array<block, 2>> messages,
            PRNG& prng,
            span<u8>& ioBuffer);

        static constexpr auto header = "iknp-sender";
        void serialize(std::ostream& out)
        {
            out.write(header, std::strlen(header));
            bool hasBase = hasBaseOts();

            out.write((char*)&hasBase, sizeof(hasBase));
            out.write((char*)&mPrngIdx, sizeof(mPrngIdx));

            if (hasBase)
            {
                out.write((char*)mBaseChoiceBits.data(), mBaseChoiceBits.sizeBytes());

                for (u64 i = 0; i < mGens.mAESs.size(); ++i)
                {
                    auto k = mGens.mAESs[i].getKey();
                    out.write((char*)&k, sizeof(k));
                }
            }
        }

        void deserialize(std::istream& in)
        {
            std::vector<u8> buff(std::strlen(header));
            in.read((char*)buff.data(), buff.size());

            if (std::memcmp(buff.data(), header, buff.size()))
            {
                std::cout << header << " failed to deserialize. Bad header. " LOCATION << std::endl;
                throw RTE_LOC;
            }

            bool hasBase;

            in.read((char*)&hasBase, sizeof(hasBase));
            in.read((char*)&mPrngIdx, sizeof(mPrngIdx));

            if (hasBase)
            {
                mBaseChoiceBits.resize(gOtExtBaseOtCount);
                in.read((char*)mBaseChoiceBits.data(), mBaseChoiceBits.sizeBytes());

                for (u64 i = 0; i < mGens.mAESs.size(); ++i)
                {
                    block k;
                    in.read((char*)&k, sizeof(k));
                    mGens.mAESs[i].setKey(k);
                }
            }
        }

    };


    class IknpOtExtReceiver
    {
    public:


        bool mHasBase = false;
        oc::AlignedArray<oc::MultiKeyAES<gOtExtBaseOtCount>, 2> mGens;
        u64 mPrngIdx = 0;

        IknpOtExtReceiver() = default;
        IknpOtExtReceiver(const IknpOtExtReceiver&) = delete;
        IknpOtExtReceiver(IknpOtExtReceiver&&) = default;
        IknpOtExtReceiver(span<std::array<block, 2>> baseSendOts);

        void operator=(IknpOtExtReceiver&& v)
        {
            mHasBase = std::move(v.mHasBase);
            mGens = std::move(v.mGens);
            v.mHasBase = false;
        }

        // returns whether the base OTs have been set. They must be set before
        // split or receive is called.
        bool hasBaseOts() const
        {
            return mHasBase;
        }

        // sets the base OTs.
        void setUniformBaseOts(span<std::array<block, 2>> baseSendOts);

        // returns an independent instance of this extender which can securely be
        // used concurrently to this current one. The base OTs for the new instance 
        // are derived from the orginial base OTs.
        //IknpOtExtReceiver splitBase();

        // The first round of the OT-receiver protocol. This will send a message. 
        // This function can return early with a code::suspend error in which
        // case the caller should perform io and call the function again.
        // @choices, input: the choice bits that the receiver choose.
        // @messages, output: the random messages that will be returned.
        // @prng, input: the randomness source.
        // @chl, input: the io buffer/socket.
        void receiveRoundOne_s(
            const BitVector& choices,
            span<block> messages,
            PRNG& prng,
            std::vector<u8>& ioBuffer);


        static constexpr auto header = "iknp-recver";

        void serialize(std::ostream& out)
        {
            out.write(header, std::strlen(header));

            out.write((char*)&mHasBase, sizeof(mHasBase));
            out.write((char*)&mPrngIdx, sizeof(mPrngIdx));

            if (mHasBase)
            {
                for (u64 i = 0; i < mGens[0].mAESs.size(); ++i)
                {
                    auto k0 = mGens[0].mAESs[i].getKey();
                    auto k1 = mGens[1].mAESs[i].getKey();

                    out.write((char*)&k0, sizeof(k0));
                    out.write((char*)&k1, sizeof(k1));
                }
            }
        }

        void deserialize(std::istream& in)
        {
            std::vector<u8> buff(std::strlen(header));
            in.read((char*)buff.data(), buff.size());

            if (std::memcmp(buff.data(), header, buff.size()))
            {
                std::cout << header << " failed to deserialize. Bad header. " LOCATION << std::endl;
                throw RTE_LOC;
            }

            in.read((char*)&mHasBase, sizeof(mHasBase));
            in.read((char*)&mPrngIdx, sizeof(mPrngIdx));

            if (mHasBase)
            {
                for (u64 i = 0; i < mGens[0].mAESs.size(); ++i)
                {
                    block k0;
                    block k1;
                    in.read((char*)&k0, sizeof(k0));
                    in.read((char*)&k1, sizeof(k1));
                    mGens[0].mAESs[i].setKey(k0);
                    mGens[1].mAESs[i].setKey(k1);
                }
            }
        }

    };


    namespace tests
    {

        void OtExt_Iknp_Buff_test();
    }
}

