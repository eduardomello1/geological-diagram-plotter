"""Conversions and validation for Wo-En-Fs compositions."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Composition:
    name: str
    wo: float
    en: float
    fs: float

    def normalized(self) -> "Composition":
        total = self.wo + self.en + self.fs
        if total <= 0:
            raise ValueError("Wo + En + Fs must be greater than zero.")
        return Composition(
            self.name,
            self.wo * 100 / total,
            self.en * 100 / total,
            self.fs * 100 / total,
        )


def ternary_coordinates(wo: float, en: float, fs: float) -> tuple[float, float, float]:
    """Return Plotly ternary coordinates (a=Wo, b=En, c=Fs), normalized to 100."""
    values = (float(wo), float(en), float(fs))
    if any(value < 0 for value in values):
        raise ValueError("Wo, En and Fs cannot be negative.")
    total = sum(values)
    if total <= 0:
        raise ValueError("Wo + En + Fs must be greater than zero.")
    return tuple(value * 100 / total for value in values)
