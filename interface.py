"""Vensters, knoppen en Canvas-weergave van Mini-RPG.

SpelInterface gebruikt de speler, vijand en acties van MiniRPG.
De spelregels staan in main.py; afbeeldingen worden geladen door visuals.py.
"""

import tkinter as tk
from tkinter import messagebox, ttk

from instellingen import (
    POTION_GENEZING_PERCENT, POTION_PRIJS, WAPEN_PRIJS, WAPEN_VERBETERING, BAAS_LEVEL,
    BAAS_GENEZING, NEDERLAAG_GOUD, LEVEL_HP_UPGRADE, LEVEL_AANVAL_UPGRADE,
    LEVEL_VERDEDIGING_UPGRADE, EINDBAAS_LEVEL, ACHTERGROND, PANEEL, PANEEL_LICHT, TEKST,
    GEDIMD, GROEN, GOUD, ROOD, KLASSEN, xp_voor_level, wapen_prijs, wapen_limiet,
)
from visuals import landschap, personage, baas_balk


class SpelInterface:
    """De weergavemethoden die MiniRPG overneemt."""

    def maak_stijl(self):
        stijl = ttk.Style()
        stijl.theme_use("clam")
        for naam, kleur, achtergrond, rand, dikte in (
            ("HP", GROEN, "#34434a", "#34434a", 10),
            ("Enemy", ROOD, "#34434a", "#34434a", 10),
            ("XP", GOUD, PANEEL_LICHT, PANEEL, 5),
        ):
            stijl.configure(
                f"{naam}.Horizontal.TProgressbar", troughcolor=achtergrond,
                background=kleur, bordercolor=rand, lightcolor=kleur,
                darkcolor=kleur, thickness=dikte,
            )

    def ververs_scherm(self):
        """Werk de statistieken, actieknoppen en scène samen bij."""
        self.update_status()
        self.update_acties()
        self.teken_scène()

    def toon_achtergrond(self):
        """Begin een nieuw scherm met het maanwoud over het hele venster."""
        self.wis_scherm()
        achtergrond = tk.Canvas(self.root, bg=ACHTERGROND, highlightthickness=0)
        achtergrond.place(relwidth=1, relheight=1)
        achtergrond.bind("<Configure>", lambda e: landschap(achtergrond, e.width, e.height))

    def maak_popup(self, titel, padx=24, pady=22):
        """Maak een dialoog met dezelfde stijl en modaliteit."""
        venster = tk.Toplevel(self.root)
        venster.title(titel)
        venster.configure(bg=PANEEL)
        venster.resizable(False, False)
        venster.transient(self.root)
        venster.grab_set()
        inhoud = tk.Frame(venster, bg=PANEEL, padx=padx, pady=pady)
        inhoud.pack(fill="both", expand=True)
        return venster, inhoud

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

    def centreer_venster(self, venster):
        venster.update_idletasks()
        x = self.root.winfo_rootx() + (self.root.winfo_width() - venster.winfo_width()) // 2
        y = self.root.winfo_rooty() + (self.root.winfo_height() - venster.winfo_height()) // 2
        venster.geometry(f"+{max(0, x)}+{max(0, y)}")

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
        self.toon_achtergrond()
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
        for klasse, statistieken in KLASSEN.items():
            omschrijving = (
                f"{statistieken['hp']} HP  ·  {statistieken['aanval']} aanval  ·  "
                f"{statistieken['kritieke_kans']}% kritieke kans"
            )
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
        self.ververs_scherm()

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
        self.xp_tekst.configure(text="VOLGEND LEVEL   Versla één vijand")
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
            if not self.kan_potion_gebruiken():
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

    def toon_level_keuze(self):
        if not self.level_keuzes or self.level_keuze_venster:
            return
        level = self.level_keuzes[0]
        venster, inhoud = self.maak_popup("Level omhoog!")
        self.level_keuze_venster = venster
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
        self.centreer_venster(venster)

    def toon_overwinningspagina(self):
        self.toon_achtergrond()
        kaart = tk.Frame(self.root, bg=PANEEL, padx=40, pady=34,
                         highlightthickness=2, highlightbackground=GOUD)
        kaart.place(relx=0.5, rely=0.5, anchor="center")
        self.label(kaart, "JE HEBT HET SPEL UITGESPEELD!", 23, GOUD, True).pack(pady=(0, 12))
        self.label(kaart, "De Gouden Draak is verslagen. De Wildernis is gered!", 12).pack()
        self.label(kaart, f"{self.speler['naam']} · Level {self.speler['level']} · "
                   f"{self.speler['goud']} goud", 12, GROEN).pack(pady=(12, 22))
        self.knop(kaart, "Nieuw avontuur", self.toon_startscherm, GROEN).pack(fill="x")
        self.knop(kaart, "Afsluiten", self.root.destroy).pack(fill="x", pady=(8, 0))

    def toon_verliespagina(self, verloren_goud, verloren_level):
        self.toon_achtergrond()
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

    def bezoek_winkel(self):
        if self.gevecht:
            return
        winkel, inhoud = self.maak_popup("Winkel", padx=22, pady=20)
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

        def koop_potions(aantal):
            prijs = aantal * POTION_PRIJS
            if self.speler["goud"] < prijs:
                messagebox.showinfo("Winkel", "Je hebt niet genoeg goud.", parent=winkel)
                return
            self.speler["goud"] -= prijs
            self.speler["inventaris"].extend(["Health Potion"] * aantal)
            if aantal == 1:
                self.log("Je koopt een Health Potion.")
            else:
                self.log(f"Je koopt {aantal} Health Potions.")
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
        for aantal in (1, 10, 100):
            tekst = (
                f"Health Potion  (+{POTION_GENEZING_PERCENT}% van Max HP)  ·  {POTION_PRIJS} goud"
                if aantal == 1 else f"{aantal}x Health Potion  ·  {aantal * POTION_PRIJS} goud"
            )
            self.knop(
                inhoud, tekst, lambda n=aantal: koop_potions(n),
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
        self.centreer_venster(winkel)

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
            canvas.create_text(breedte*.5, hoogte-16,
                               text=f"Klik op Verkennen / Nachtvorst: level {BAAS_LEVEL} / Gouden Draak: level {EINDBAAS_LEVEL}",
                               fill=TEKST, font=("Segoe UI", 10))
