#include "MasnyRindal.h"


#include <cryptoTools/Common/BitVector.h>
#include <cryptoTools/Common/Log.h>
#include <cryptoTools/Crypto/RandomOracle.h>
#include <cryptoTools/Crypto/RCurve.h>

#include "cryptoTools/Network/IOService.h"
#include "cryptoTools/Network/Session.h"
#include "cryptoTools/Common/TestCollection.h"

#include <thread>
#include <sstream>

namespace dropOt
{

    void MasnyRindal::receiveRoundOne(
        BitVector choices_,
        PRNG& prng,
        std::vector<u8>& ioBuffer)
    {
        if (mState != State::RoundOne)
            panic("bad state, " LOCATION);


        mChoices = std::move(choices_);

        auto n = mChoices.size();
        Curve curve;
        std::array<Point, 2> r;
        auto pointSize = Point::size;

        Point hPoint;
        std::vector<u8> hashBuff(roundUpTo(pointSize, 16));
        mSk = {};
        mSk.reserve(n);

        auto begin = ioBuffer.size();
        ioBuffer.resize(begin + Point::size * 2 * n);
        span<u8> buff = { ioBuffer.begin() + begin, ioBuffer.end() };
        // loop over the input and generate the private 
        // keys.
        for (u64 i = 0; i < n; ++i)
        {
            // We process things in batches of max size step. We 
            // then send those off before the next step is started.
            auto& rrNot = r[mChoices[i] ^ 1];
            auto& rr = r[mChoices[i]];

            rrNot.randomize(prng);
            rrNot.toBytes(hashBuff.data());
            hPoint.fromHash(hashBuff.data(), pointSize);

            mSk.emplace_back(prng);
            rr = Point::mulGenerator(mSk[i]);
            rr -= hPoint;

            r[0].toBytes(buff.subspan(0, Point::size).data()); buff = buff.subspan(Point::size);
            r[1].toBytes(buff.subspan(0, Point::size).data()); buff = buff.subspan(Point::size);
        }

        // progress to the next round.
        mState = State::RoundTwo;
    }

    void MasnyRindal::receiveRoundTwo(
        span<block> messages,
        PRNG& prng,
        span<u8>& recvBuff)
    {
        if (mState != State::RoundTwo)
            panic("bad state, " LOCATION);

        Curve curve;
        Point Mb, k;
        auto n = mChoices.size();
        auto pointSize = Point::size;

        if (recvBuff.size() != Point::size)
            throw RTE_LOC;

        // Compute the random OT messages.
        Mb.fromBytes(recvBuff.data());
        std::vector<u8> hashBuff(Point::size);
        oc::RandomOracle ro(sizeof(block));
        for (u64 i = 0; i < n; ++i)
        {
            k = Mb;
            k *= mSk[i];

            k.toBytes(hashBuff.data());
            ro.Reset();
            ro.Update(i * 2 + mChoices[i]);
            ro.Update(hashBuff.data(), Point::size);
            ro.Final(messages[i]);
        }

        resetState();
    }

    void MasnyRindal::sendRoundOne(
        u64 n,
        PRNG& prng,
        std::vector<u8>& buff)
    {
        if (mState != State::RoundOne)
            panic("bad state, " LOCATION);

        Curve curve;
        auto pointSize = Point::size;
        mSk = {};
        mSk.emplace_back();
        mSk[0].randomize(prng);

        Point Mb = Point::mulGenerator(mSk[0]);

        auto begin = buff.size();
        buff.resize(begin + Point::size);
        Mb.toBytes(buff.data() + begin);

        mState = State::RoundTwo;
    }



    void MasnyRindal::sendRoundTwo(
        span<std::array<block, 2>> messages,
        PRNG& prng,
        span<u8>& buff)
    {
        if (mState != State::RoundTwo)
            panic("bad state, " LOCATION);

        u64 n = static_cast<u64>(messages.size());
        Curve curve;
        auto pointSize = Point::size;
        oc::RandomOracle ro(sizeof(block));

        std::vector<u8> hashBuff(roundUpTo(pointSize, 16));
        Point pHash, r;

        if (buff.size() != n * Point::size * 2)
            throw RTE_LOC;

        for (u64 i = 0; i < n; ++i)
        {
            std::array<span<u8>, 2> buffIters{
                buff.subspan(0,Point::size),
                buff.subspan(Point::size,Point::size)
            };
            buff = buff.subspan(2 * Point::size);

            for (u64 j = 0; j < 2; ++j)
            {

                r.fromBytes(buffIters[j].data());
                pHash.fromHash(buffIters[j ^ 1].data(), int(pointSize));
                r += pHash;
                r *= mSk[0];

                r.toBytes(hashBuff.data());
                ro.Reset();
                ro.Update(i * 2 + j);
                ro.Update(hashBuff.data(), Point::size);
                ro.Final(messages[i][j]);
            }
        }

        resetState();
    }

    namespace tests
    {

        void Bot_MasnyRindal_Buff_test()
        {

            PRNG prng0(oc::ZeroBlock);
            PRNG prng1(oc::OneBlock);

            u64 numOTs = 50;
            std::vector<block> recvMsg(numOTs);
            std::vector<std::array<block, 2>> sendMsg(numOTs);
            BitVector choices(numOTs);
            choices.randomize(prng0);

            MasnyRindal baseOTs0, baseOTs1;

            std::vector<u8> buff0, buff1;

            baseOTs0.receiveRoundOne(choices, prng0, buff0);
            baseOTs1.sendRoundOne(numOTs, prng1, buff1);

            std::stringstream ss0;
            baseOTs0.serialize(ss0);
            baseOTs0.resetState();
            baseOTs0.deserialize(ss0);

            //std::stringstream ss1;
            //baseOTs1.serialize(ss1);
            //baseOTs1.resetState();
            //baseOTs1.deserialize(ss1);


            span<u8> span1 = buff1;
            span<u8> span0 = buff0;
            baseOTs0.receiveRoundTwo(recvMsg, prng0, span1);
            baseOTs1.sendRoundTwo(sendMsg, prng1, span0);

            for (u64 i = 0; i < numOTs; ++i)
            {
                if (neq(recvMsg[i], sendMsg[i][choices[i]]))
                {
                    std::cout << "failed " << i << " exp = m[" << int(choices[i]) << "], act = " << recvMsg[i] << " true = " << sendMsg[i][0] << ", " << sendMsg[i][1] << std::endl;
                    throw oc::UnitTestFail();
                }
            }
        }

    }

}
