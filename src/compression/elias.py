import math

from ..utils.exceptions import CompressionError
from ..utils.logger import get_logger

logger = get_logger(__name__)


class EliasGammaEncoder:
    """Кодер Элиаса-Гамма для положительных целых чисел"""

    @staticmethod
    def encode_number(number: int) -> str:
        """Кодирование одного числа в битовую строку"""
        if number <= 0:
            logger.error(f"Для кодирования Элиаса-Гамма требуются положительные числа, получено: {number}")
            raise CompressionError("Число должно быть положительным для кодирования Элиаса-Гамма")

        n_bit = int(math.log2(number))
        return "0" * n_bit + bin(number)[2:]

    @staticmethod
    def encode(numbers: list[int]) -> bytes:
        """Пакетное кодирование списка чисел в байты"""
        if not numbers:
            return b""

        bitstring = ""
        for n in numbers:
            bitstring += EliasGammaEncoder.encode_number(n)

        # Выравнивание длины битовой строки до кратной 8
        padding = len(bitstring) % 8
        bitstring += "0" * padding

        # Преобразование битовой строки в байты
        byte_array = bytearray()
        for i in range(0, len(bitstring), 8):
            byte = bitstring[i: i + 8]
            byte_array.append(int(byte, 2))

        return bytes(byte_array)

    @staticmethod
    def decode(byte_data: bytes) -> list[int]:
        """Декодирование байтов в список чисел"""
        if not byte_data:
            return []

        bitstring = "".join(f"{byte:08b}" for byte in byte_data)
        numbers = []
        i = 0
        n = len(bitstring)

        zero_counter = 0
        while i < n:
            # Подсчёт ведущих нулей
            if bitstring[i] == "0":
                zero_counter += 1
                i += 1
                continue

            # Извлечение закодированного числа
            number = int(bitstring[i: i + zero_counter + 1], 2)
            numbers.append(number)

            i += zero_counter + 1
            zero_counter = 0

        return numbers


class EliasDeltaEncoder:
    """Кодер Элиаса-Дельта для положительных целых чисел"""

    @staticmethod
    def encode_number(number: int) -> str:
        """Кодирование одного числа в битовую строку"""
        if number <= 0:
            logger.error(f"Для кодирования Элиаса-Дельта требуются положительные числа, получено: {number}")
            raise CompressionError("Число должно быть положительным для кодирования Элиаса-Дельта")

        n = int(math.log2(number)) + 1
        gamma_n_code = EliasGammaEncoder.encode_number(n)
        return gamma_n_code + bin(number)[3:]  # Отрезаем ведущую 1

    @staticmethod
    def encode(numbers: list[int]) -> bytes:
        """Пакетное кодирование списка чисел в байты"""
        if not numbers:
            return b""

        bitstring = ""
        for n in numbers:
            bitstring += EliasDeltaEncoder.encode_number(n)

        # Выравнивание длины битовой строки до кратной 8
        padding = len(bitstring) % 8
        bitstring += "0" * padding

        # Преобразование битовой строки в байты
        byte_array = bytearray()
        for i in range(0, len(bitstring), 8):
            byte = bitstring[i: i + 8]
            byte_array.append(int(byte, 2))

        return bytes(byte_array)

    @staticmethod
    def decode(byte_data: bytes) -> list[int]:
        """Декодирование байтов в список чисел"""
        if not byte_data:
            return []

        bitstring = "".join(f"{byte:08b}" for byte in byte_data)
        numbers = []
        i = 0
        n = len(bitstring)

        zero_counter = 0
        while i < n:
            # Определение длины кода длины
            if bitstring[i] == "0":
                zero_counter += 1
                i += 1
                continue

            # Декодирование длины числа
            bit_count = int(bitstring[i: i + zero_counter + 1], 2)
            i += zero_counter + 1

            # Восстановление исходного числа
            number = int("1" + bitstring[i: i + bit_count - 1], 2)
            numbers.append(number)

            i += bit_count - 1
            zero_counter = 0

        return numbers
