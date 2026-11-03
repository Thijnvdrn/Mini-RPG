"""Spelregels van De Wildernis. Start het spel met: python main.py."""

import random
import tkinter as tk
from tkinter import messagebox

from audio import AchtergrondMuziek
from interface import SpelInterface
# De instellingen blijven ook beschikbaar voor bestaande imports uit main.
from instellingen import (
    POTION_GENEZING_PERCENT, POTION_PRIJS, WAPEN_PRIJS, WAPEN_VERBETERING, XP_PER_LEVEL,
    VIJAND_XP_MIN, VIJAND_XP_MAX, VIJAND_HP_PER_LEVEL, VIJAND_AANVAL_PER_LEVEL,
    GEVECHT_KANS, RUST_GENEZING, BAAS_LEVEL, BAAS_HP, BAAS_HP_BEREIK, BAAS_AANVAL_BEREIK,
    BAAS_GENEZING, BAAS_GENEZING_BEREIK, VERDEDIGING_PERCENT, BAAS_WOEDE_MULTIPLIER,
    NEDERLAAG_GOUD,
    LEVEL_HP_UPGRADE, LEVEL_AANVAL_UPGRADE, LEVEL_VERDEDIGING_UPGRADE, LEVEL_BASIS_HP,
    LEVEL_UPGRADE_INTERVAL,
    MAX_LEVEL, EINDBAAS_LEVEL, EINDBAAS_HP, EINDBAAS_HP_BEREIK,
    EINDBAAS_AANVAL, EINDBAAS_AANVAL_BEREIK, EINDBAAS_GENEZING, EINDBAAS_GENEZING_BEREIK,
    ACHTERGROND, PANEEL, PANEEL_LICHT, TEKST, GEDIMD, GROEN, GOUD, ROOD, KLASSEN, VIJANDEN,
    VERHALEN,
    xp_voor_level, wapen_prijs, wapen_limiet,
)


def maak_speler(naam, klasse, verhaal="Het Maanwoud"):
    statistieken = KLASSEN[klasse]
    return {
        "naam": naam,
        "klasse": klasse,
        "verhaal": verhaal,
        "hp": statistieken["hp"],
        "max_hp": statistieken["hp"],
        "aanval": statistieken["aanval"],
        "verdediging": 0,
        "kritieke_kans": statistieken["kritieke_kans"],
        "goud": 20,
        "xp": 0,
        "level": 1,
        "inventaris": ["Health Potion", "Health Potion"],
        "baas_verslagen": False,
        "uitgespeeld": False,
        "wapen_upgrades": 0,
    }


def maak_vijand(speler_level):
    vijand_soort = random.choice(list(VIJANDEN))
    statistieken = VIJANDEN[vijand_soort]
    extra_levels = speler_level - 1
    hp = statistieken["hp"] + extra_levels * VIJAND_HP_PER_LEVEL
    return {
        "naam": vijand_soort,
        "beurten": 0,
        "hp": hp,
        "max_hp": hp,
        "aanval": statistieken["aanval"] + extra_levels * VIJAND_AANVAL_PER_LEVEL + extra_levels // 5,
        "goud": statistieken["goud"] + extra_levels * 2,
        "xp": random.randint(VIJAND_XP_MIN, VIJAND_XP_MAX),
    }


def maak_baas(speler_level):
    extra_levels = max(0, speler_level - BAAS_LEVEL)
    hp = random.randint(*BAAS_HP_BEREIK) + extra_levels * 30
    return {
        "naam": "Nachtvorst", "hp": hp, "max_hp": hp,
        "aanval": random.randint(*BAAS_AANVAL_BEREIK) + extra_levels * 2,
        "goud": 500, "xp": XP_PER_LEVEL,
        "baas": True, "woedend": False, "beurten": 0,
        "genezing": random.randint(*BAAS_GENEZING_BEREIK),
    }


def maak_gouden_draak():
    hp = random.randint(*EINDBAAS_HP_BEREIK)
    return {
        "naam": "Gouden Draak", "hp": hp, "max_hp": hp,
        "aanval": random.randint(*EINDBAAS_AANVAL_BEREIK), "goud": 2000, "xp": XP_PER_LEVEL,
        "baas": True, "eindbaas": True,
        "genezing": random.randint(*EINDBAAS_GENEZING_BEREIK),
        "woedend": False, "beurten": 0,
    }


class MiniRPG(SpelInterface):
    """Beheert de voortgang en voert de spelacties uit."""

    def __init__(self, root):
        self.root = root
        self.root.title("Mini-RPG — De Wildernis")
        breedte = min(1920, max(900, root.winfo_screenwidth() - 16))
        hoogte = min(1000, max(760, root.winfo_screenheight() - 80))
        self.root.geometry(f"{breedte}x{hoogte}+0+0")
        self.root.minsize(900, 760)
        self.root.configure(bg=ACHTERGROND)
        self.speler = None
        self.vijand = None
        self.gevecht = False
        self.level_keuzes = []
        self.level_upgrades = []
        self.level_keuze_venster = None
        self.animaties = set()
        self.canvas_redraw_tasks = {}
        self.muziek = AchtergrondMuziek()
        self.muziek_aan = False
        self.root.protocol("WM_DELETE_WINDOW", self.sluit_spel)
        self.maak_stijl()
        self.toon_startscherm()

    def start_spel(self):
        naam = self.naam_invoer.get().strip()
        if not naam:
            messagebox.showwarning("Naam ontbreekt", "Vul eerst de naam van je held in.")
            self.naam_invoer.focus_set()
            return
        verhaal = self.verhaal_keuze.get()
        self.speler = maak_speler(naam, self.klasse_keuze.get(), verhaal)
        self.level_keuzes = []
        self.level_upgrades = []
        if naam.casefold() == "baas":
            self.speler["level"] = BAAS_LEVEL
            self.speler["goud"] = 10_000_000
            for index in range(self.speler["level"] - 1):
                self.speler["max_hp"] += LEVEL_BASIS_HP
                self.speler["hp"] += LEVEL_BASIS_HP
                level = index + 2
                if level % LEVEL_UPGRADE_INTERVAL == 0:
                    keuze = ("hp", "aanval", "verdediging")[len(self.level_upgrades) % 3]
                    self.geef_level_upgrade(keuze)
        self.gevecht = False
        self.vijand = None
        self.muziek_aan = True
        self.start_muziek()
        self.toon_spelscherm()
        self.log(f"Welkom, {naam} de {self.speler['klasse']}! Je avontuur begint.")
        self.log(f"Verhaal gekozen: {verhaal}. {VERHALEN[verhaal]['beschrijving']}")
        self.log(
            f"Verdien {VIJAND_XP_MIN}-{VIJAND_XP_MAX} XP per vijand; "
            f"{XP_PER_LEVEL} XP brengt je een level omhoog. Max level: {MAX_LEVEL}."
        )
        self.log(
            f"Versla de Nachtvorst op level {BAAS_LEVEL} en de Gouden Draak "
            f"op level {EINDBAAS_LEVEL}. Elke {LEVEL_UPGRADE_INTERVAL} levels kies je een upgrade."
        )
        self.log("Elke derde vijandelijke beurt komt een zware aanval. Verdedig om 65% schade te blokkeren.")

    def herstel_hp(self, genezing):
        """Genees tot maximaal volle HP en geef het werkelijke herstel terug."""
        oude_hp = self.speler["hp"]
        self.speler["hp"] = min(self.speler["max_hp"], oude_hp + genezing)
        return self.speler["hp"] - oude_hp

    def kan_potion_gebruiken(self):
        return (
            "Health Potion" in self.speler["inventaris"]
            and self.speler["hp"] != self.speler["max_hp"]
        )

    def verken(self):
        if self.gevecht or self.speler["uitgespeeld"]:
            return
        if self.start_baasgevecht():
            return
        verhaal = VERHALEN[self.speler["verhaal"]]
        gevecht_kans = max(
            0, min(100, GEVECHT_KANS + verhaal["gevecht_bonus"])
        )
        if random.randint(1, 100) <= gevecht_kans:
            self.vijand = maak_vijand(self.speler["level"])
            self.gevecht = True
            self.log(f"Een {self.vijand['naam']} verschijnt uit de wildernis!")
            self.update_acties()
        else:
            self.verwerk_verkenningsvondst(verhaal)
        self.update_status()
        self.teken_scène()

    def verwerk_verkenningsvondst(self, verhaal):
        uitkomst = random.randint(1, 100)
        if uitkomst <= 40:
            genezing = random.randint(25, 55) + verhaal["genezing_bonus"]
            herstel = self.herstel_hp(max(1, genezing))
            self.log(f"Een verborgen bron herstelt {herstel} HP.")
        elif uitkomst <= 67:
            goud = max(1, random.randint(15, 55) + verhaal["goud_bonus"])
            self.speler["goud"] += goud
            self.log(f"Je vindt een vergeten schat met {goud} goud!")
        elif uitkomst <= 88:
            xp = random.randint(VIJAND_XP_MIN, VIJAND_XP_MAX)
            self.speler["xp"] += xp
            self.log(f"Een oud runenaltaar schenkt je {xp} XP.")
            self.controleer_level()
        else:
            self.speler["inventaris"].append("Health Potion")
            self.log("Een reiziger liet een Health Potion achter. Je vindt hem!")

    def start_baasgevecht(self):
        if (self.gevecht or self.speler["level"] < BAAS_LEVEL
                or self.speler["uitgespeeld"]
                or (self.speler["baas_verslagen"] and self.speler["level"] < EINDBAAS_LEVEL)):
            return False
        eindbaas = self.speler["level"] >= EINDBAAS_LEVEL
        self.vijand = maak_gouden_draak() if eindbaas else maak_baas(self.speler["level"])
        self.gevecht = True
        self.log(f"Baasgevecht! De {self.vijand['naam']} daalt neer tussen de bomen.")
        if eindbaas:
            self.log("Versla de Gouden Draak en speel het spel uit!")
        self.log("Elke derde beurt: een zware aanval! Bij halve HP wordt de baas woedend: 2× schade.")
        self.log(
            f"De {self.vijand['naam']} heeft {self.vijand['hp']} HP, "
            f"valt aan met {self.vijand['aanval']} kracht en geneest "
            f"{self.vijand['genezing']} HP per beurt."
        )
        self.ververs_scherm()
        return True

    def val_aan(self):
        if not self.gevecht or not self.vijand:
            return
        schade = random.randint(self.speler["aanval"] - 3, self.speler["aanval"] + 3)
        kritiek = random.randint(1, 100) <= self.speler["kritieke_kans"]
        if kritiek:
            schade *= 2
        self.vijand["hp"] = max(0, self.vijand["hp"] - schade)
        soort_aanval = "Spreuk" if self.speler["klasse"] == "Magiër" else "Aanval"
        melding = f"{soort_aanval} doet {schade} schade"
        self.log(melding + (" — kritieke treffer!" if kritiek else "."))
        self.verwerk_beurt()
        self.animeer_slag("held", "vijand", 1)
        self.toon_effect(f"{'KRITIEK! ' if kritiek else ''}−{schade}", .72, GOUD if kritiek else ROOD)

    def gebruik_potion(self):
        if not self.gevecht or not self.vijand:
            return
        if not self.kan_potion_gebruiken():
            return
        genezing = self.speler["max_hp"] * POTION_GENEZING_PERCENT // 100
        herstel = self.herstel_hp(genezing)
        self.speler["inventaris"].remove("Health Potion")
        self.log(f"Je gebruikt een potion en herstelt {herstel} HP.")
        self.verwerk_beurt()
        self.toon_effect(f"+{herstel} HP", .28, GROEN)

    def vlucht(self):
        if not self.gevecht or not self.vijand:
            return
        vlucht_kans = 35 if self.vijand.get("baas") else 60
        if random.randint(1, 100) <= vlucht_kans:
            self.log("Je ontsnapt! Je krijgt geen beloning.")
            self.gevecht = False
            self.vijand = None
            self.update_acties()
            self.teken_scène()
            return
        self.log("Vluchten mislukt!")
        self.vijand_valt_aan()

    def verwerk_beurt(self):
        if not self.gevecht or not self.vijand:
            return
        if self.vijand["hp"] != 0:
            self.vijand_valt_aan()
            return

        eindbaas = self.vijand.get("eindbaas", False)
        if self.vijand.get("baas") and not eindbaas:
            self.speler["baas_verslagen"] = True
            self.log("De Nachtvorst is verslagen! Het maanwoud is weer vrij.")
        self.speler["goud"] += self.vijand["goud"]
        xp = self.vijand["xp"]
        self.speler["xp"] += xp
        self.log(f"Gewonnen! +{self.vijand['goud']} goud en +{xp} XP.")
        self.gevecht = False
        self.vijand = None
        if eindbaas:
            self.controleer_level(kies_upgrade=False)
            self.speler["uitgespeeld"] = True
            self.toon_overwinningspagina()
            return
        self.controleer_level()
        self.ververs_scherm()

    def verdedig(self):
        if not self.gevecht or not self.vijand:
            return
        self.log(f"Je verdedigt en blokkeert {VERDEDIGING_PERCENT}% van de schade.")
        self.vijand_valt_aan(verdedigd=True)

    def vijand_valt_aan(self, verdedigd=False):
        if not self.gevecht or not self.vijand:
            return
        aanval = self.vijand["aanval"]
        self.vijand["beurten"] += 1
        if self.vijand.get("baas") and self.vijand["hp"] <= self.vijand["max_hp"] / 2:
            if not self.vijand["woedend"]:
                self.log(f"De {self.vijand['naam']} wordt woedend! Zijn aanvallen doen 2× schade.")
            self.vijand["woedend"] = True
        zware_aanval = self.vijand["beurten"] % 3 == 0
        if zware_aanval:
            aanval = aanval * 3 // 2
        schade = random.randint(aanval - 2, aanval + 2)
        if self.vijand.get("woedend"):
            schade *= BAAS_WOEDE_MULTIPLIER
        schade = max(1, schade - self.speler.get("verdediging", 0))
        if verdedigd:
            schade = max(1, schade * (100 - VERDEDIGING_PERCENT) // 100)
        self.speler["hp"] = max(0, self.speler["hp"] - schade)
        melding = f"De {self.vijand['naam']} doet {schade} schade"
        if zware_aanval:
            melding += " met drakenvuur!" if self.vijand.get("baas") else " met een zware aanval!"
        else:
            melding += "."
        self.log(melding)
        if self.speler["hp"] == 0:
            self.gevecht = False
            self.vijand = None
            verloren_goud = self.speler["goud"]
            verloren_level = self.verlies_level()
            self.speler["goud"] = NEDERLAAG_GOUD
            self.speler["hp"] = self.speler["max_hp"]
            self.toon_verliespagina(verloren_goud, verloren_level)
            return
        if self.gevecht and self.vijand.get("baas"):
            genezing = self.vijand.get("genezing", BAAS_GENEZING)
            self.vijand["hp"] = min(self.vijand["max_hp"], self.vijand["hp"] + genezing)
        self.ververs_scherm()
        self.animeer_slag("vijand", "held", -1)
        self.animeer_geraakt("held")
        self.toon_effect(f"−{schade}", .28, ROOD)

    def controleer_level(self, kies_upgrade=True):
        while (
            self.speler["level"] < MAX_LEVEL
            and self.speler["xp"] >= xp_voor_level(self.speler["level"])
        ):
            self.speler["xp"] -= xp_voor_level(self.speler["level"])
            self.speler["level"] += 1
            self.speler["max_hp"] += LEVEL_BASIS_HP
            if not kies_upgrade:
                continue
            bericht = f"Level omhoog! Je bent nu level {self.speler['level']}. +{LEVEL_BASIS_HP} Max HP."
            if self.speler["level"] % LEVEL_UPGRADE_INTERVAL == 0:
                self.level_keuzes.append(self.speler["level"])
                bericht += " Kies een upgrade."
            self.log(bericht)
        if self.speler["level"] >= MAX_LEVEL:
            self.speler["xp"] = 0
        if not kies_upgrade:
            return
        if self.level_keuzes:
            self.toon_level_keuze()
        else:
            self.start_baasgevecht()

    def geef_level_upgrade(self, keuze):
        if keuze == "hp":
            self.speler["max_hp"] += LEVEL_HP_UPGRADE
            self.speler["hp"] = min(
                self.speler["max_hp"], self.speler["hp"] + LEVEL_HP_UPGRADE
            )
        elif keuze == "aanval":
            self.speler["aanval"] += LEVEL_AANVAL_UPGRADE
        elif keuze == "verdediging":
            self.speler["verdediging"] += LEVEL_VERDEDIGING_UPGRADE
        else:
            raise ValueError(f"Onbekende upgrade: {keuze}")
        self.level_upgrades.append(keuze)

    def kies_level_upgrade(self, keuze):
        if not self.level_keuzes:
            return
        self.geef_level_upgrade(keuze)
        self.level_keuzes.pop(0)
        venster = self.level_keuze_venster
        self.level_keuze_venster = None
        if venster and venster.winfo_exists():
            venster.destroy()
        self.update_status()
        if self.level_keuzes:
            self.toon_level_keuze()
        elif not self.start_baasgevecht():
            self.update_acties()
            self.teken_scène()

    def verlies_level(self):
        if self.speler["level"] <= 1:
            return False
        verloren_level = self.speler["level"]
        self.speler["level"] -= 1
        self.speler["max_hp"] -= LEVEL_BASIS_HP
        if verloren_level in self.level_keuzes:
            self.level_keuzes.remove(verloren_level)
        elif verloren_level % LEVEL_UPGRADE_INTERVAL == 0 and self.level_upgrades:
            keuze = self.level_upgrades.pop()
            if keuze == "hp":
                self.speler["max_hp"] -= LEVEL_HP_UPGRADE
            elif keuze == "aanval":
                self.speler["aanval"] -= LEVEL_AANVAL_UPGRADE
            else:
                self.speler["verdediging"] -= LEVEL_VERDEDIGING_UPGRADE
        return True

    def verder_na_verlies(self):
        self.toon_spelscherm()
        self.log(
            f"Je bent hersteld op level {self.speler['level']} met "
            f"{NEDERLAAG_GOUD} goud. Bezoek de handelaar en word sterker."
        )
        if not self.start_baasgevecht():
            self.ververs_scherm()

    def stop_spel(self):
        if messagebox.askyesno("Avontuur stoppen", "Weet je zeker dat je wilt stoppen?"):
            self.muziek.stop()
            self.muziek_aan = False
            self.toon_startscherm()

    def start_muziek(self):
        try:
            self.muziek.start()
        except (OSError, RuntimeError) as fout:
            self.muziek_aan = False
            messagebox.showwarning(
                "Muziek niet beschikbaar",
                f"De achtergrondmuziek kon niet worden gestart:\n{fout}",
                parent=self.root,
            )
        if hasattr(self, "muziek_knop") and self.muziek_knop.winfo_exists():
            self.muziek_knop.configure(
                text=f"Muziek: {'aan' if self.muziek_aan else 'uit'}"
            )

    def schakel_muziek(self):
        if self.muziek_aan:
            self.muziek.stop()
            self.muziek_aan = False
        else:
            self.muziek_aan = True
            self.start_muziek()

    def sluit_spel(self):
        self.muziek.stop()
        self.root.destroy()


def main():
    root = tk.Tk()
    MiniRPG(root)
    root.mainloop()


if __name__ == "__main__":
    main()
