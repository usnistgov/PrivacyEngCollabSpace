/*
*   Copyright 2022-2023 Visa
*
*   This code is licensed under the Creative Commons
*   Attribution-NonCommercial 4.0 International Public License 
*   (https://creativecommons.org/licenses/by-nc/4.0/legalcode).
*/
#pragma once
#include "drop-ot/config.h"
#include "cryptoTools/Common/Defines.h"
#include "cryptoTools/Common/Version.h"
#include "cryptoTools/Crypto/PRNG.h"
#include "cryptoTools/Network/Channel.h"
#include "cryptoTools/Common/BitVector.h"
#include <system_error>
#include <cryptoTools/Crypto/SodiumCurve.h>


#if CRYPTO_TOOLS_VERSION  < 10502
static_assert(0, "please update cryptoTools");
#endif

#ifdef DROP_OT_ENABLE_RELIC
#include "cryptoTools/Crypto/RCurve.h"

#ifndef ENABLE_RELIC
static_assert(0, "please enable relic in cryptoTools");
#endif

#if !defined(MULTI) || ((MULTI != PTHREAD) && (MULTI != OPENMP))
static_assert(0,"Relic must be built with -DMULTI=PTHREAD or -DMULTI=OPENMP");
#endif
#endif
#ifdef DROP_OT_ENABLE_SODIUM
#include "cryptoTools/Crypto/SodiumCurve.h"

#endif

namespace dropOt
{
    using u64 = oc::u64;
    using i64 = oc::i64;
    using u32 = oc::u32;
    using i32 = oc::i32;
    using u16 = oc::u16;
    using i16 = oc::i16;
    using u8 = oc::u8;
    using i8 = oc::i8;

    template<typename T>
    using span = oc::span<T>;

    using block = oc::block;
    inline block toBlock(u8* data) { return oc::toBlock(data); }
    inline block toBlock(u64 low_u64) { return oc::toBlock(low_u64); }
    inline block toBlock(u64 high_u64, u64 low_u64) { return oc::toBlock(high_u64, low_u64); }

    
#ifdef DROP_OT_ENABLE_RELIC
    using Number = oc::REccNumber;
    using Point = oc::REccPoint;
    using Curve = oc::REllipticCurve;
#else

    using Number = oc::Sodium::Prime25519;
    using Point = oc::Sodium::Rist25519;
    //using Curve = oc::REllipticCurve;
    struct Curve { Curve() {} };
#endif

#ifdef ENABLE_BOOST
    using Channel = oc::Channel;
#endif

    using BitVector = oc::BitVector;
    using PRNG = oc::PRNG;

    std::string hex(span<u8> d);

    [[ noreturn ]] inline void panic(const std::string& msg)
    {
        std::cout << "Panic, " << msg << std::endl;
        std::terminate();
    }

    inline u64 roundUpTo(u64 val, u64 step) { return ((val + step - 1) / step) * step; }

    enum class Role {
        R0, R1
    };



    enum class Op
    {
        Default, Add, Mult
    };

    inline void Agg(Point& agg, Point& r, Op op)
    {
        if (op == Op::Mult)
            panic("logic error");

        agg += r;
    }

    inline void Agg(Number& agg, Number& r, Op op)
    {
        if (op == Op::Add)
            agg += r;
        else
            agg *= r;
    }
}


