# Mini-RPG — De Wildernis

Welkom in **De Wildernis**, een kleine Nederlandstalige RPG die met Python en Tkinter is gemaakt. Kies een held, verken een maanverlicht bos en word sterk genoeg om de Nachtvorst te verslaan. Deze README legt uit hoe je het spel start, hoe het werkt en waar je de verschillende onderdelen van de code kunt vinden.

## Starten

Je hebt Python 3.10 of hoger nodig. Tkinter wordt normaal gesproken met Python meegeleverd; er zijn geen extra packages nodig.

```powershell
python main.py
```

Voer dit commando uit vanuit de map met de spelbestanden. Vul daarna een naam in, kies een klasse en begin je avontuur.

## Het spel

Je begint met 20 goud en twee Health Potions. Kies uit drie klassen:

| Klasse | Levenspunten | Aanval | Kritieke kans |
| --- | ---: | ---: | ---: |
| Krijger | 120 | 18 | 10% |
| Magiër | 80 | 25 | 10% |
| Sluipmoordenaar | 95 | 16 | 40% |

Verken het bos om Goblins, Orcs en Draken tegen te komen. In 25% van de verkenningen is er geen gevecht en herstel je maximaal 8 HP. Tijdens een gevecht kun je aanvallen, een potion gebruiken of proberen te vluchten. Een kritieke treffer doet dubbele schade. Vluchten lukt bij gewone vijanden met 60% kans; als het mislukt, valt de vijand aan. Bij 0 HP eindigt het spel.

Versla vijanden om goud en XP te verdienen. Iedere level vereist `level × 80` XP. Een nieuw level geeft 12 Max HP en 3 aanval; je huidige HP wordt daarbij niet hersteld. Vijanden worden sterker naarmate je level stijgt: per level krijgen ze 12 extra HP en 2 extra aanval.

De handelaar verkoopt Health Potions voor 20 goud en wapen-upgrades voor 45 goud. Een potion herstelt 50% van je maximale HP (naar beneden afgerond), tot maximaal je volle gezondheid. Een wapen-upgrade geeft 5 extra aanval.

### De Nachtvorst

Bij level 20 begint het baasgevecht tegen de Nachtvorst. Als je tijdens een gevecht level 20 bereikt, begint het gevecht meteen; anders start het bij je volgende verkenning. De baas heeft 5000 HP en geneest tijdens het gevecht iedere seconde 100 HP. Elke derde vijandelijke beurt gebruikt hij schaduwvuur, dat 150% van zijn aanval doet. Onder de helft van zijn HP wordt hij woedend en krijgt hij 12 extra aanval.

Vluchten bij de baas lukt met 35% kans. Na een ontsnapping verschijnt hij bij de volgende verkenning weer met volle HP. Een overwinning geeft eenmalig 500 goud en 1200 XP. Boven level 20 krijgt de Nachtvorst per extra level 30 HP en 3 aanval. Je voortgang wordt niet opgeslagen wanneer je het spel afsluit.

## Hoe de code is opgebouwd

- **`main.py`** bevat de spelregels en de Tkinter-interface. Hier worden de speler en vijanden aangemaakt, beurten afgehandeld, XP en levels bijgehouden, de winkel beheerd en het baasgevecht geregeld.
- **`visuals.py`** tekent het bos, de helden, de vijanden en de HUD van de Nachtvorst op een Tkinter Canvas. De illustraties worden in code getekend; er zijn geen losse afbeeldingen nodig.
- **`test_boss.py`** bevat regressietests voor onder andere level-ups, het starten en stoppen van het baasgevecht, genezing, vluchten en de baasbeloning.

De belangrijkste spelinstellingen — zoals prijzen, genezing, levelbonussen en de level waarop de baas verschijnt — staan als constanten bovenaan `main.py`. Klasse-statistieken vind je in `KLASSEN`; de basiswaarden en beloningen van gewone vijanden staan in `maak_vijand()`. Voor nieuwe of aangepaste illustraties kun je terecht in `visuals.py`.

## Tests uitvoeren

```powershell
python -m unittest
```

Voer dit commando uit vanuit de map met de spelbestanden.
De tests maken een Tkinter-venster aan. Op systemen zonder grafische omgeving kan daarvoor een display nodig zijn.
