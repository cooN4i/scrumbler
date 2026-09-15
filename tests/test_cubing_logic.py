from app.services.scrambler import generate_scramble_3x3
from app.services.stats import calculate_average_trimmed, format_time


def test_scramble_length_and_validity():
    scramble = generate_scramble_3x3(21)
    moves = scramble.split()
    assert len(moves) == 21

    # Check that consecutive moves don't touch the same face
    for i in range(len(moves) - 1):
        face1 = moves[i][0]
        face2 = moves[i + 1][0]
        assert face1 != face2, f"Consecutive moves share face: {moves[i]}, {moves[i + 1]}"


def test_calculate_average_trimmed_regular():
    # 5 solves: 10.00, 11.00, 12.00, 13.00, 14.00 (in ms: 10000, 11000, 12000, 13000, 14000)
    # Best (10000) and Worst (14000) are trimmed.
    # Average of 11000, 12000, 13000 = 12000 ms.
    times = [10000, 11000, 12000, 13000, 14000]
    avg = calculate_average_trimmed(times)
    assert avg == 12000


def test_calculate_average_trimmed_single_dnf():
    # 1 DNF among 5 solves:
    # 10000, 11000, 12000, 13000, None (DNF)
    # The DNF is considered worst and trimmed. Best (10000) is trimmed.
    # Average of remaining: 11000, 12000, 13000 = 12000.
    times = [10000, 11000, 12000, 13000, None]
    avg = calculate_average_trimmed(times)
    assert avg == 12000


def test_calculate_average_trimmed_two_dnfs():
    # 2 DNFs among 5 solves:
    # More than 1 DNF in ao5 -> Whole average is DNF (returns None)
    times = [10000, 11000, 12000, None, None]
    avg = calculate_average_trimmed(times)
    assert avg is None


def test_format_time():
    assert format_time(8420) == "8.42"
    assert format_time(68420) == "1:08.42"
    assert format_time(None) == "DNF"
    assert format_time(10000, penalty="+2") == "10.00+"
    assert format_time(10000, penalty="dnf") == "DNF"
