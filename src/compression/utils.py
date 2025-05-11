from .elias import EliasDeltaEncoder, EliasGammaEncoder
from ..utils.logger import get_logger

logger = get_logger(__name__)


def encode_postings(postings: list[int]) -> bytes:
    if not postings:
        return b""

    sorted_postings = sorted(list(set(postings)))
    deltas = [sorted_postings[0]]
    for i in range(1, len(sorted_postings)):
        deltas.append(sorted_postings[i] - sorted_postings[i - 1])

    return EliasGammaEncoder.encode(deltas)


def decode_postings(encoded: bytes) -> list[int]:
    deltas = EliasGammaEncoder.decode(encoded)

    if not deltas:
        return []

    postings = [deltas[0]]
    for delta in deltas[1:]:
        postings.append(postings[-1] + delta)

    return postings
