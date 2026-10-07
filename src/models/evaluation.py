from dataclasses import asdict, dataclass

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


@dataclass(frozen=True)
class Metrics:
    mae_mgd: float
    rmse_mgd: float
    r2: float | None
    n_samples: int

    @property
    def target_met(self) -> bool:
        return self.r2 is not None and self.r2 > 0.80 and self.mae_mgd < 0.05

    def to_dict(self) -> dict:
        return {**asdict(self), "target_met": self.target_met}


def evaluate(actual: np.ndarray, predicted: np.ndarray) -> Metrics:
    actual, predicted = np.asarray(actual, dtype=float), np.asarray(predicted, dtype=float)
    if actual.ndim != 1 or actual.shape != predicted.shape or actual.size < 2:
        raise ValueError("evaluation needs at least two aligned one-dimensional observations")
    if not np.isfinite(actual).all() or not np.isfinite(predicted).all():
        raise ValueError("evaluation values must be finite")
    return Metrics(
        mae_mgd=float(mean_absolute_error(actual, predicted)),
        rmse_mgd=float(np.sqrt(mean_squared_error(actual, predicted))),
        r2=float(r2_score(actual, predicted)) if np.ptp(actual) > 1e-12 else None,
        n_samples=len(actual),
    )
