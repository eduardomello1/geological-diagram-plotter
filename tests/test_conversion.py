import pytest

from pyroxene_diagram.conversion import ternary_coordinates


def test_coordinates_are_normalized_to_100():
    assert ternary_coordinates(1, 2, 1) == (25.0, 50.0, 25.0)


@pytest.mark.parametrize("values", [(-1, 2, 3), (0, 0, 0)])
def test_invalid_compositions_raise(values):
    with pytest.raises(ValueError):
        ternary_coordinates(*values)
