/*
*   Copyright 2022-2023 Visa
*
*   This code is licensed under the Creative Commons
*   Attribution-NonCommercial 4.0 International Public License 
*   (https://creativecommons.org/licenses/by-nc/4.0/legalcode).
*/
#pragma once
#include "Defines.h"

namespace dropOt
{
    // This is the Base OT protocl of Masny, Rindal 2019.
    // See https://eprint.iacr.org/2019/706.
    class MasnyRindal
    {
    public:

        enum State
        {
            RoundOne,
            RoundTwo
        };

        // The secret keys of each party.
        std::vector<Number> mSk;

        // receiver choice bits.
        BitVector mChoices;

        // The current state of the protocol.
        State mState = State::RoundOne;
        void resetState() { 
            mState = State::RoundOne; 
            mSk.resize(0);
            mChoices.resize(0);
        }



        static constexpr auto header = "MasnyRindal";

        void serialize(std::ostream& out)
        {
            Curve curve;

            out.write(header, std::strlen(header));
            out.write((char*)&mState, sizeof(mState));

            u64 size = mSk.size();
            out.write((char*)&size, sizeof(size));

            if (size)
            {
                std::vector<u8> buff;
                size = mSk[0].sizeBytes();

                out.write((char*)&size, sizeof(size));
                buff.resize(size);
                for (auto& sk : mSk)
                {
                    sk.toBytes(buff.data());
                    out.write((char*)buff.data(), buff.size());
                }
            }

            size = mChoices.size();
            out.write((char*)&size, sizeof(size));
            if (size)
            {
                out.write((char*)mChoices.data(), mChoices.sizeBytes());

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

            in.read((char*)&mState, sizeof(mState));

            if (mState != State::RoundOne && mState != State::RoundTwo)
            {
                std::cout << header << " failed to deserialize. Bad state. " LOCATION << std::endl;
                throw RTE_LOC;
            }

            Curve curve;
            u64 size;
            in.read((char*)&size, sizeof(size));
            mSk.resize(size);

            if (size)
            {
                u64 size2;
                in.read((char*)&size2, sizeof(size2));
                if (size2 != mSk[0].sizeBytes())
                {
                    std::cout << header << " failed to deserialize. Bad sk key size. " LOCATION << std::endl;
                    throw RTE_LOC;
                }
            }
            for (auto i = 0; i < size; ++i)
            {
                buff.resize(mSk[i].sizeBytes());
                in.read((char*)buff.data(), buff.size());
                mSk[i].fromBytes(buff.data());
            }


            in.read((char*)&size, sizeof(size));
            if (size)
            {
                mChoices.resize(size);
                in.read((char*)mChoices.data(), mChoices.sizeBytes());
            }
        }


        // Perform round 1 of the OT-receiver
        // protocol. Will return a dropOt::code
        // which encodes {success, error, ...}.
        // @choices, input: the choice bits of the messages.
        // @prng, input: the source of randomness.
        // @chl, input: the location the io should be send/recv.
        void receiveRoundOne(
            BitVector choices,
            PRNG& prng,
            std::vector<u8>& ioBuffer);

        // Perform round 2 of the OT-receiver
        // protocol. Will return a dropOt::code
        // which encodes {success, suspend, error, ...}.
        // If suspend is returned the caller should 
        // perform io and call the function again.
        // @choices, input: the choice bits of the messages.
        // @messages, output: the location that the random messages will be written to.
        // @prng, input: the source of randomness.
        // @chl, input: the location the io should be send/recv.
        void receiveRoundTwo(
            span<block> messages,
            PRNG& prng,
            span<u8>& ioBuffer);

        // Perform round 1 of the OT-sender
        // protocol. Will return a dropOt::code
        // which encodes {success, error, ...}.
        // @n, input: the number of OTs to perfom.
        // @prng, input: the source of randomness.
        // @chl, input: the location the io should be send/recv.
        void sendRoundOne(
            u64 n,
            PRNG& prng,
            std::vector<u8>& ioBuffer);


        // Perform round 2 of the OT-sender
        // protocol. Will return a dropOt::code
        // which encodes {success, suspend, error, ...}.
        // If suspend is returned the caller should 
        // perform io and call the function again.
        // @messages, output: the location that the random messages will be written to.
        // @prng, input: the source of randomness.
        // @chl, input: the location the io should be send/recv.
        void sendRoundTwo(
            span<std::array<block, 2>> messages,
            PRNG& prng,
            span<u8>& ioBuffer);
    };

    namespace tests {
        void Bot_MasnyRindal_Buff_test();
    }

}
