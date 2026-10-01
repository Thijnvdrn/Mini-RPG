"""Een visuele RPG. Start het spel met: python main.py."""

import random
import tkinter as tk
from tkinter import messagebox, ttk
from visuals import landschap, personage, baas_balk


POTION_GENEZING_PERCENT = 50
POTION_PRIJS = 20
WAPEN_PRIJS = 45
WAPEN_VERBETERING = 5
XP_PER_LEVEL = 80
HP_PER_LEVEL = 12
AANVAL_PER_LEVEL = 3
VIJAND_HP_PER_LEVEL = 12
VIJAND_AANVAL_PER_LEVEL = 2
GEVECHT_KANS = 75
RUST_GENEZING = 8
BAAS_LEVEL = 20
BAAS_HP = 5000
BAAS_GENEZING = 100  # Per seconde tijdens het gevecht.

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


def maak_speler(naam, klasse):
    statistieken = KLASSEN[klasse]
    return {
        "naam": naam,
        "klasse": klasse,
        "hp": statistieken["hp"],
        "max_hp": statistieken["hp"],
        "aanval": statistieken["aanval"],
        "kritieke_kans": statistieken["kritieke_kans"],
        "goud": 20,
        "xp": 0,
        "level": 1,
        "inventaris": ["Health Potion", "Health Potion"],
        "baas_verslagen": False,
    }


def maak_vijand(speler_level):
    vijand_soort = random.choice(["Goblin", "Orc", "Draak"])
    statistieken = {
        "Goblin": {"hp": 40, "aanval": 8, "goud": 12, "xp": 20},
        "Orc": {"hp": 60, "aanval": 11, "goud": 20, "xp": 30},
        "Draak": {"hp": 90, "aanval": 15, "goud": 35, "xp": 45},
    }[vijand_soort]
    extra_levels = speler_level - 1
    return {
        "naam": vijand_soort,
        "hp": statistieken["hp"] + extra_levels * VIJAND_HP_PER_LEVEL,
        "max_hp": statistieken["hp"] + extra_levels * VIJAND_HP_PER_LEVEL,
        "aanval": statistieken["aanval"] + extra_levels * VIJAND_AANVAL_PER_LEVEL,
        "goud": statistieken["goud"] + extra_levels * 5,
        "xp": statistieken["xp"] + extra_levels * 5,
    }


def maak_baas(speler_level):
    extra_levels = max(0, speler_level - BAAS_LEVEL)
    hp = BAAS_HP + extra_levels * 30
    return {
        "naam": "Nachtvorst", "hp": hp, "max_hp": hp,
        "aanval": 48 + extra_levels * 3, "goud": 500, "xp": 1200,
        "baas": True, "woedend": False, "beurten": 0,
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
        self.animaties = set()
        self.baas_genezing = None
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
        self.stop_baasgenezing()
        for taak in self.animaties:
            self.root.after_cancel(taak)
        self.animaties.clear()
        for widget in self.root.winfo_children():
            widget.destroy()

    def later(self, vertraging, actie):
        def uitvoeren():
            self.animaties.discard(taak)
            actie()
        taak = self.root.after(vertraging, uitvoeren)
        self.animaties.add(taak)
        return taak

    def stop_baasgenezing(self):
        if self.baas_genezing is not None:
            self.root.after_cancel(self.baas_genezing)
            self.animaties.discard(self.baas_genezing)
            self.baas_genezing = None

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
            padx=16,
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
        self.gevecht = False
        self.vijand = None
        self.toon_spelscherm()
        self.log(f"Welkom, {naam} de {self.speler['klasse']}! Je avontuur begint.")

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
        xp_nodig = speler["level"] * XP_PER_LEVEL
        self.xp_tekst.configure(text=f"ERVARING   {speler['xp']} / {xp_nodig} XP")
        self.xp_balk.configure(maximum=xp_nodig, value=speler["xp"])
        self.statistieken.configure(
            text=f"Aanval     {speler['aanval']}\nKritiek     {speler['kritieke_kans']}%"
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
            self.knop(self.acties, "Verken het bos  →", self.verken, GROEN).pack(
                side="left", padx=(0, 7)
            )
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
        if (self.gevecht or self.speler["level"] < BAAS_LEVEL
                or self.speler["baas_verslagen"]):
            return False
        self.vijand = maak_baas(self.speler["level"])
        self.gevecht = True
        self.log("Baasgevecht! De Nachtvorst daalt neer tussen de bomen.")
        self.log("Elke derde beurt: schaduwvuur! Onder halve HP wordt hij woedend.")
        self.log(f"De Nachtvorst geneest {BAAS_GENEZING} HP per seconde.")
        vijand = self.vijand

        def genees():
            self.baas_genezing = None
            if not self.gevecht or self.vijand is not vijand or vijand["hp"] <= 0:
                return
            vijand["hp"] = min(vijand["max_hp"], vijand["hp"] + BAAS_GENEZING)
            self.teken_scène()
            self.baas_genezing = self.later(1000, genees)

        self.baas_genezing = self.later(1000, genees)
        self.update_status()
        self.update_acties()
        self.teken_scène()
        return True

    def val_aan(self):
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
        vlucht_kans = 35 if self.vijand.get("baas") else 60
        if random.randint(1, 100) <= vlucht_kans:
            self.stop_baasgenezing()
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
            self.stop_baasgenezing()
            if self.vijand.get("baas"):
                self.speler["baas_verslagen"] = True
                self.log("De Nachtvorst is verslagen! Het maanwoud is weer vrij.")
            self.speler["goud"] += self.vijand["goud"]
            self.speler["xp"] += self.vijand["xp"]
            self.log(
                f"Gewonnen! +{self.vijand['goud']} goud en +{self.vijand['xp']} XP."
            )
            self.gevecht = False
            self.vijand = None
            self.controleer_level()
            self.update_status()
            self.update_acties()
            self.teken_scène()
            return
        self.vijand_valt_aan()

    def vijand_valt_aan(self):
        aanval = self.vijand["aanval"]
        schaduwvuur = False
        if self.vijand.get("baas"):
            self.vijand["beurten"] += 1
            if self.vijand["hp"] <= self.vijand["max_hp"] / 2:
                if not self.vijand["woedend"]:
                    self.log("De Nachtvorst wordt woedend! Zijn aanval stijgt met 12.")
                self.vijand["woedend"] = True
                aanval += 12
            schaduwvuur = self.vijand["beurten"] % 3 == 0
            if schaduwvuur:
                aanval = aanval * 3 // 2
        schade = random.randint(aanval - 2, aanval + 2)
        self.speler["hp"] = max(0, self.speler["hp"] - schade)
        self.log(f"De {self.vijand['naam']} doet {schade} schade"
                 + (" met schaduwvuur!" if schaduwvuur else "."))
        self.update_status()
        self.update_acties()
        self.teken_scène()
        self.toon_effect(f"−{schade}", .28, ROOD)
        if self.speler["hp"] == 0:
            self.stop_baasgenezing()
            self.gevecht = False
            self.update_acties()
            messagebox.showinfo(
                "Game over",
                f"{self.speler['naam']} is verslagen op level {self.speler['level']}.",
            )
            self.toon_startscherm()

    def controleer_level(self):
        while self.speler["xp"] >= self.speler["level"] * XP_PER_LEVEL:
            self.speler["xp"] -= self.speler["level"] * XP_PER_LEVEL
            self.speler["level"] += 1
            self.speler["max_hp"] += HP_PER_LEVEL
            self.speler["aanval"] += AANVAL_PER_LEVEL
            self.log(
                f"Level omhoog! Level {self.speler['level']}: +{HP_PER_LEVEL} Max HP, "
                f"+{AANVAL_PER_LEVEL} aanval."
            )
        self.start_baasgevecht()

    def bezoek_winkel(self):
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
            if self.speler["goud"] < WAPEN_PRIJS:
                messagebox.showinfo("Winkel", "Je hebt niet genoeg goud.", parent=winkel)
                return
            self.speler["goud"] -= WAPEN_PRIJS
            self.speler["aanval"] += WAPEN_VERBETERING
            self.log("Je wapen is verbeterd met +5 aanval.")
            update_goud()
            self.update_status()

        update_goud()
        self.knop(
            inhoud,
            f"Health Potion  (+{POTION_GENEZING_PERCENT}% van Max HP)  ·  {POTION_PRIJS} goud",
            koop_potion,
        ).pack(fill="x", pady=4)
        self.knop(
            inhoud,
            f"Wapen-upgrade  (+{WAPEN_VERBETERING} aanval)  ·  {WAPEN_PRIJS} goud",
            upgrade_wapen,
        ).pack(fill="x", pady=4)
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
                               else "Volg het pad naar een nieuw avontuur", anchor="w",
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
                baas_balk(canvas, breedte, self.vijand, volgende, BAAS_GENEZING)
            else:
                self.vijand_frame.pack(fill="x", before=self.gebeurtenissen.master)
            self.vijand_balk.configure(maximum=self.vijand["max_hp"], value=self.vijand["hp"])
            self.vijand_naam.configure(text=self.vijand["naam"].upper())
            self.vijand_hp.configure(text=f"{self.vijand['hp']} / {self.vijand['max_hp']} HP")
        else:
            self.vijand_frame.pack_forget()
            canvas.create_text(breedte*.69, grond-30, text="Het onbekende wacht...",
                               fill="#a4b8a3", font=("Segoe UI", 12, "italic"))


def main():
    root = tk.Tk()
    MiniRPG(root)
    root.mainloop()


if __name__ == "__main__":
    main()
