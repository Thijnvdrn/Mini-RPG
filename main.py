"""Een visuele RPG. Start het spel met: python main.py."""

import random
import tkinter as tk
from tkinter import messagebox, ttk
from visuals import landschap, personage, baas_balk


POTION_GENEZING_PERCENT = 50
POTION_PRIJS = 20
WAPEN_PRIJS = 80
WAPEN_VERBETERING = 3
XP_PER_LEVEL = 2
VIJAND_XP_MULTIPLIER = 2
VIJAND_HP_PER_LEVEL = 18
VIJAND_AANVAL_PER_LEVEL = 1
GEVECHT_KANS = 75
RUST_GENEZING = 8
BAAS_LEVEL = 30
BAAS_HP = 1700
BAAS_GENEZING = 16  # Na elke vijandelijke beurt.
EINDBAAS_LEVEL = 100
EINDBAAS_HP = 12_000
EINDBAAS_AANVAL = 105
EINDBAAS_GENEZING = 45
VERDEDIGING_PERCENT = 65
BAAS_WOEDE_MULTIPLIER = 2
EINDBAAS_WOEDE_MULTIPLIER = 3
NEDERLAAG_GOUD = 100
LEVEL_HP_UPGRADE = 20
LEVEL_AANVAL_UPGRADE = 3
LEVEL_VERDEDIGING_UPGRADE = 1

ACHTERGROND = "#0d171e"
PANEEL = "#17272e"
PANEEL_LICHT = "#263c43"
TEKST = "#edf3e8"
GEDIMD = "#a8b9b5"
GROEN = "#83c98a"
GOUD = "#f2c66d"
ROOD = "#ef7771"

KLASSEN = {
    "Krijger": {"hp": 120, "aanval": 18, "kritieke_kans": 10},
    "Magiër": {"hp": 80, "aanval": 25, "kritieke_kans": 10},
    "Sluipmoordenaar": {"hp": 95, "aanval": 16, "kritieke_kans": 40},
}


def xp_voor_level(level):
    return level * XP_PER_LEVEL


def wapen_prijs(speler):
    upgrades = speler["wapen_upgrades"]
    return WAPEN_PRIJS + upgrades * 35 + upgrades ** 2 * 15


def wapen_limiet(speler):
    return 1 + speler["level"] // 2


def maak_speler(naam, klasse):
    statistieken = KLASSEN[klasse]
    return {
        "naam": naam,
        "klasse": klasse,
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
        "eindbaas_verslagen": False,
        "wapen_upgrades": 0,
    }


def maak_vijand(speler_level):
    vijand_soort = random.choice(["Goblin", "Orc", "Draak"])
    statistieken = {
        "Goblin": {"hp": 40, "aanval": 8, "goud": 12, "xp": 20},
        "Orc": {"hp": 60, "aanval": 11, "goud": 20, "xp": 30},
        "Draak": {"hp": 90, "aanval": 15, "goud": 35, "xp": 45},
    }[vijand_soort]
    extra_levels = speler_level - 1
    hp = statistieken["hp"] + extra_levels * VIJAND_HP_PER_LEVEL + extra_levels ** 2 // 4
    return {
        "naam": vijand_soort,
        "beurten": 0,
        "hp": hp,
        "max_hp": hp,
        "aanval": statistieken["aanval"] + extra_levels * VIJAND_AANVAL_PER_LEVEL + extra_levels // 5,
        "goud": statistieken["goud"] + extra_levels * 2,
        "xp": (statistieken["xp"] + extra_levels * 5) * VIJAND_XP_MULTIPLIER,
    }


def maak_baas(speler_level):
    extra_levels = max(0, speler_level - BAAS_LEVEL)
    hp = BAAS_HP + extra_levels * 30
    return {
        "naam": "Nachtvorst", "hp": hp, "max_hp": hp,
        "aanval": 38 + extra_levels * 2, "goud": 500, "xp": 1200,
        "baas": True, "woedend": False, "beurten": 0,
        "genezing": BAAS_GENEZING, "woede_multiplier": BAAS_WOEDE_MULTIPLIER,
        "speciale_aanval": "Schaduwvuur",
    }


def maak_eindbaas():
    return {
        "naam": "Gouden Draak", "hp": EINDBAAS_HP, "max_hp": EINDBAAS_HP,
        "aanval": EINDBAAS_AANVAL, "goud": 10_000, "xp": 0,
        "baas": True, "eindbaas": True, "woedend": False, "beurten": 0,
        "genezing": EINDBAAS_GENEZING,
        "woede_multiplier": EINDBAAS_WOEDE_MULTIPLIER,
        "speciale_aanval": "Gouden vuur",
    }


class MiniRPG:
    def __init__(self, root):
        self.root = root
        self.root.title("Mini-RPG — De Wildernis")
        self.root.geometry("1100x820")
        self.root.minsize(900, 760)
        self.root.configure(bg=ACHTERGROND)
        self.speler = None
        self.vijand = None
        self.gevecht = False
        self.spel_uitgespeeld = False
        self.level_keuzes = []
        self.level_upgrades = []
        self.level_keuze_venster = None
        self.animaties = set()
        self.maak_stijl()
        self.toon_startscherm()

    def maak_stijl(self):
        stijl = ttk.Style()
        stijl.theme_use("clam")
        stijl.configure(
            "HP.Horizontal.TProgressbar",
            troughcolor="#34434a",
            background=GROEN,
            bordercolor="#34434a",
            lightcolor=GROEN,
            darkcolor=GROEN,
        )
        stijl.configure(
            "Enemy.Horizontal.TProgressbar",
            troughcolor="#34434a",
            background=ROOD,
            bordercolor="#34434a",
            lightcolor=ROOD,
            darkcolor=ROOD,
        )
        stijl.configure(
            "XP.Horizontal.TProgressbar", troughcolor=PANEEL_LICHT,
            background=GOUD, bordercolor=PANEEL, lightcolor=GOUD, darkcolor=GOUD,
        )
        stijl.configure("HP.Horizontal.TProgressbar", thickness=10)
        stijl.configure("Enemy.Horizontal.TProgressbar", thickness=10)
        stijl.configure("XP.Horizontal.TProgressbar", thickness=5)

    def wis_scherm(self):
        for taak in self.animaties:
            self.root.after_cancel(taak)
        self.animaties.clear()
        self.level_keuze_venster = None
        for widget in self.root.winfo_children():
            widget.destroy()

    def later(self, vertraging, actie):
        def uitvoeren():
            self.animaties.discard(taak)
            actie()
        taak = self.root.after(vertraging, uitvoeren)
        self.animaties.add(taak)
        return taak

    def label(self, ouder, tekst, grootte=12, kleur=TEKST, vet=False, **opties):
        return tk.Label(
            ouder,
            text=tekst,
            font=("Segoe UI", grootte, "bold" if vet else "normal"),
            bg=opties.pop("bg", ouder.cget("bg")),
            fg=kleur,
            **opties,
        )

    def knop(self, ouder, tekst, actie, kleur=PANEEL_LICHT, breedte=None):
        knop = tk.Button(
            ouder,
            text=tekst,
            command=actie,
            font=("Segoe UI", 11, "bold"),
            bg=kleur,
            fg=ACHTERGROND if kleur == GROEN else TEKST,
            activebackground=GROEN,
            activeforeground=ACHTERGROND,
            disabledforeground="#80908e",
            relief="flat",
            bd=0,
            padx=10,
            pady=11,
            cursor="hand2",
            width=breedte,
            highlightthickness=1,
            highlightbackground=kleur,
            highlightcolor=GOUD,
        )
        knop.bind("<Enter>", lambda _e: knop.configure(
            bg="#a0dab0" if kleur == GROEN else "#36515a"
        ) if knop.cget("state") != "disabled" else None)
        knop.bind("<Leave>", lambda _e: knop.configure(bg=kleur))
        return knop

    def toon_startscherm(self):
        self.wis_scherm()
        achtergrond = tk.Canvas(self.root, bg=ACHTERGROND, highlightthickness=0)
        achtergrond.place(relwidth=1, relheight=1)
        achtergrond.bind("<Configure>", lambda e: landschap(achtergrond, e.width, e.height))
        inhoud = tk.Frame(self.root, bg=ACHTERGROND)
        inhoud.place(relx=0.5, rely=0.5, anchor="center")

        self.label(inhoud, "EEN AVONTUUR IN DE SCHADUWEN", 9, GOUD, True).pack(pady=(20, 8))
        self.label(inhoud, "De Wildernis", 36, TEKST, True).pack(pady=(0, 4))
        self.label(inhoud, "Kies je held. Vind je pad. Schrijf je verhaal.", 12, GEDIMD).pack(
            pady=(0, 28)
        )

        kaart = tk.Frame(inhoud, bg=PANEEL, padx=30, pady=25,
                         highlightthickness=1, highlightbackground="#36504c")
        kaart.pack()
        self.label(kaart, "Hoe heet de avonturier?", 13, vet=True).pack(anchor="w")
        self.naam_invoer = tk.Entry(
            kaart,
            font=("Segoe UI", 13),
            bg=PANEEL_LICHT,
            fg=TEKST,
            insertbackground=TEKST,
            relief="flat",
            width=31,
        )
        self.naam_invoer.pack(fill="x", pady=(8, 20), ipady=8)
        self.naam_invoer.bind("<Return>", lambda _event: self.start_spel())

        self.label(kaart, "Kies je klasse", 13, vet=True).pack(anchor="w")
        self.klasse_keuze = tk.StringVar(value="Krijger")
        omschrijvingen = {
            "Krijger": "120 HP  ·  18 aanval  ·  stevig",
            "Magiër": "80 HP  ·  25 aanval  ·  krachtige spreuken",
            "Sluipmoordenaar": "95 HP  ·  16 aanval  ·  40% kritieke kans",
        }
        for klasse, omschrijving in omschrijvingen.items():
            rij = tk.Frame(kaart, bg=PANEEL)
            rij.pack(fill="x", pady=3)
            portret = tk.Canvas(rij, width=54, height=62, bg=PANEEL, highlightthickness=0)
            portret.pack(side="left", padx=(0, 8))
            personage(portret, 27, 57, klasse, .46)
            tk.Radiobutton(
                rij,
                text=klasse,
                variable=self.klasse_keuze,
                value=klasse,
                font=("Segoe UI", 11, "bold"),
                bg=PANEEL,
                fg=TEKST,
                activebackground=PANEEL,
                activeforeground=TEKST,
                selectcolor=PANEEL_LICHT,
                highlightthickness=0,
            ).pack(side="left")
            self.label(rij, omschrijving, 10, GEDIMD).pack(side="right", padx=8)

        self.knop(kaart, "Begin avontuur", self.start_spel, GROEN).pack(
            fill="x", pady=(22, 0)
        )
        self.label(inhoud, "Verken · Vecht · Word sterker", 10, GEDIMD).pack(pady=18)
        self.naam_invoer.focus_set()

    def start_spel(self):
        naam = self.naam_invoer.get().strip()
        if not naam:
            messagebox.showwarning("Naam ontbreekt", "Vul eerst de naam van je held in.")
            self.naam_invoer.focus_set()
            return
        self.speler = maak_speler(naam, self.klasse_keuze.get())
        self.spel_uitgespeeld = False
        self.level_keuzes = []
        self.level_upgrades = []
        if naam.casefold() == "baas":
            self.speler["level"] = BAAS_LEVEL - 1
            self.speler["goud"] = 10_000
            for index in range(BAAS_LEVEL - 2):
                keuze = ("hp", "aanval", "verdediging")[index % 3]
                self.level_upgrades.append(keuze)
                if keuze == "hp":
                    self.speler["max_hp"] += LEVEL_HP_UPGRADE
                    self.speler["hp"] += LEVEL_HP_UPGRADE
                elif keuze == "aanval":
                    self.speler["aanval"] += LEVEL_AANVAL_UPGRADE
                else:
                    self.speler["verdediging"] += LEVEL_VERDEDIGING_UPGRADE
        self.gevecht = False
        self.vijand = None
        self.toon_spelscherm()
        self.log(f"Welkom, {naam} de {self.speler['klasse']}! Je avontuur begint.")
        self.log("Elke derde vijandelijke beurt komt een zware aanval. Verdedig om 65% schade te blokkeren.")

    def toon_spelscherm(self):
        self.wis_scherm()
        header = tk.Frame(self.root, bg=ACHTERGROND, padx=24, pady=15)
        header.pack(fill="x")
        merk = tk.Frame(header, bg=ACHTERGROND)
        merk.pack(side="left")
        self.label(merk, "MINI-RPG  /  HOOFDSTUK I", 9, GOUD, True).pack(anchor="w")
        self.label(merk, "De Wildernis", 23, TEKST, True).pack(anchor="w")
        self.header_status = self.label(header, "", 11, GEDIMD)
        self.header_status.pack(side="right")

        hoofd = tk.Frame(self.root, bg=ACHTERGROND, padx=24)
        hoofd.pack(fill="both", expand=True)
        self.scène = tk.Canvas(
            hoofd, height=270, bg="#172936", highlightthickness=1,
            highlightbackground="#36504c"
        )
        self.scène.pack(fill="both", expand=True, pady=(0, 14))
        self.scène.bind("<Configure>", lambda _event: self.teken_scène())

        onder = tk.Frame(hoofd, bg=ACHTERGROND)
        onder.pack(fill="x", pady=(0, 20))
        links = tk.Frame(onder, bg=PANEEL, padx=18, pady=14)
        links.pack(side="left", fill="y", padx=(0, 14))
        rechts = tk.Frame(onder, bg=ACHTERGROND)
        rechts.pack(side="left", fill="both", expand=True)

        self.label(links, "HELD", 10, GOUD, True).pack(anchor="w")
        self.held_naam = self.label(links, "", 15, vet=True)
        self.held_naam.pack(anchor="w", pady=(4, 8))
        self.held_klasse = self.label(links, "", 10, GEDIMD)
        self.held_klasse.pack(anchor="w")
        self.hp_tekst = self.label(links, "", 10)
        self.hp_tekst.pack(anchor="w", pady=(16, 5))
        self.hp_balk = ttk.Progressbar(
            links, style="HP.Horizontal.TProgressbar", length=180, maximum=100
        )
        self.hp_balk.pack(fill="x")
        self.xp_tekst = self.label(links, "", 10, GEDIMD)
        self.xp_tekst.pack(anchor="w", pady=(12, 3))
        self.xp_balk = ttk.Progressbar(links, style="XP.Horizontal.TProgressbar", length=210)
        self.xp_balk.pack(fill="x", pady=(3, 0))
        self.statistieken = self.label(links, "", 10, GEDIMD, justify="left")
        self.statistieken.pack(anchor="w", pady=(8, 0))
        self.inventaris_tekst = self.label(links, "", 10, GEDIMD, justify="left")
        self.inventaris_tekst.pack(anchor="w", pady=(13, 0))

        self.vijand_frame = tk.Frame(rechts, bg=PANEEL, padx=14, pady=10)
        self.vijand_naam = self.label(self.vijand_frame, "", 11, ROOD, True)
        self.vijand_naam.pack(side="left")
        self.vijand_hp = self.label(self.vijand_frame, "", 10, GEDIMD)
        self.vijand_hp.pack(side="right")
        self.vijand_balk = ttk.Progressbar(
            self.vijand_frame,
            style="Enemy.Horizontal.TProgressbar",
            length=130,
            maximum=100,
        )
        self.vijand_balk.pack(side="right", padx=12, fill="x", expand=True)

        log_frame = tk.Frame(rechts, bg=PANEEL, padx=12, pady=9)
        log_frame.pack(fill="both", expand=True, pady=(8, 10))
        self.label(log_frame, "AVONTURENLOG", 9, GOUD, True).pack(anchor="w", pady=(0, 7))
        self.gebeurtenissen = tk.Text(
            log_frame,
            height=6,
            wrap="word",
            state="disabled",
            bg=PANEEL,
            fg=TEKST,
            font=("Segoe UI", 10),
            relief="flat",
            padx=3,
            pady=3,
            highlightthickness=0,
            spacing1=4,
            spacing3=4,
        )
        self.gebeurtenissen.tag_configure("beloning", foreground=GOUD)
        self.gebeurtenissen.tag_configure("schade", foreground=ROOD)
        self.gebeurtenissen.tag_configure("herstel", foreground=GROEN)
        self.vijand_frame.pack(fill="x")
        self.vijand_frame.pack_forget()
        self.gebeurtenissen.pack(fill="both", expand=True)

        self.acties = tk.Frame(rechts, bg=ACHTERGROND)
        self.acties.pack(fill="x")
        self.update_status()
        self.update_acties()
        self.teken_scène()

    def log(self, bericht):
        if not hasattr(self, "gebeurtenissen"):
            return
        self.gebeurtenissen.configure(state="normal")
        tag = ("beloning" if "Gewonnen" in bericht or "Level omhoog" in bericht
               else "herstel" if "herstelt" in bericht
               else "schade" if "schade" in bericht else "")
        self.gebeurtenissen.insert("end", "›  " + bericht + "\n", tag)
        self.gebeurtenissen.see("end")
        self.gebeurtenissen.configure(state="disabled")

    def update_status(self):
        speler = self.speler
        self.header_status.configure(
            text=f"✦  {speler['goud']} goud     ·     Level {speler['level']}"
        )
        self.held_naam.configure(text=speler["naam"])
        self.held_klasse.configure(text=speler["klasse"])
        self.hp_tekst.configure(text=f"LEVENSKRACHT   {speler['hp']} / {speler['max_hp']}")
        self.hp_balk.configure(
            maximum=speler["max_hp"], value=speler["hp"]
        )
        xp_nodig = xp_voor_level(speler["level"])
        self.xp_tekst.configure(text=f"ERVARING   {speler['xp']} / {xp_nodig} XP")
        self.xp_balk.configure(maximum=xp_nodig, value=speler["xp"])
        self.statistieken.configure(
            text=f"Aanval     {speler['aanval']}\n"
                 f"Verdediging  {speler['verdediging']}\n"
                 f"Kritiek     {speler['kritieke_kans']}%"
        )
        potions = speler["inventaris"].count("Health Potion")
        self.inventaris_tekst.configure(
            text=f"INVENTARIS\nHealth Potion  × {potions}"
        )

    def update_acties(self):
        for widget in self.acties.winfo_children():
            widget.destroy()
        if self.gevecht:
            self.knop(self.acties, "⚔  Aanvallen", self.val_aan, GROEN).pack(
                side="left", padx=(0, 7)
            )
            self.knop(self.acties, "Verdedig", self.verdedig).pack(side="left", padx=4)
            potion_knop = self.knop(
                self.acties,
                f"✚  Potion ({self.speler['inventaris'].count('Health Potion')})",
                self.gebruik_potion,
            )
            if (
                "Health Potion" not in self.speler["inventaris"]
                or self.speler["hp"] == self.speler["max_hp"]
            ):
                potion_knop.configure(state="disabled")
            potion_knop.pack(side="left", padx=7)
            vlucht_tekst = "↗  Vluchten (35%)" if self.vijand.get("baas") else "↗  Vluchten"
            self.knop(self.acties, vlucht_tekst, self.vlucht, PANEEL).pack(
                side="left", padx=7
            )
        else:
            self.knop(self.acties, "Verkennen", self.verken, GROEN).pack(
                side="left", padx=(0, 7))
            self.knop(self.acties, "Handelaar", self.bezoek_winkel).pack(
                side="left", padx=7
            )
            self.knop(self.acties, "Stoppen", self.stop_spel, PANEEL).pack(
                side="right"
            )

    def verken(self):
        if self.gevecht:
            return
        if self.start_baasgevecht():
            return
        if random.randint(1, 100) <= GEVECHT_KANS:
            self.vijand = maak_vijand(self.speler["level"])
            self.gevecht = True
            self.log(f"Een {self.vijand['naam']} verschijnt uit de wildernis!")
            self.update_acties()
        else:
            oude_hp = self.speler["hp"]
            self.speler["hp"] = min(self.speler["max_hp"], oude_hp + RUST_GENEZING)
            herstel = self.speler["hp"] - oude_hp
            self.log(f"Je vindt een rustige plek en herstelt {herstel} HP.")
        self.update_status()
        self.teken_scène()

    def start_baasgevecht(self):
        if self.gevecht or self.spel_uitgespeeld:
            return False
        if (self.speler["level"] >= EINDBAAS_LEVEL
                and not self.speler.get("eindbaas_verslagen", False)):
            self.vijand = maak_eindbaas()
            self.log("De Gouden Draak daalt neer! Dit is je laatste gevecht.")
            self.log(
                f"Gouden vuur elke derde beurt; bij halve HP wordt hij woedend "
                f"en doet {EINDBAAS_WOEDE_MULTIPLIER}× schade."
            )
        elif self.speler["level"] >= BAAS_LEVEL and not self.speler["baas_verslagen"]:
            self.vijand = maak_baas(self.speler["level"])
            self.log("Baasgevecht! De Nachtvorst daalt neer tussen de bomen.")
            self.log("Elke derde beurt: schaduwvuur! Bij halve HP wordt hij woedend: 2× schade.")
        else:
            return False
        self.gevecht = True
        self.log(
            f"De {self.vijand['naam']} geneest {self.vijand['genezing']} HP per beurt."
        )
        self.update_status()
        self.update_acties()
        self.teken_scène()
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
        self.toon_effect(f"{'KRITIEK! ' if kritiek else ''}−{schade}", .72, GOUD if kritiek else ROOD)

    def gebruik_potion(self):
        if not self.gevecht or not self.vijand:
            return
        if (
            "Health Potion" not in self.speler["inventaris"]
            or self.speler["hp"] == self.speler["max_hp"]
        ):
            return
        oude_hp = self.speler["hp"]
        genezing = self.speler["max_hp"] * POTION_GENEZING_PERCENT // 100
        self.speler["hp"] = min(
            self.speler["max_hp"], oude_hp + genezing
        )
        self.speler["inventaris"].remove("Health Potion")
        self.log(f"Je gebruikt een potion en herstelt {self.speler['hp'] - oude_hp} HP.")
        herstel = self.speler["hp"] - oude_hp
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
        if self.vijand["hp"] == 0:
            eindbaas_verslagen = self.vijand.get("eindbaas", False)
            if eindbaas_verslagen:
                self.speler["eindbaas_verslagen"] = True
                self.spel_uitgespeeld = True
            elif self.vijand.get("baas"):
                self.speler["baas_verslagen"] = True
                self.log("De Nachtvorst is verslagen! Het maanwoud is weer vrij.")
            self.speler["goud"] += self.vijand["goud"]
            self.speler["xp"] += self.vijand["xp"]
            self.log(
                f"Gewonnen! +{self.vijand['goud']} goud en +{self.vijand['xp']} XP."
            )
            self.gevecht = False
            self.vijand = None
            if eindbaas_verslagen:
                self.toon_eindscherm()
                return
            self.controleer_level()
            self.update_status()
            self.update_acties()
            self.teken_scène()
            return
        self.vijand_valt_aan()

    def verdedig(self):
        if not self.gevecht or not self.vijand:
            return
        self.log(f"Je verdedigt en blokkeert {VERDEDIGING_PERCENT}% van de schade.")
        self.vijand_valt_aan(verdedigd=True)

    def vijand_valt_aan(self, verdedigd=False):
        aanval = self.vijand["aanval"]
        self.vijand["beurten"] += 1
        if self.vijand.get("baas") and self.vijand["hp"] <= self.vijand["max_hp"] / 2:
            if not self.vijand["woedend"]:
                self.log(
                    f"De {self.vijand['naam']} wordt woedend! Zijn aanvallen doen "
                    f"{self.vijand['woede_multiplier']}× schade."
                )
            self.vijand["woedend"] = True
        speciale_aanval = self.vijand["beurten"] % 3 == 0
        if speciale_aanval:
            aanval = aanval * 3 // 2
        schade = random.randint(aanval - 2, aanval + 2)
        if self.vijand.get("woedend"):
            schade *= self.vijand.get("woede_multiplier", BAAS_WOEDE_MULTIPLIER)
        schade = max(1, schade - self.speler.get("verdediging", 0))
        if verdedigd:
            schade = max(1, schade * (100 - VERDEDIGING_PERCENT) // 100)
        self.speler["hp"] = max(0, self.speler["hp"] - schade)
        self.log(f"De {self.vijand['naam']} doet {schade} schade"
                 + (f" met {self.vijand.get('speciale_aanval', 'een zware aanval').lower()}!"
                    if speciale_aanval else "."))
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
            self.vijand["hp"] = min(
                self.vijand["max_hp"],
                self.vijand["hp"] + self.vijand.get("genezing", BAAS_GENEZING),
            )
        self.update_status()
        self.update_acties()
        self.teken_scène()
        self.toon_effect(f"−{schade}", .28, ROOD)

    def controleer_level(self):
        while (self.speler["level"] < EINDBAAS_LEVEL
               and self.speler["xp"] >= xp_voor_level(self.speler["level"])):
            self.speler["xp"] -= xp_voor_level(self.speler["level"])
            self.speler["level"] += 1
            self.level_keuzes.append(self.speler["level"])
            self.log(f"Level omhoog! Je bent nu level {self.speler['level']}. Kies een upgrade.")
        if self.level_keuzes:
            self.toon_level_keuze()
        else:
            self.start_baasgevecht()

    def toon_level_keuze(self):
        if not self.level_keuzes or self.level_keuze_venster:
            return
        level = self.level_keuzes[0]
        venster = tk.Toplevel(self.root)
        self.level_keuze_venster = venster
        venster.title("Level omhoog!")
        venster.configure(bg=PANEEL)
        venster.resizable(False, False)
        venster.transient(self.root)
        venster.grab_set()
        inhoud = tk.Frame(venster, bg=PANEEL, padx=24, pady=22)
        inhoud.pack(fill="both", expand=True)
        self.label(inhoud, f"LEVEL {level}", 10, GOUD, True).pack(anchor="w")
        self.label(inhoud, "Kies je upgrade", 21, vet=True).pack(anchor="w", pady=(4, 8))
        self.label(inhoud, "Deze bonus geldt meteen en blijft bij je volgende levels.",
                   10, GEDIMD).pack(anchor="w", pady=(0, 14))
        keuzes = [
            ("Levenskracht", f"+{LEVEL_HP_UPGRADE} Max HP en HP", "hp"),
            ("Aanval", f"+{LEVEL_AANVAL_UPGRADE} aanval", "aanval"),
            ("Verdediging", f"+{LEVEL_VERDEDIGING_UPGRADE} verdediging per treffer", "verdediging"),
        ]
        for naam, bonus, keuze in keuzes:
            self.knop(
                inhoud, f"{naam}  ·  {bonus}",
                lambda geselecteerd=keuze: self.kies_level_upgrade(geselecteerd),
                PANEEL_LICHT,
            ).pack(fill="x", pady=4)
        venster.protocol("WM_DELETE_WINDOW", lambda: None)
        venster.update_idletasks()
        x = self.root.winfo_rootx() + (self.root.winfo_width()-venster.winfo_width())//2
        y = self.root.winfo_rooty() + (self.root.winfo_height()-venster.winfo_height())//2
        venster.geometry(f"+{max(0, x)}+{max(0, y)}")

    def kies_level_upgrade(self, keuze):
        if not self.level_keuzes:
            return
        self.level_keuzes.pop(0)
        if keuze == "hp":
            self.speler["max_hp"] += LEVEL_HP_UPGRADE
            self.speler["hp"] = min(
                self.speler["max_hp"], self.speler["hp"] + LEVEL_HP_UPGRADE
            )
        elif keuze == "aanval":
            self.speler["aanval"] += LEVEL_AANVAL_UPGRADE
        else:
            self.speler["verdediging"] += LEVEL_VERDEDIGING_UPGRADE
        self.level_upgrades.append(keuze)
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
        self.speler["level"] -= 1
        if self.level_upgrades:
            keuze = self.level_upgrades.pop()
            if keuze == "hp":
                self.speler["max_hp"] -= LEVEL_HP_UPGRADE
            elif keuze == "aanval":
                self.speler["aanval"] -= LEVEL_AANVAL_UPGRADE
            else:
                self.speler["verdediging"] -= LEVEL_VERDEDIGING_UPGRADE
        return True

    def toon_verliespagina(self, verloren_goud, verloren_level):
        self.wis_scherm()
        achtergrond = tk.Canvas(self.root, bg=ACHTERGROND, highlightthickness=0)
        achtergrond.place(relwidth=1, relheight=1)
        achtergrond.bind("<Configure>", lambda e: landschap(achtergrond, e.width, e.height))
        kaart = tk.Frame(self.root, bg=PANEEL, padx=40, pady=34,
                         highlightthickness=1, highlightbackground="#72504c")
        kaart.place(relx=0.5, rely=0.5, anchor="center")
        self.label(kaart, "JE HEBT VERLOREN", 25, ROOD, True).pack(pady=(0, 12))
        if verloren_level:
            self.label(kaart, "Je verliest een level en de bijbehorende upgrade.", 12).pack()
        else:
            self.label(kaart, "Je bent op level 1 gebleven.", 12).pack()
        self.label(
            kaart,
            f"Je verloren goud: {verloren_goud}  ·  Herstelgeld: {NEDERLAAG_GOUD}",
            11, GOUD,
        ).pack(pady=(8, 18))
        self.knop(kaart, "Verder naar het woud", self.verder_na_verlies, GROEN).pack(fill="x")

    def verder_na_verlies(self):
        self.toon_spelscherm()
        self.log(
            f"Je bent hersteld op level {self.speler['level']} met "
            f"{NEDERLAAG_GOUD} goud. Bezoek de handelaar en word sterker."
        )
        if not self.start_baasgevecht():
            self.update_status()
            self.update_acties()
            self.teken_scène()

    def toon_eindscherm(self):
        messagebox.showinfo(
            "👑 Je hebt het spel uitgespeeld!",
            f"Gefeliciteerd, {self.speler['naam']}! Je hebt de Gouden Draak verslagen "
            "en het spel uitgespeeld.\n\nBedankt voor het spelen! 👑",
            parent=self.root,
        )
        self.wis_scherm()
        achtergrond = tk.Canvas(self.root, bg=ACHTERGROND, highlightthickness=0)
        achtergrond.place(relwidth=1, relheight=1)
        achtergrond.bind("<Configure>", lambda e: landschap(achtergrond, e.width, e.height))
        kaart = tk.Frame(self.root, bg=PANEEL, padx=42, pady=36,
                         highlightthickness=1, highlightbackground=GOUD)
        kaart.place(relx=0.5, rely=0.5, anchor="center")
        self.label(kaart, "👑", 42, GOUD, True).pack(pady=(0, 8))
        self.label(kaart, "SPEL UITGESPEELD!", 24, GOUD, True).pack()
        self.label(kaart, "Je hebt de Gouden Draak verslagen.", 13).pack(pady=(8, 4))
        self.label(kaart, "Bedankt voor het spelen!", 13, GEDIMD).pack(pady=(0, 20))
        self.knop(kaart, "Terug naar het beginscherm", self.toon_startscherm, GROEN).pack(fill="x")

    def bezoek_winkel(self):
        if self.gevecht:
            return
        winkel = tk.Toplevel(self.root)
        winkel.title("Winkel")
        winkel.configure(bg=PANEEL)
        winkel.resizable(False, False)
        winkel.transient(self.root)
        winkel.grab_set()
        inhoud = tk.Frame(winkel, bg=PANEEL, padx=22, pady=20)
        inhoud.pack(fill="both", expand=True)
        self.label(inhoud, "DE HANDELAAR", 9, GOUD, True).pack(anchor="w")
        self.label(inhoud, "Klaar voor de volgende tocht?", 20, vet=True).pack(anchor="w", pady=(5, 14))
        goud_label = self.label(inhoud, "", 12, GOUD, True)
        goud_label.pack(anchor="w", pady=(0, 14))

        def update_goud():
            goud_label.configure(text=f"Je hebt {self.speler['goud']} goud")
            upgrade_knop.configure(
                text=f"Wapen +{WAPEN_VERBETERING} / {wapen_prijs(self.speler)} goud "
                     f"({self.speler['wapen_upgrades']}/{wapen_limiet(self.speler)})",
                state="normal" if self.speler["wapen_upgrades"] < wapen_limiet(self.speler) else "disabled",
            )

        def koop_potion():
            if self.speler["goud"] < POTION_PRIJS:
                messagebox.showinfo("Winkel", "Je hebt niet genoeg goud.", parent=winkel)
                return
            self.speler["goud"] -= POTION_PRIJS
            self.speler["inventaris"].append("Health Potion")
            self.log("Je koopt een Health Potion.")
            update_goud()
            self.update_status()
            self.update_acties()

        def upgrade_wapen():
            if self.speler["wapen_upgrades"] >= wapen_limiet(self.speler):
                messagebox.showinfo("Winkel", "Bereik een hoger level voor meer upgrades.", parent=winkel)
                return
            prijs = wapen_prijs(self.speler)
            if self.speler["goud"] < prijs:
                messagebox.showinfo("Winkel", "Je hebt niet genoeg goud.", parent=winkel)
                return
            self.speler["goud"] -= prijs
            self.speler["wapen_upgrades"] += 1
            self.speler["aanval"] += WAPEN_VERBETERING
            self.log(f"Je wapen is verbeterd met +{WAPEN_VERBETERING} aanval.")
            update_goud()
            self.update_status()

        self.label(inhoud, "Elke twee levels komt een extra wapen-upgrade vrij.", 10, GEDIMD).pack(anchor="w", pady=(0, 8))
        self.knop(
            inhoud,
            f"Health Potion  (+{POTION_GENEZING_PERCENT}% van Max HP)  ·  {POTION_PRIJS} goud",
            koop_potion,
        ).pack(fill="x", pady=4)
        upgrade_knop = self.knop(
            inhoud,
            f"Wapen-upgrade  (+{WAPEN_VERBETERING} aanval)  ·  {WAPEN_PRIJS} goud",
            upgrade_wapen,
        )
        upgrade_knop.pack(fill="x", pady=4)
        update_goud()
        self.knop(inhoud, "Terug naar avontuur", winkel.destroy, PANEEL_LICHT).pack(
            fill="x", pady=(14, 0)
        )
        winkel.update_idletasks()
        x = self.root.winfo_rootx() + (self.root.winfo_width()-winkel.winfo_width())//2
        y = self.root.winfo_rooty() + (self.root.winfo_height()-winkel.winfo_height())//2
        winkel.geometry(f"+{max(0, x)}+{max(0, y)}")

    def stop_spel(self):
        if messagebox.askyesno("Avontuur stoppen", "Weet je zeker dat je wilt stoppen?"):
            self.toon_startscherm()

    def toon_effect(self, tekst, positie, kleur):
        canvas = getattr(self, "scène", None)
        if canvas is None or not canvas.winfo_exists():
            return
        x = canvas.winfo_width() * positie
        y = canvas.winfo_height() * .77 - 125
        item = canvas.create_text(x, y, text=tekst, fill=kleur,
                                  font=("Segoe UI", 18, "bold"), tags="effect")

        def stap(frame=0):
            if not canvas.winfo_exists() or not canvas.find_withtag(item):
                return
            if frame >= 24:
                canvas.delete(item)
                return
            canvas.move(item, 0, -1.3)
            self.later(35, lambda: stap(frame + 1))
        stap()

    def teken_scène(self):
        if not hasattr(self, "scène") or not self.scène.winfo_exists():
            return
        canvas = self.scène
        canvas.delete("all")
        breedte = max(canvas.winfo_width(), 500)
        hoogte = max(canvas.winfo_height(), 250)
        landschap(canvas, breedte, hoogte)
        baasgevecht = self.gevecht and self.vijand and self.vijand.get("baas")
        if not baasgevecht:
            canvas.create_rectangle(18, 16, 265, 73, fill="#13262d", outline="#36504c")
            canvas.create_text(32, 32, text="DE WILDERNIS  /  MAANWOUD", anchor="w",
                               fill=GOUD, font=("Segoe UI", 9, "bold"))
            canvas.create_text(32, 54, text="Een vijand blokkeert je pad" if self.gevecht
                               else "Verken het woud voor een nieuw avontuur", anchor="w",
                               fill=TEKST, font=("Segoe UI", 10))
        grond = hoogte * .84
        schaal = min(1.3, hoogte / 300)
        held_x = breedte * .28
        personage(canvas, held_x, grond, self.speler["klasse"], schaal)
        canvas.create_text(held_x, grond + 24, text=self.speler["naam"],
                           fill=TEKST, font=("Segoe UI", 11, "bold"))
        if self.gevecht and self.vijand:
            vijand_x = breedte * .72
            vijand_schaal = min(schaal * 1.35, (grond - 114) / 138) if baasgevecht else schaal
            personage(canvas, vijand_x, grond, self.vijand["naam"], vijand_schaal)
            canvas.create_text(vijand_x, grond + 24, text=self.vijand["naam"],
                               fill="#efb2a0", font=("Segoe UI", 11, "bold"))
            canvas.create_text(breedte*.5, grond-45, text="VS", fill=GOUD,
                               font=("Segoe UI", 13, "bold"))
            if baasgevecht:
                self.vijand_frame.pack_forget()
                volgende = (self.vijand["beurten"] + 1) % 3 == 0
                baas_balk(
                    canvas, breedte, self.vijand, volgende,
                    self.vijand.get("genezing", BAAS_GENEZING),
                )
            else:
                self.vijand_frame.pack(fill="x", before=self.gebeurtenissen.master)
            self.vijand_balk.configure(maximum=self.vijand["max_hp"], value=self.vijand["hp"])
            volgende = (self.vijand["beurten"] + 1) % 3 == 0
            self.vijand_naam.configure(text=self.vijand["naam"].upper() +
                                      (" / ZWARE AANVAL!" if volgende else " / Normale aanval"))
            self.vijand_hp.configure(text=f"{self.vijand['hp']} / {self.vijand['max_hp']} HP")
        else:
            self.vijand_frame.pack_forget()
            volgende_baas = (
                f"De Gouden Draak verschijnt op level {EINDBAAS_LEVEL}"
                if self.speler["baas_verslagen"]
                else f"De Nachtvorst verschijnt op level {BAAS_LEVEL}"
            )
            canvas.create_text(breedte*.5, hoogte-16,
                               text=f"Klik op Verkennen / {volgende_baas}",
                               fill=TEKST, font=("Segoe UI", 10))


def main():
    root = tk.Tk()
    MiniRPG(root)
    root.mainloop()


if __name__ == "__main__":
    main()
