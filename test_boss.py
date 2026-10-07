"""Regressiechecks voor de levelovergang en het baasgevecht."""

import tkinter as tk
import unittest
from unittest.mock import Mock, patch

from main import (MiniRPG, maak_vijand, maak_speler, xp_voor_level, wapen_prijs, wapen_limiet,
                  BAAS_LEVEL, BAAS_HP, BAAS_GENEZING, LEVEL_HP_UPGRADE,
                  LEVEL_AANVAL_UPGRADE, LEVEL_VERDEDIGING_UPGRADE,
                  WAPEN_VERBETERING, KLASSEN, NEDERLAAG_GOUD, LEVEL_BASIS_HP,
                  LEVEL_BASIS_AANVAL, EINDBAAS_LEVEL, EINDBAAS_HP,
                  EINDBAAS_AANVAL, EINDBAAS_GENEZING, POTION_PRIJS)


class BaasgevechtTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.app = MiniRPG(self.root)
        self.app.naam_invoer.insert(0, "Testheld")
        self.app.start_spel()
        self.app.speler.update(level=BAAS_LEVEL-1, hp=390, max_hp=390, aanval=72, xp=0)

    def tearDown(self):
        self.app.wis_scherm()
        self.root.update_idletasks()
        self.root.destroy()

    def start_baas(self):
        self.app.speler["level"] = BAAS_LEVEL
        self.app.start_baasgevecht()

    def kies_level(self, naam):
        venster = self.app.level_keuze_venster
        knop = next(
            widget for widget in venster.winfo_children()[0].winfo_children()
            if isinstance(widget, tk.Button) and widget.cget("text").startswith(naam)
        )
        knop.invoke()

    def test_naam_baas_start_op_level_99_met_10_miljoen_goud(self):
        self.app.wis_scherm()
        self.app.toon_startscherm()
        self.app.naam_invoer.insert(0, "Baas")
        self.app.start_spel()
        self.assertEqual(self.app.speler["level"], EINDBAAS_LEVEL-1)
        self.assertEqual(self.app.speler["goud"], 10_000_000)
        self.assertEqual(self.app.speler["hp"], self.app.speler["max_hp"])
        self.assertEqual(self.app.speler["max_hp"], KLASSEN["Krijger"]["hp"] + 98 * LEVEL_BASIS_HP + 33 * LEVEL_HP_UPGRADE)
        self.assertEqual(self.app.speler["aanval"], KLASSEN["Krijger"]["aanval"] + 98 * LEVEL_BASIS_AANVAL + 33 * LEVEL_AANVAL_UPGRADE)
        self.assertEqual(self.app.speler["verdediging"], 32 * LEVEL_VERDEDIGING_UPGRADE)

    def test_overwinning_bij_levelgrens_start_baas_direct(self):
        self.app.vijand = maak_vijand(19)
        self.app.vijand.update(hp=0, xp=1)
        self.app.gevecht = True
        self.app.verwerk_beurt()
        self.kies_level("Aanval")
        self.assertEqual(self.app.speler["level"], BAAS_LEVEL)
        self.assertEqual(self.app.speler["hp"], 390 + LEVEL_BASIS_HP)
        self.assertEqual(self.app.speler["max_hp"], 390 + LEVEL_BASIS_HP)
        self.assertEqual(self.app.speler["aanval"], 72 + LEVEL_BASIS_AANVAL + LEVEL_AANVAL_UPGRADE)
        self.assertTrue(self.app.gevecht)
        self.assertTrue(self.app.vijand["baas"])
        self.assertEqual(self.app.vijand["hp"], BAAS_HP)

    def test_onder_baaslevel_heeft_geen_baas(self):
        with patch("main.random.randint", return_value=1):
            self.app.verken()
        self.assertFalse(self.app.vijand.get("baas", False))

    def test_beurten_buiten_gevecht_veranderen_niets(self):
        speler = self.app.speler.copy()
        with patch("main.random.randint") as worp:
            self.app.verwerk_beurt()
            self.app.vijand_valt_aan()
        worp.assert_not_called()
        self.assertEqual(self.app.speler, speler)
        self.assertIsNone(self.app.vijand)
        self.assertFalse(self.app.gevecht)

    def test_meerdere_xp_zonder_upgradekeuze_worden_volledig_verwerkt(self):
        self.app.speler["xp"] = 3
        with patch.object(self.app, "toon_level_keuze") as keuze, \
                patch.object(self.app, "start_baasgevecht") as baas:
            self.app.controleer_level(kies_upgrade=False)
        self.assertEqual(self.app.speler["level"], BAAS_LEVEL + 2)
        self.assertEqual(self.app.speler["xp"], 0)
        self.assertEqual(self.app.speler["max_hp"], 390 + 3 * LEVEL_BASIS_HP)
        self.assertEqual(self.app.speler["aanval"], 72 + 3 * LEVEL_BASIS_AANVAL)
        self.assertEqual(self.app.speler["hp"], self.app.speler["max_hp"])
        self.assertEqual(self.app.level_keuzes, [])
        keuze.assert_not_called()
        baas.assert_not_called()

    def test_onbekende_upgrade_behoudt_de_openstaande_keuze(self):
        self.app.level_keuzes = [BAAS_LEVEL]
        speler = self.app.speler.copy()
        with self.assertRaises(ValueError):
            self.app.kies_level_upgrade("onbekend")
        self.assertEqual(self.app.level_keuzes, [BAAS_LEVEL])
        self.assertEqual(self.app.level_upgrades, [])
        self.assertEqual(self.app.speler, speler)

    def test_woede_en_schaduwvuur(self):
        self.start_baas()
        self.app.speler.update(hp=1000, max_hp=1000)
        self.app.vijand["hp"] = BAAS_HP // 2
        with patch("main.random.randint", side_effect=lambda laag, hoog: laag + 2) as worp:
            self.app.vijand_valt_aan()
            self.app.vijand_valt_aan()
            self.app.vijand_valt_aan()
        self.assertTrue(self.app.vijand["woedend"])
        self.assertEqual([call.args for call in worp.call_args_list],
                         [(36, 40), (36, 40), (55, 59)])
        self.assertEqual(self.app.speler["hp"], 734)

    def test_woede_blijft_actief_na_genezing(self):
        self.start_baas()
        with patch("main.random.randint", return_value=50):
            self.app.vijand_valt_aan()
            self.assertEqual(self.app.speler["hp"], 340)
            self.app.vijand["hp"] = BAAS_HP // 2
            self.app.vijand_valt_aan()
            self.assertEqual(self.app.speler["hp"], 240)
            self.app.vijand.update(hp=BAAS_HP, beurten=0)
            self.app.vijand_valt_aan()
            self.assertEqual(self.app.speler["hp"], 140)

    def test_nederlaag_toont_verliespagina_verliest_level_en_geeft_herstelgeld(self):
        for baas, goud in [(False, 125), (True, 125), (False, 0)]:
            with self.subTest(baas=baas, goud=goud):
                self.app.speler.update(hp=1, goud=goud)
                if baas:
                    self.start_baas()
                else:
                    self.app.vijand = maak_vijand(19)
                    self.app.gevecht = True
                voortgang = self.app.speler.copy()
                with patch("main.random.randint", return_value=48), \
                        patch.object(self.app, "toon_startscherm") as startscherm:
                    self.app.vijand_valt_aan()
                startscherm.assert_not_called()
                self.assertEqual(self.app.speler,
                                 {**voortgang, "level": voortgang["level"] - 1,
                                  "hp": voortgang["max_hp"] - LEVEL_BASIS_HP,
                                  "max_hp": voortgang["max_hp"] - LEVEL_BASIS_HP,
                                  "aanval": voortgang["aanval"] - LEVEL_BASIS_AANVAL,
                                  "goud": NEDERLAAG_GOUD})
                self.assertFalse(self.app.gevecht)
                self.assertIsNone(self.app.vijand)
                self.app.verder_na_verlies()
                self.assertIn("Verkennen", [w.cget("text") for w in self.app.acties.winfo_children()])
                with patch("main.random.randint", return_value=1):
                    self.app.verken()
                self.assertTrue(self.app.gevecht)
                self.assertFalse(self.app.vijand.get("baas", False))
                self.app.gevecht = False
                self.app.vijand = None

    def test_nederlaag_draait_upgrade_van_verloren_level_terug(self):
        self.app.speler.update(level=2, hp=1, max_hp=120 + LEVEL_BASIS_HP + LEVEL_HP_UPGRADE,
                               aanval=18 + LEVEL_BASIS_AANVAL, goud=80)
        self.app.level_upgrades = ["hp"]
        self.app.vijand = maak_vijand(2)
        self.app.gevecht = True
        with patch("main.random.randint", return_value=48):
            self.app.vijand_valt_aan()
        self.assertEqual(self.app.speler["level"], 1)
        self.assertEqual(self.app.speler["max_hp"], 120)
        self.assertEqual(self.app.speler["hp"], 120)
        self.assertEqual(self.app.level_upgrades, [])
        self.assertEqual(self.app.speler["goud"], NEDERLAAG_GOUD)

    def test_vluchten_en_opnieuw_ontmoeten(self):
        self.start_baas()
        self.app.vijand["hp"] = 200
        with patch("main.random.randint", return_value=35):
            self.app.vlucht()
        self.assertFalse(self.app.gevecht)
        self.app.verken()
        self.assertTrue(self.app.vijand["baas"])
        self.assertEqual(self.app.vijand["hp"], BAAS_HP)

    def test_mislukte_vlucht_kost_een_beurt(self):
        self.start_baas()
        with patch("main.random.randint", side_effect=[36, 48]):
            self.app.vlucht()
        self.assertTrue(self.app.gevecht)
        self.assertEqual(self.app.speler["hp"], 342)
        self.assertEqual(self.app.vijand["beurten"], 1)

    def test_overwinning_geeft_beloning_en_geen_tweede_baas(self):
        self.start_baas()
        goud = self.app.speler["goud"]
        self.app.vijand["hp"] = 0
        self.app.verwerk_beurt()
        self.kies_level("Levenskracht")
        self.assertTrue(self.app.speler["baas_verslagen"])
        self.assertEqual(self.app.speler["goud"], goud + 500)
        self.assertEqual(self.app.speler["level"], BAAS_LEVEL+1)
        self.assertEqual(self.app.speler["xp"], 0)
        self.assertFalse(self.app.gevecht)
        with patch("main.random.randint", return_value=1):
            self.app.verken()
        self.assertFalse(self.app.vijand.get("baas", False))

    def test_hp_balk_volgt_schade_en_past_in_venster(self):
        self.start_baas()
        self.app.vijand["hp"] = BAAS_HP // 2
        self.app.vijand["woedend"] = True
        self.root.deiconify()
        self.root.geometry("900x760")
        self.root.update()
        self.app.teken_scène()
        canvas = self.app.scène
        breedte = canvas.winfo_width()
        links, _, rechts, _ = canvas.coords(canvas.find_withtag("baas_hp")[0])
        self.assertAlmostEqual(rechts - links, (breedte * .64 - 4) / 2)
        self.assertTrue(canvas.find_withtag("baas_hud"))
        self.assertFalse(self.app.vijand_frame.winfo_ismapped())
        for knop in self.app.acties.winfo_children():
            self.assertLessEqual(knop.winfo_rootx() + knop.winfo_width(),
                                 self.root.winfo_rootx() + self.root.winfo_width())
            self.assertLessEqual(knop.winfo_rooty() + knop.winfo_height(),
                                 self.root.winfo_rooty() + self.root.winfo_height())




    def test_een_kill_geeft_een_level_en_basisbonussen(self):
        self.app.speler.update(level=1, xp=0, hp=100, max_hp=120, aanval=18)
        self.app.controleer_level()
        self.assertEqual(self.app.speler["level"], 1)
        self.app.speler["xp"] = 1
        self.app.controleer_level()
        self.assertEqual(self.app.speler["level"], 2)
        self.kies_level("Verdediging")
        self.assertEqual(self.app.speler["max_hp"], 120 + LEVEL_BASIS_HP)
        self.assertEqual(self.app.speler["aanval"], 18 + LEVEL_BASIS_AANVAL)
        self.assertEqual(self.app.speler["verdediging"], LEVEL_VERDEDIGING_UPGRADE)
        self.assertEqual(self.app.speler["hp"], self.app.speler["max_hp"])

    def test_meerdere_kills_geven_afzonderlijke_upgradekeuzes(self):
        self.app.speler.update(level=1, xp=0, hp=30, max_hp=120, aanval=18)
        for keuze in ("hp", "aanval"):
            self.app.vijand = maak_vijand(self.app.speler["level"])
            self.app.vijand["hp"] = 0
            self.app.gevecht = True
            self.app.verwerk_beurt()
            self.assertEqual(len(self.app.level_keuzes), 1)
            self.app.kies_level_upgrade(keuze)
        self.assertEqual(self.app.speler["level"], 3)
        self.assertEqual(self.app.speler["xp"], 0)
        self.assertEqual(self.app.speler["hp"], self.app.speler["max_hp"])
        self.assertEqual(self.app.speler["max_hp"], 120 + 2 * LEVEL_BASIS_HP + LEVEL_HP_UPGRADE)
        self.assertEqual(self.app.speler["aanval"], 18 + 2 * LEVEL_BASIS_AANVAL + LEVEL_AANVAL_UPGRADE)
        self.assertEqual(self.app.level_upgrades, ["hp", "aanval"])

    def test_level_100_start_gouden_draak_na_upgradekeuze(self):
        self.app.speler.update(level=99, xp=0, baas_verslagen=True)
        self.app.vijand = maak_vijand(99)
        self.app.vijand["hp"] = 0
        self.app.gevecht = True
        self.app.verwerk_beurt()
        self.assertEqual(self.app.speler["level"], 100)
        self.assertFalse(self.app.gevecht)
        self.app.kies_level_upgrade("aanval")
        self.assertTrue(self.app.gevecht)
        self.assertTrue(self.app.vijand["eindbaas"])
        self.assertEqual(self.app.vijand["naam"], "Gouden Draak")
        self.assertEqual(self.app.vijand["hp"], EINDBAAS_HP)
        self.assertEqual(self.app.vijand["aanval"], EINDBAAS_AANVAL)
        self.assertEqual(self.app.vijand["genezing"], EINDBAAS_GENEZING)
        teksten = [self.app.scène.itemcget(item, "text")
                   for item in self.app.scène.find_withtag("baas_hud")
                   if self.app.scène.type(item) == "text"]
        self.assertTrue(any("GOUDEN DRAAK" in tekst for tekst in teksten))

    def test_gouden_draak_verslaan_toont_einde_en_geeft_een_level(self):
        self.app.speler.update(level=100, xp=0, baas_verslagen=True)
        self.app.start_baasgevecht()
        goud = self.app.speler["goud"]
        self.app.vijand["hp"] = 0
        self.app.verwerk_beurt()
        self.assertTrue(self.app.speler["uitgespeeld"])
        self.assertEqual(self.app.speler["level"], 101)
        self.assertEqual(self.app.speler["goud"], goud + 2000)
        self.assertIsNone(self.app.level_keuze_venster)
        self.assertFalse(self.app.gevecht)
        kaart = next(w for w in self.root.winfo_children() if isinstance(w, tk.Frame))
        self.assertTrue(any(isinstance(w, tk.Label) and "UITGESPEELD" in w.cget("text")
                            for w in kaart.winfo_children()))
        self.app.verken()
        self.assertIsNone(self.app.vijand)
        self.assertFalse(self.app.start_baasgevecht())
        next(w for w in kaart.winfo_children() if isinstance(w, tk.Button)
             and w.cget("text") == "Nieuw avontuur").invoke()
        self.app.naam_invoer.insert(0, "Nieuwe held")
        self.app.start_spel()
        self.assertFalse(self.app.speler["uitgespeeld"])
        self.assertEqual(self.app.speler["level"], 1)

    def test_gouden_draak_geneest_met_eindbaas_genezing(self):
        self.app.speler.update(level=EINDBAAS_LEVEL, baas_verslagen=True)
        self.app.start_baasgevecht()
        self.app.vijand["hp"] -= 500

        with patch("main.random.randint", return_value=EINDBAAS_AANVAL), \
                patch.object(self.app, "update_status"), \
                patch.object(self.app, "update_acties"), \
                patch.object(self.app, "teken_scène"), \
                patch.object(self.app, "toon_effect"):
            self.app.vijand_valt_aan()

        self.assertEqual(
            self.app.vijand["hp"],
            EINDBAAS_HP - 500 + EINDBAAS_GENEZING,
        )

    def test_gouden_draak_vluchten_en_opnieuw_proberen(self):
        self.app.speler.update(level=100, baas_verslagen=True)
        self.app.start_baasgevecht()
        self.app.vijand["hp"] = 10
        with patch("main.random.randint", return_value=1):
            self.app.vlucht()
        self.assertFalse(self.app.speler["uitgespeeld"])
        self.app.verken()
        self.assertTrue(self.app.vijand["eindbaas"])
        self.assertEqual(self.app.vijand["hp"], EINDBAAS_HP)

    def test_potion_geneest_halve_max_hp_en_kost_een_beurt(self):
        for max_hp, verwacht in [(120, 72), (390, 207), (121, 72)]:
            with self.subTest(max_hp=max_hp):
                self.app.speler.update(hp=20, max_hp=max_hp, inventaris=["Health Potion"])
                self.app.vijand = maak_vijand(1)
                self.app.gevecht = True
                with patch("main.random.randint", return_value=8):
                    self.app.gebruik_potion()
                self.assertEqual(self.app.speler["hp"], verwacht)
                self.assertEqual(self.app.speler["inventaris"], [])

    def test_potion_geneest_niet_boven_max_hp(self):
        self.app.speler.update(hp=110, max_hp=120)
        self.app.vijand = maak_vijand(1)
        self.app.gevecht = True
        with patch.object(self.app, "verwerk_beurt"):
            self.app.gebruik_potion()
        self.assertEqual(self.app.speler["hp"], 120)
        self.assertEqual(len(self.app.speler["inventaris"]), 1)

    def test_potion_bij_volle_hp_of_zonder_potion_kost_geen_beurt(self):
        for hp, inventaris in [(120, ["Health Potion"]), (20, [])]:
            with self.subTest(hp=hp):
                self.app.speler.update(hp=hp, max_hp=120, inventaris=inventaris.copy())
                with patch.object(self.app, "verwerk_beurt") as beurt:
                    self.app.gebruik_potion()
                beurt.assert_not_called()
                self.assertEqual(self.app.speler["hp"], hp)
                self.assertEqual(self.app.speler["inventaris"], inventaris)

    def test_vijanden_schalen_met_het_level(self):
        with patch("main.random.choice", return_value="Goblin"):
            laag = maak_vijand(1)
            hoog = maak_vijand(20)
        self.assertEqual(laag["hp"], 40)
        self.assertEqual(hoog["hp"], 192)
        self.assertEqual(hoog["aanval"], 30)

    def test_verkennen_vervangt_lopen_zonder_loop_timer(self):
        self.assertIn('Verkennen', [w.cget('text') for w in self.app.acties.winfo_children()])
        self.assertFalse(self.app.animaties)
        with patch('main.random.randint', return_value=1):
            self.app.verken()
        vijand = self.app.vijand
        self.app.verken()
        self.assertIs(self.app.vijand, vijand)

    def test_verdedigen_tegen_aangekondigde_zware_aanval(self):
        self.app.speler.update(hp=120, max_hp=120)
        self.app.vijand = maak_vijand(1)
        self.app.vijand.update(aanval=20, beurten=2)
        self.app.gevecht = True
        self.app.teken_scène()
        self.assertIn('ZWARE AANVAL', self.app.vijand_naam.cget('text'))
        with patch('main.random.randint', return_value=30):
            self.app.verdedig()
        self.assertEqual(self.app.speler['hp'], 110)
        self.assertEqual(self.app.vijand['beurten'], 3)
        self.assertIn('Normale aanval', self.app.vijand_naam.cget('text'))

    def test_genezing_per_beurt_tot_maximum(self):
        self.start_baas()
        self.app.vijand['hp'] = BAAS_HP-20
        with patch('main.random.randint', return_value=34):
            self.app.vijand_valt_aan()
            self.assertEqual(self.app.vijand['hp'], BAAS_HP-20+BAAS_GENEZING)
            self.app.vijand_valt_aan()
        self.assertEqual(self.app.vijand['hp'], BAAS_HP)

    def test_winkel_limiet_en_stijgende_prijs(self):
        self.app.speler.update(level=1, goud=10000)
        self.app.bezoek_winkel()
        winkel = next(w for w in self.root.winfo_children() if isinstance(w, tk.Toplevel))
        knop = next(w for w in winkel.winfo_children()[0].winfo_children()
                    if isinstance(w, tk.Button) and w.cget('text').startswith('Wapen'))
        aanval = self.app.speler['aanval']
        knop.invoke()
        self.assertEqual(self.app.speler['aanval'], aanval+WAPEN_VERBETERING)
        self.assertEqual(self.app.speler['goud'], 9920)
        self.assertEqual(knop.cget('state'), 'disabled')
        knop.invoke()
        self.assertEqual(self.app.speler['wapen_upgrades'], 1)
        winkel.destroy()
        self.app.speler['level'] = 2
        self.app.bezoek_winkel()
        winkel = next(w for w in self.root.winfo_children() if isinstance(w, tk.Toplevel))
        knop = next(w for w in winkel.winfo_children()[0].winfo_children()
                    if isinstance(w, tk.Button) and w.cget('text').startswith('Wapen'))
        prijs = wapen_prijs(self.app.speler)
        self.assertGreater(prijs, 80)
        knop.invoke()
        self.assertEqual(self.app.speler['goud'], 9920-prijs)

    def test_winkel_kan_tien_potions_tegelijk_kopen(self):
        self.app.speler.update(goud=1000)
        aantal_potions = self.app.speler["inventaris"].count("Health Potion")
        self.app.bezoek_winkel()
        winkel = next(w for w in self.root.winfo_children() if isinstance(w, tk.Toplevel))
        knop = next(
            w for w in winkel.winfo_children()[0].winfo_children()
            if isinstance(w, tk.Button) and w.cget("text").startswith("10x Health Potion")
        )

        knop.invoke()

        self.assertEqual(self.app.speler["inventaris"].count("Health Potion"), aantal_potions + 10)
        self.assertEqual(self.app.speler["goud"], 1000 - 10 * POTION_PRIJS)

        self.app.speler["goud"] = 10 * POTION_PRIJS - 1
        with patch("main.messagebox.showinfo") as melding:
            knop.invoke()
        melding.assert_called_once()
        self.assertEqual(self.app.speler["inventaris"].count("Health Potion"), aantal_potions + 10)
        self.assertEqual(self.app.speler["goud"], 10 * POTION_PRIJS - 1)
        winkel.destroy()

    def test_winkel_kan_honderd_potions_tegelijk_kopen(self):
        self.app.speler.update(goud=100 * POTION_PRIJS)
        aantal_potions = self.app.speler["inventaris"].count("Health Potion")
        self.app.bezoek_winkel()
        winkel = next(w for w in self.root.winfo_children() if isinstance(w, tk.Toplevel))
        knop = next(
            w for w in winkel.winfo_children()[0].winfo_children()
            if isinstance(w, tk.Button) and w.cget("text").startswith("100x Health Potion")
        )

        knop.invoke()

        self.assertEqual(self.app.speler["inventaris"].count("Health Potion"), aantal_potions + 100)
        self.assertEqual(self.app.speler["goud"], 0)
        winkel.destroy()


class ProgressieTests(unittest.TestCase):
    def test_hele_avontuur_is_haalbaar_voor_elke_klasse(self):
        for klasse in KLASSEN:
            with self.subTest(klasse=klasse):
                app = MiniRPG.__new__(MiniRPG)
                app.speler = maak_speler("Held", klasse)
                app.vijand = None
                app.gevecht = False
                app.level_keuzes = []
                app.level_upgrades = []
                app.level_keuze_venster = None
                for methode in ("log", "update_status", "update_acties", "teken_scène",
                                "toon_effect", "toon_level_keuze", "toon_overwinningspagina",
                                "toon_verliespagina"):
                    setattr(app, methode, Mock())

                def worp(laag, hoog):
                    if (laag, hoog) == (1, 100):
                        return 100  # Geen kritieke treffers.
                    if hoog == app.speler["aanval"] + 3:
                        return laag  # Minimaal uitgaande schade.
                    return hoog  # Maximaal inkomende schade.

                kills = 0
                with patch("main.random.randint", side_effect=worp), \
                        patch("main.random.choice", return_value="Draak"):
                    while not app.speler["uitgespeeld"] and kills < 100:
                        if not app.gevecht and not app.start_baasgevecht():
                            app.vijand = maak_vijand(app.speler["level"])
                            app.gevecht = True
                        for _ in range(100):
                            app.val_aan()
                            if not app.gevecht:
                                break
                        self.assertFalse(app.gevecht)
                        self.assertGreater(app.speler["hp"], 0)
                        app.toon_verliespagina.assert_not_called()
                        kills += 1
                        if app.level_keuzes:
                            app.kies_level_upgrade("verdediging")
                self.assertEqual(kills, 100)
                self.assertEqual(app.speler["level"], 101)
                self.assertTrue(app.speler["baas_verslagen"])
                self.assertTrue(app.speler["uitgespeeld"])
                app.toon_overwinningspagina.assert_called_once()

    def test_gevechten_zijn_makkelijker_zonder_extra_upgrades(self):
        for klasse, stats in KLASSEN.items():
            for level in (10, 30, 60, 99):
                aanval = stats["aanval"] + (level - 1) * LEVEL_BASIS_AANVAL
                for soort in ("Goblin", "Orc", "Draak"):
                    with self.subTest(klasse=klasse, level=level, soort=soort):
                        with patch("main.random.choice", return_value=soort):
                            vijand = maak_vijand(level)
                        self.assertLessEqual(vijand["hp"], 2 * (aanval - 3))
                        self.assertEqual(vijand["xp"], xp_voor_level(level))

    def test_route_naar_level_100_duurt_99_kills(self):
        self.assertEqual(sum(xp_voor_level(level) for level in range(1, EINDBAAS_LEVEL)), 99)


if __name__ == "__main__":
    unittest.main()
