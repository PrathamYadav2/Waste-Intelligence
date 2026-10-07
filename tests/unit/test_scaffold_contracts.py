import pytest
from src.recovery.scoring import ROUTES, score_recovery, RecoveryInput
from src.forecasting.pipeline import CANDIDATES
from src.vision.classifier import ClassifierFactory

def test_routes_defined():
    assert len(ROUTES) == 6

def test_candidates_exclude_lstm():
    assert "lstm" not in CANDIDATES

def test_recovery_scoring_real():
    res = score_recovery(RecoveryInput(waste_class="Glass", condition="clean"))
    assert res.score > 0
    assert res.route in ROUTES
    assert "material_factor" in res.factor_breakdown

def test_classifier_factory_unsupported():
    with pytest.raises(ValueError):
        ClassifierFactory.create("unsupported_backbone_xyz")
