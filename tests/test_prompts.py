import pytest

from som.etapa2_prompts import Prompt, PromptSet


def test_hash_estavel():
    pset = PromptSet(
        nome="t",
        prompts=[Prompt(id="1", texto="olá"), Prompt(id="2", texto="mundo")],
    )
    h1 = pset.hash_congelamento
    pset2 = PromptSet(
        nome="t",
        prompts=[Prompt(id="1", texto="olá"), Prompt(id="2", texto="mundo")],
        hash_congelamento=h1,
    )
    pset2.verificar_congelamento()  # não deve levantar


def test_quebra_congelamento():
    pset = PromptSet(
        nome="t",
        prompts=[Prompt(id="1", texto="olá")],
    )
    h = pset.hash_congelamento
    # altera o texto
    pset.prompts[0].texto = "alterado"
    with pytest.raises(RuntimeError, match="alterado após o congelamento"):
        # força recálculo interno
        pset.hash_congelamento = h
        pset.verificar_congelamento()
