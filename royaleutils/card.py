import royaleutils.utils
import pandas as pd
import logging

class Card(object):
    def __init__(self, card_data):
        self.name = card_data.get("name")
        self.id = card_data.get("id")
        self.level = card_data.get("level")
        self.star_level = card_data.get("starLevel")
        self.evolution_level = card_data.get("evolutionLevel")
        self.max_level = card_data.get("maxLevel")
        self.max_evolution_level = card_data.get("maxEvolutionLevel")
        self.rarity = card_data.get("rarity")
        self.elixir_cost = card_data.get("elixirCost")
        self.icon_urls = card_data.get("iconUrls", {})

    def __repr__(self):
        return f"<Card {self.name} (Level {self.level}, {self.rarity.title()})>"