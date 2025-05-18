import pytest

from src.compression.elias import EliasGammaEncoder, EliasDeltaEncoder, CompressionError


def test_elias_gamma_encode_number_valid():

    assert EliasGammaEncoder.encode_number(1) == "1"

    assert EliasGammaEncoder.encode_number(4) == "00100"

    assert EliasGammaEncoder.encode_number(10) == "0001010"


def test_elias_gamma_encode_number_invalid():
    with pytest.raises(CompressionError):
        EliasGammaEncoder.encode_number(0)
    with pytest.raises(CompressionError):
        EliasGammaEncoder.encode_number(-5)


def test_elias_gamma_encode_and_decode():
    numbers = [1, 2, 3, 4, 5, 15]
    encoded = EliasGammaEncoder.encode(numbers)
    decoded = EliasGammaEncoder.decode(encoded)
    assert decoded == numbers


def test_elias_gamma_encode_empty():
    assert EliasGammaEncoder.encode([]) == b""
    assert EliasGammaEncoder.decode(b"") == []


def test_elias_delta_encode_number_valid():
    assert EliasDeltaEncoder.encode_number(
        1) == EliasGammaEncoder.encode_number(1) + ""
    code = EliasDeltaEncoder.encode_number(10)
    assert isinstance(code, str)
    assert len(code) > 0


def test_elias_delta_encode_number_invalid():
    with pytest.raises(CompressionError):
        EliasDeltaEncoder.encode_number(0)
    with pytest.raises(CompressionError):
        EliasDeltaEncoder.encode_number(-1)


def test_elias_delta_encode_and_decode():
    numbers = [1, 2, 3, 4]
    encoded = EliasDeltaEncoder.encode(numbers)
    decoded = EliasDeltaEncoder.decode(encoded)
    assert decoded == numbers


def test_elias_delta_encode_empty():
    assert EliasDeltaEncoder.encode([]) == b""
    assert EliasDeltaEncoder.decode(b"") == []
