"""File/function localization and reliability metrics."""


def metrics(ranking, gold):
    ranking = list(dict.fromkeys(ranking))
    gold = set(gold)
    if not gold:
        return dict(eligible=False, top1=None, top5=None, top10=None, mrr=None, recall10=None)
    hits = [i + 1 for i, p in enumerate(ranking) if p in gold]
    return dict(
        eligible=True,
        top1=int(bool(hits and min(hits) <= 1)),
        top5=int(bool(hits and min(hits) <= 5)),
        top10=int(bool(hits and min(hits) <= 10)),
        mrr=1 / min(hits) if hits else 0,
        recall10=len(set(ranking[:10]) & gold) / len(gold),
    )


def set_metrics(predicted, expected):
    """Multi-location precision/recall/F1 for a declared prediction cutoff."""
    predicted, expected = set(predicted), set(expected)
    if not expected:
        return dict(precision=None, recall=None, f1=None)
    hits = len(predicted & expected)
    precision = hits / len(predicted) if predicted else 0.0
    recall = hits / len(expected)
    return dict(
        precision=precision,
        recall=recall,
        f1=2 * precision * recall / (precision + recall) if precision + recall else 0.0,
    )


def calibration(probabilities, outcomes, bins=10):
    """For externally calibrated probabilities only; no confidence is fabricated."""
    if not probabilities or len(probabilities) != len(outcomes) or bins < 1:
        raise ValueError("Calibration requires aligned nonempty samples and positive bins")
    if any(not 0 <= p <= 1 for p in probabilities) or any(y not in (0, 1) for y in outcomes):
        raise ValueError("Invalid probability or binary outcome")
    brier = sum((p - y) ** 2 for p, y in zip(probabilities, outcomes)) / len(outcomes)
    ece = 0.0
    for i in range(bins):
        members = [
            (p, y) for p, y in zip(probabilities, outcomes) if min(bins - 1, int(p * bins)) == i
        ]
        if members:
            ece += abs(sum(p - y for p, y in members)) / len(outcomes)
    return dict(brier=brier, ece=ece)


def selective_accuracy(correct, abstained):
    if not correct or len(correct) != len(abstained):
        raise ValueError("Selective accuracy requires aligned nonempty cases")
    accepted = [x for x, a in zip(correct, abstained) if not a]
    return dict(
        coverage=len(accepted) / len(correct),
        accuracy=sum(accepted) / len(accepted) if accepted else None,
    )


def cost_accuracy_auc(points):
    """Trapezoidal area over measured cost/accuracy pairs (no extrapolation)."""
    points = sorted(points)
    if len(points) < 2 or any(c < 0 or not 0 <= a <= 1 for c, a in points):
        raise ValueError("Need at least two valid cost/accuracy measurements")
    return sum((b[0] - a[0]) * (a[1] + b[1]) / 2 for a, b in zip(points, points[1:]))
