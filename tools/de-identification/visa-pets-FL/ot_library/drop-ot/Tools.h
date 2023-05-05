/*
*   Copyright 2022-2023 Visa
*
*   This code is licensed under the Creative Commons
*   Attribution-NonCommercial 4.0 International Public License 
*   (https://creativecommons.org/licenses/by-nc/4.0/legalcode).
*/
#pragma once
#include <cryptoTools/Common/Defines.h>
#include <cryptoTools/Common/MatrixView.h>
#include <cassert>
namespace osuCrypto {




    void eklundh_transpose128(block* inOut);
    inline void eklundh_transpose128(std::array<block, 128>& inOut) { eklundh_transpose128(inOut.data()); }

#ifdef OC_ENABLE_AVX2
    void avx_transpose128(block* inOut);
#endif
#ifdef OC_ENABLE_SSE2
    void sse_transpose128(block* inOut);
    inline void sse_transpose128(std::array<block, 128>& inOut) { sse_transpose128(inOut.data()); };
#endif
    void transpose(const MatrixView<block>& in, const MatrixView<block>& out);
    void transpose(const MatrixView<u8>& in, const MatrixView<u8>& out);


    // Input must be given the alignment of an AlignedBlockArray, i.e. 32 bytes with AVX or 16 bytes
    // without.
    inline void transpose128(block* inOut)
    {
#if defined(OC_ENABLE_AVX2)
        assert((u64)inOut % 32 == 0);
        avx_transpose128(inOut);
#elif defined(OC_ENABLE_SSE2)
        assert((u64)inOut % 16 == 0);
        sse_transpose128(inOut);
#else
        eklundh_transpose128(inOut);
#endif
    }

    inline void transpose128(std::array<block, 128>& inOut) { transpose128(inOut.data()); };
}
