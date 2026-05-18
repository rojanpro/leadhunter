from app.services.evolution import EvolutionClient


def test_evolution_unconfigured_is_safe():
    client = EvolutionClient()
    assert isinstance(client.configured(), bool)
