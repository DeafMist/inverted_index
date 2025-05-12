from .elias import EliasDeltaEncoder, EliasGammaEncoder


def encode_postings(postings: list[int], method: str) -> bytes:
    if not postings:
        return b""

    sorted_postings = sorted(list(set(postings)))
    deltas = [sorted_postings[0]]
    for i in range(1, len(sorted_postings)):
        deltas.append(sorted_postings[i] - sorted_postings[i - 1])

    if method == 'delta':
        return EliasDeltaEncoder.encode(deltas)
    return EliasGammaEncoder.encode(deltas)  # по умолчанию gamma


def decode_postings(encoded: bytes, method: str) -> list[int]:
    if method == 'delta':
        deltas = EliasDeltaEncoder.decode(encoded)
    else:  # gamma по умолчанию
        deltas = EliasGammaEncoder.decode(encoded)

    if not deltas:
        return []

    postings = [deltas[0]]
    for delta in deltas[1:]:
        postings.append(postings[-1] + delta)

    return postings
