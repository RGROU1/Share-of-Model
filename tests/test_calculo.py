from som.etapa6_calculo import intervalo_wilson


def test_wilson_limites():
    lo, hi = intervalo_wilson(0, 100)
    assert lo >= 0.0
    assert hi <= 1.0
    assert lo < hi

    lo, hi = intervalo_wilson(100, 100)
    assert lo >= 0.0
    assert hi <= 1.0


def test_wilson_centro():
    lo, hi = intervalo_wilson(50, 100)
    assert 0.4 < lo < 0.5
    assert 0.5 < hi < 0.6
