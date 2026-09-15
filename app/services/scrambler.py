import random

# WCA 3x3x3 Move Groups
# Faces: R, L, U, D, F, B
# Axis grouping:
# Axis 0: R, L (Right / Left)
# Axis 1: U, D (Up / Down)
# Axis 2: F, B (Front / Back)

AXIS_FACES = {
    0: ["R", "L"],
    1: ["U", "D"],
    2: ["F", "B"],
}

FACE_TO_AXIS = {
    "R": 0, "L": 0,
    "U": 1, "D": 1,
    "F": 2, "B": 2,
}

MODIFIERS = ["", "'", "2"]


def generate_scramble_3x3(length: int = 21) -> str:
    """
    Generates a valid WCA-compliant 3x3x3 scramble.
    Ensures:
    1. Consecutive moves never use the same face (e.g., no 'R R' or 'R R2').
    2. Moves along the same axis never conflict (e.g., no 'R L R' or 'U D U' sequences).
    """
    moves = []
    last_axis = None
    second_last_axis = None

    faces = ["R", "L", "U", "D", "F", "B"]
    last_face = None

    while len(moves) < length:
        face = random.choice(faces)
        axis = FACE_TO_AXIS[face]

        # Condition 1: Can't pick the same face twice in a row
        if face == last_face:
            continue

        # Condition 2: If previous two moves were on the same axis (e.g. R then L),
        # the third move cannot be on that same axis (no R L R')
        if axis == last_axis and last_axis == second_last_axis:
            continue

        # If previous move was on the same axis, we can't repeat the face,
        # but also to avoid non-standard patterns like R L R, check if last was on same axis
        if axis == last_axis:
            # We already checked face != last_face.
            pass

        modifier = random.choice(MODIFIERS)
        moves.append(f"{face}{modifier}")

        second_last_axis = last_axis
        last_axis = axis
        last_face = face

    return " ".join(moves)
