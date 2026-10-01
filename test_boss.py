"""Regressiechecks voor de level-20-overgang en het baasgevecht."""

import tkinter as tk
import unittest
from unittest.mock import patch

from main import MiniRPG, maak_vijand


class BaasgevechtTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.app = MiniRPG(self.root)
        self.app.naam_invoer.insert(0, "Testheld")
        self.app.start_spel()
        self.app.speler.update(level=19, hp=390, max_hp=390, aanval=72, xp=1500)

    def tearDown(self):
        self.app.wis_scherm()
        self.root.update_idletasks()
        self.root.destroy()

    def start_baas(self):
        self.app.speler["level"] = 20
        self.app.start_baasgevecht()

    def test_overwinning_op_level_19_start_baas_direct(self):
        self.app.vijand = maak_vijand(19)
        self.app.vijand.update(hp=0, xp=20)
        self.app.gevecht = True
        self.app.verwerk_beurt()
        self.assertEqual(self.app.speler["level"], 20)
        self.assertEqual(self.app.speler["hp"], 390)
        self.assertEqual(self.app.speler["max_hp"], 402)
        self.assertTrue(self.app.gevecht)
        self.assertTrue(self.app.vijand["baas"])
        self.assertEqual(self.app.vijand["hp"], 5000)

    def test_level_19_heeft_geen_baas(self):
        with patch("main.random.randint", return_value=1):
            self.app.verken()
        self.assertFalse(self.app.vijand.get("baas", False))

    def test_woede_en_schaduwvuur(self):
        self.start_baas()
        self.app.vijand["hp"] = 350
        with patch("main.random.randint", side_effect=lambda laag, hoog: laag + 2) as worp:
            self.app.vijand_valt_aan()
            self.app.vijand_valt_aan()
            self.app.vijand_valt_aan()
        self.assertTrue(self.app.vijand["woedend"])
        self.assertEqual([call.args for call in worp.call_args_list],
                         [(58, 62), (58, 62), (88, 92)])
        self.assertEqual(self.app.speler["hp"], 180)

    def test_vluchten_en_opnieuw_ontmoeten(self):
        self.start_baas()
        self.app.vijand["hp"] = 200
        with patch("main.random.randint", return_value=35):
            self.app.vlucht()
        self.assertFalse(self.app.gevecht)
        self.app.verken()
        self.assertTrue(self.app.vijand["baas"])
        self.assertEqual(self.app.vijand["hp"], 5000)

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
        self.assertTrue(self.app.speler["baas_verslagen"])
        self.assertEqual(self.app.speler["goud"], goud + 500)
        self.assertEqual(self.app.speler["level"], 21)
        self.assertEqual(self.app.speler["xp"], 1100)
        self.assertFalse(self.app.gevecht)
        with patch("main.random.randint", return_value=1):
            self.app.verken()
        self.assertFalse(self.app.vijand.get("baas", False))

    def test_hp_balk_volgt_schade_en_past_in_venster(self):
        self.start_baas()
        self.app.vijand["hp"] = 2500
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
            self.assertLessEqual(knop.winfo_rooty() + knop.winfo_height(),
                                 self.root.winfo_rooty() + self.root.winfo_height())

    def test_genezing_per_seconde_en_nooit_boven_maximum(self):
        with patch.object(self.app, "later", return_value=None) as timer:
            self.start_baas()
            genees = timer.call_args.args[1]
            self.assertEqual(timer.call_args.args[0], 1000)
            self.app.vijand["hp"] = 4800
            genees()
            self.assertEqual(self.app.vijand["hp"], 4900)
            self.app.vijand["hp"] = 4990
            genees()
            self.assertEqual(self.app.vijand["hp"], 5000)
            self.assertEqual(timer.call_count, 3)

    def test_timer_stopt_na_vlucht_en_oude_baas_geneest_niet(self):
        self.start_baas()
        timer = self.app.baas_genezing
        with patch("main.random.randint", return_value=1):
            self.app.vlucht()
        self.assertIsNone(self.app.baas_genezing)
        self.assertNotIn(timer, self.root.tk.call("after", "info"))

    def test_verslagen_baas_wordt_niet_opnieuw_genezen(self):
        with patch.object(self.app, "later", return_value=None) as timer:
            self.start_baas()
            genees = timer.call_args.args[1]
            baas = self.app.vijand
            baas["hp"] = 0
            self.app.verwerk_beurt()
            genees()
            self.assertEqual(baas["hp"], 0)
            self.assertEqual(timer.call_count, 1)

    def test_levelen_met_gematigde_xp_drempel(self):
        self.app.speler.update(level=1, xp=79, hp=100, max_hp=120, aanval=18)
        self.app.controleer_level()
        self.assertEqual(self.app.speler["level"], 1)
        self.app.speler["xp"] = 80
        self.app.controleer_level()
        self.assertEqual(self.app.speler["level"], 2)
        self.assertEqual(self.app.speler["max_hp"], 132)
        self.assertEqual(self.app.speler["aanval"], 21)
        self.assertEqual(self.app.speler["hp"], 100)

    def test_meerdere_levels_herstellen_geen_hp(self):
        self.app.speler.update(level=1, xp=240, hp=30, max_hp=120)
        self.app.controleer_level()
        self.assertEqual(self.app.speler["level"], 3)
        self.assertEqual(self.app.speler["hp"], 30)
        self.assertEqual(self.app.speler["max_hp"], 144)

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
        self.assertEqual(hoog["hp"], 268)
        self.assertEqual(hoog["aanval"], 46)


if __name__ == "__main__":
    unittest.main()
