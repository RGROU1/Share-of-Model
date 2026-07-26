from som.etapa1_escopo import Escopo, Marca


def test_resolver_alias():
    escopo = Escopo(
        categoria="teste",
        marcas=[
            Marca(id="a", nome="Marca A", aliases=["marca-a", "MA"]),
            Marca(id="b", nome="Marca B"),
        ],
    )
    assert escopo.resolver("Eu uso a Marca A há anos") == "a"
    assert escopo.resolver("recomendo marca-a") == "a"
    assert escopo.resolver("MA é ótimo") == "a"
    assert escopo.resolver("nada a ver") is None


def test_alerta_diluicao():
    marcas = [Marca(id=f"m{i}", nome=f"M{i}") for i in range(15)]
    escopo = Escopo(categoria="x", marcas=marcas)
    assert escopo.alerta_diluicao() is not None
    assert escopo.alerta_diluicao(limite=20) is None
