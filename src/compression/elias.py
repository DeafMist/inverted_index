import math

from ..utils.exceptions import CompressionError
from ..utils.logger import get_logger

logger = get_logger(__name__)


class EliasGammaEncoder:
    @staticmethod
    def encode_number(number: int) -> str:
        if number <= 0:
            logger.error(f"Elias Gamma encoding requires positive integers, got {number}")
            raise CompressionError("Number must be positive for Elias Gamma encoding")

        n_bit = int(math.log2(number))
        return "0" * n_bit + bin(number)[2:]

    @staticmethod
    def encode(numbers: list[int]) -> bytes:
        if not numbers:
            return b""

        bitstring = ""
        for n in numbers:
            bitstring += EliasGammaEncoder.encode_number(n)

        # Pad with zeros to make length multiple of 8
        padding = len(bitstring) % 8
        bitstring += "0" * padding

        # Convert to bytes
        byte_array = bytearray()
        for i in range(0, len(bitstring), 8):
            byte = bitstring[i: i + 8]
            byte_array.append(int(byte, 2))

        return bytes(byte_array)

    @staticmethod
    def decode(byte_data: bytes) -> list[int]:
        if not byte_data:
            return []

        bitstring = "".join(f"{byte:08b}" for byte in byte_data)
        numbers = []
        i = 0
        n = len(bitstring)

        zero_counter = 0
        while i < n:
            if bitstring[i] == "0":
                zero_counter += 1
                i += 1
                continue

            number = int(bitstring[i: i + zero_counter + 1], 2)
            numbers.append(number)

            i += zero_counter + 1
            zero_counter = 0

        return numbers


class EliasDeltaEncoder:
    @staticmethod
    def encode_number(number: int) -> str:
        if number <= 0:
            logger.error(f"Elias Delta encoding requires positive integers, got {number}")
            raise CompressionError("Number must be positive for Elias Delta encoding")

        n = int(math.log2(number)) + 1
        gamma_n_code = EliasGammaEncoder.encode_number(n)
        return gamma_n_code + bin(number)[3:]

    @staticmethod
    def encode(numbers: list[int]) -> bytes:
        if not numbers:
            return b""

        bitstring = ""
        for n in numbers:
            bitstring += EliasDeltaEncoder.encode_number(n)

        # Pad with zeros to make length multiple of 8
        padding = len(bitstring) % 8
        bitstring += "0" * padding

        # Convert to bytes
        byte_array = bytearray()
        for i in range(0, len(bitstring), 8):
            byte = bitstring[i: i + 8]
            byte_array.append(int(byte, 2))

        return bytes(byte_array)

    @staticmethod
    def decode(byte_data: bytes) -> list[int]:
        if not byte_data:
            return []

        bitstring = "".join(f"{byte:08b}" for byte in byte_data)
        numbers = []
        i = 0
        n = len(bitstring)

        zero_counter = 0
        while i < n:
            if bitstring[i] == "0":
                zero_counter += 1
                i += 1
                continue

            bit_count = int(bitstring[i: i + zero_counter + 1], 2)
            i += zero_counter + 1

            number = int("1" + bitstring[i: i + bit_count - 1], 2)
            numbers.append(number)

            i += bit_count - 1
            zero_counter = 0

        return numbers
