"""Spelbalans, kleuren en basisstatistieken van De Wildernis."""

POTION_GENEZING_PERCENT = 50
POTION_PRIJS = 20
WAPEN_PRIJS = 80
WAPEN_VERBETERING = 8
XP_PER_LEVEL = 1
VIJAND_HP_PER_LEVEL = 8
VIJAND_AANVAL_PER_LEVEL = 1
GEVECHT_KANS = 75
RUST_GENEZING = 40
BAAS_LEVEL = 30
BAAS_HP = 1700
BAAS_GENEZING = 16  # Na elke vijandelijke beurt.
VERDEDIGING_PERCENT = 65
BAAS_WOEDE_MULTIPLIER = 2
NEDERLAAG_GOUD = 100
LEVEL_HP_UPGRADE = 40
LEVEL_AANVAL_UPGRADE = 10
LEVEL_VERDEDIGING_UPGRADE = 2
LEVEL_BASIS_HP = 30
EINDBAAS_LEVEL = 100
EINDBAAS_HP = 12_000
EINDBAAS_AANVAL = 150
EINDBAAS_GENEZING = 60

ACHTERGROND = "#0d171e"
PANEEL = "#17272e"
PANEEL_LICHT = "#263c43"
TEKST = "#edf3e8"
GEDIMD = "#a8b9b5"
GROEN = "#83c98a"
GOUD = "#f2c66d"
ROOD = "#ef7771"

KLASSEN = {
    "Krijger": {"hp": 240, "aanval": 40, "kritieke_kans": 10},
    "Magiër": {"hp": 180, "aanval": 55, "kritieke_kans": 10},
    "Sluipmoordenaar": {"hp": 210, "aanval": 38, "kritieke_kans": 40},
}

VIJANDEN = {
    "Goblin": {"hp": 40, "aanval": 8, "goud": 12},
    "Orc": {"hp": 60, "aanval": 11, "goud": 20},
    "Draak": {"hp": 90, "aanval": 15, "goud": 35},
}


def xp_voor_level(level):
    return XP_PER_LEVEL


def wapen_prijs(speler):
    upgrades = speler["wapen_upgrades"]
    return WAPEN_PRIJS + upgrades * 35 + upgrades ** 2 * 15


def wapen_limiet(speler):
    return 1 + speler["level"] // 2
