"""Spelbalans, kleuren en basisstatistieken van De Wildernis."""

POTION_GENEZING_PERCENT = 30
POTION_PRIJS = 30
WAPEN_PRIJS = 80
WAPEN_VERBETERING = 8
XP_PER_LEVEL = 3
VIJAND_XP_MIN = 1
VIJAND_XP_MAX = 2
VIJAND_HP_PER_LEVEL = 8
VIJAND_AANVAL_PER_LEVEL = 1
GEVECHT_KANS = 75
RUST_GENEZING = 40
BAAS_LEVEL = 24
BAAS_HP_BEREIK = (420, 560)
BAAS_AANVAL_BEREIK = (34, 42)
BAAS_GENEZING_BEREIK = (8, 14)
# Preserve the representative values imported by older versions of the game.
BAAS_HP = sum(BAAS_HP_BEREIK) // 2
BAAS_GENEZING = sum(BAAS_GENEZING_BEREIK) // 2
VERDEDIGING_PERCENT = 65
BAAS_WOEDE_MULTIPLIER = 2
NEDERLAAG_GOUD = 100
LEVEL_UPGRADE_INTERVAL = 5
LEVEL_HP_UPGRADE = 20
LEVEL_AANVAL_UPGRADE = 5
LEVEL_VERDEDIGING_UPGRADE = 1
LEVEL_BASIS_HP = 30
MAX_LEVEL = 25
EINDBAAS_LEVEL = 25
EINDBAAS_HP_BEREIK = (700, 900)
EINDBAAS_AANVAL_BEREIK = (42, 54)
EINDBAAS_GENEZING_BEREIK = (12, 18)
EINDBAAS_HP = sum(EINDBAAS_HP_BEREIK) // 2
EINDBAAS_AANVAL = sum(EINDBAAS_AANVAL_BEREIK) // 2
EINDBAAS_GENEZING = sum(EINDBAAS_GENEZING_BEREIK) // 2

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

VERHALEN = {
    "Het Maanwoud": {
        "beschrijving": "Een evenwichtig avontuur vol geheimen en onverwachte vondsten.",
        "gevecht_bonus": 0,
        "goud_bonus": 0,
        "genezing_bonus": 0,
    },
    "De Vervloekte Moerassen": {
        "beschrijving": "Minder ontmoetingen en kleinere schatten, maar betere genezing.",
        "gevecht_bonus": -10,
        "goud_bonus": -5,
        "genezing_bonus": 15,
    },
    "De Drakenpas": {
        "beschrijving": "Meer gevaar onderweg, met rijkere schatten als beloning.",
        "gevecht_bonus": 10,
        "goud_bonus": 15,
        "genezing_bonus": -10,
    },
}


def xp_voor_level(level):
    return XP_PER_LEVEL


def wapen_prijs(speler):
    upgrades = speler["wapen_upgrades"]
    return WAPEN_PRIJS + upgrades * 35 + upgrades ** 2 * 15


def wapen_limiet(speler):
    return 1 + speler["level"] // 2
