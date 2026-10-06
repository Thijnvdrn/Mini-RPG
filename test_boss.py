"""Regressiechecks voor de levelovergang en het baasgevecht."""

import tkinter as tk
import unittest
from unittest.mock import patch

from main import (MiniRPG, maak_vijand, maak_speler, xp_voor_level, wapen_prijs, wapen_limiet,
                  BAAS_LEVEL, BAAS_HP, BAAS_GENEZING, LEVEL_HP_UPGRADE,
                  LEVEL_AANVAL_UPGRADE, LEVEL_VERDEDIGING_UPGRADE,
                  WAPEN_VERBETERING, KLASSEN, NEDERLAAG_GOUD,
                  EINDBAAS_LEVEL, EINDBAAS_HP, EINDBAAS_AANVAL,
                  EINDBAAS_GENEZING, maak_eindbaas)


class BaasgevechtTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.app = MiniRPG(self.root)
        self.app.naam_invoer.insert(0, "Testheld")
        self.app.start_spel()
        self.app.speler.update(level=BAAS_LEVEL-1, hp=390, max_hp=390, aanval=72, xp=xp_voor_level(BAAS_LEVEL-1)-20)

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

    def test_naam_baas_start_vlak_voor_eindbaas_met_10k_goud(self):
        self.app.wis_scherm()
        self.app.toon_startscherm()
        self.app.naam_invoer.insert(0, "Baas")
        self.app.start_spel()
        self.assertEqual(self.app.speler["level"], BAAS_LEVEL-1)
        self.assertEqual(self.app.speler["goud"], 10_000)
        self.assertEqual(self.app.speler["hp"], self.app.speler["max_hp"])
        self.assertEqual(self.app.speler["max_hp"], 120 + 10 * LEVEL_HP_UPGRADE)
        self.assertEqual(self.app.speler["aanval"], 18 + 9 * LEVEL_AANVAL_UPGRADE)
        self.assertEqual(self.app.speler["verdediging"], 9 * LEVEL_VERDEDIGING_UPGRADE)

    def test_overwinning_bij_levelgrens_start_baas_direct(self):
        self.app.vijand = maak_vijand(19)
        self.app.vijand.update(hp=0, xp=20)
        self.app.gevecht = True
        self.app.verwerk_beurt()
        self.kies_level("Aanval")
        self.assertEqual(self.app.speler["level"], BAAS_LEVEL)
        self.assertEqual(self.app.speler["hp"], 390)
        self.assertEqual(self.app.speler["max_hp"], 390)
        self.assertEqual(self.app.speler["aanval"], 75)
        self.assertTrue(self.app.gevecht)
        self.assertTrue(self.app.vijand["baas"])
        self.assertEqual(self.app.vijand["hp"], BAAS_HP)

    def test_onder_baaslevel_heeft_geen_baas(self):
        with patch("main.random.randint", return_value=1):
            self.app.verken()
        self.assertFalse(self.app.vijand.get("baas", False))

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
                                  "hp": voortgang["max_hp"], "goud": NEDERLAAG_GOUD})
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
        self.app.speler.update(level=2, hp=1, max_hp=120 + LEVEL_HP_UPGRADE,
                               aanval=18, goud=80)
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
        self.assertEqual(self.app.speler["xp"], xp_voor_level(BAAS_LEVEL-1)-20+1200-xp_voor_level(BAAS_LEVEL))
        self.assertFalse(self.app.gevecht)
        with patch("main.random.randint", return_value=1):
            self.app.verken()
        self.assertFalse(self.app.vijand.get("baas", False))

    def test_level_100_start_gouden_draak_als_eindbaas(self):
        self.app.speler.update(level=EINDBAAS_LEVEL, baas_verslagen=True)
        self.assertTrue(self.app.start_baasgevecht())
        self.assertEqual(self.app.vijand, maak_eindbaas())
        self.assertEqual(self.app.vijand["naam"], "Gouden Draak")
        self.assertTrue(self.app.vijand["eindbaas"])
        self.assertEqual(self.app.vijand["hp"], EINDBAAS_HP)
        self.assertEqual(self.app.vijand["aanval"], EINDBAAS_AANVAL)
        self.assertEqual(self.app.vijand["genezing"], EINDBAAS_GENEZING)

    def test_gouden_draak_verslaan_toont_eindmelding_met_bedankje(self):
        self.app.speler.update(level=EINDBAAS_LEVEL, baas_verslagen=True)
        self.app.start_baasgevecht()
        self.app.vijand["hp"] = 0
        with patch("main.messagebox.showinfo") as melding:
            self.app.verwerk_beurt()
        self.assertTrue(self.app.spel_uitgespeeld)
        self.assertTrue(self.app.speler["eindbaas_verslagen"])
        self.assertFalse(self.app.gevecht)
        self.assertIsNone(self.app.vijand)
        melding.assert_called_once()
        self.assertIn("👑", melding.call_args.args[0])
        self.assertIn("Bedankt voor het spelen", melding.call_args.args[1])
        self.assertFalse(self.app.start_baasgevecht())

    def test_level_is_afgetopt_op_100(self):
        self.app.speler.update(
            level=EINDBAAS_LEVEL, xp=xp_voor_level(EINDBAAS_LEVEL) + 1000,
            baas_verslagen=True, eindbaas_verslagen=True,
        )
        self.app.controleer_level()
        self.assertEqual(self.app.speler["level"], EINDBAAS_LEVEL)
        self.assertEqual(self.app.speler["xp"], xp_voor_level(EINDBAAS_LEVEL) + 1000)

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

    def test_gouden_draak_wordt_met_kroon_in_baas_hud_getoond(self):
        self.app.speler.update(level=EINDBAAS_LEVEL, baas_verslagen=True)
        self.app.start_baasgevecht()
        self.root.update()
        hud_tekst = [
            self.app.scène.itemcget(item, "text")
            for item in self.app.scène.find_withtag("baas_hud")
            if self.app.scène.type(item) == "text"
        ]
        self.assertTrue(any("👑 GOUDEN DRAAK" in tekst for tekst in hud_tekst))
        self.assertTrue(any("Gouden vuur elke derde beurt" in tekst for tekst in hud_tekst))




    def test_levelen_met_gematigde_xp_drempel(self):
        self.app.speler.update(level=1, xp=99, hp=100, max_hp=120, aanval=18)
        self.app.controleer_level()
        self.assertEqual(self.app.speler["level"], 1)
        self.app.speler["xp"] = 100
        self.app.controleer_level()
        self.assertEqual(self.app.speler["level"], 2)
        self.kies_level("Verdediging")
        self.assertEqual(self.app.speler["max_hp"], 120)
        self.assertEqual(self.app.speler["aanval"], 18)
        self.assertEqual(self.app.speler["verdediging"], LEVEL_VERDEDIGING_UPGRADE)
        self.assertEqual(self.app.speler["hp"], 100)

    def test_meerdere_levels_geven_afzonderlijke_upgradekeuzes(self):
        self.app.speler.update(level=1, xp=304, hp=30, max_hp=120, aanval=18)
        self.app.controleer_level()
        self.assertEqual(self.app.speler["level"], 3)
        self.assertEqual(self.app.level_keuzes, [2, 3])
        self.kies_level("Levenskracht")
        self.assertEqual(self.app.speler["hp"], 50)
        self.kies_level("Aanval")
        self.assertEqual(self.app.speler["max_hp"], 120 + LEVEL_HP_UPGRADE)
        self.assertEqual(self.app.speler["aanval"], 18 + LEVEL_AANVAL_UPGRADE)
        self.assertEqual(self.app.level_upgrades, ["hp", "aanval"])

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
        self.assertEqual(hoog["hp"], 472)
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


class ProgressieTests(unittest.TestCase):
    def test_gevechten_blijven_lastig_met_maximale_upgrades(self):
        for klasse, stats in KLASSEN.items():
            for level in (10, 20, 30, 40):
                speler = maak_speler('Held', klasse)
                speler['level'] = level
                aanval = (stats['aanval'] + (level-1)*LEVEL_AANVAL_UPGRADE
                          + wapen_limiet(speler)*WAPEN_VERBETERING)
                for soort in ('Goblin', 'Orc', 'Draak'):
                    with self.subTest(klasse=klasse, level=level, soort=soort):
                        with patch('main.random.choice', return_value=soort):
                            vijand = maak_vijand(level)
                        self.assertGreater(vijand['hp'], 2*(aanval+3))
                        if level >= 20:
                            self.assertGreaterEqual(vijand['hp'], 4*(aanval+3))

    def test_route_duurt_minstens_tweemaal_zo_lang(self):
        oud = sum(level*80/(95/3+(level-1)*5) for level in range(1,20))
        nieuw = sum(
            xp_voor_level(level)/(95/3+(level-1)*5)
            for level in range(1, EINDBAAS_LEVEL)
        )
        self.assertGreater(nieuw, oud*2)


if __name__ == "__main__":
    unittest.main()
