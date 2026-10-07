# Mini-RPG — De Wildernis

Welkom in **De Wildernis**, een kleine Nederlandstalige RPG die met Python en Tkinter is gemaakt. Kies een held, verken een maanverlicht bos en versla de Gouden Draak op level 100 om het spel uit te spelen. Deze README legt uit hoe je het spel start, hoe het werkt en waar je de verschillende onderdelen van de code kunt vinden.

## Starten

Je hebt Python 3.10 of hoger nodig. Tkinter wordt normaal gesproken met Python meegeleverd; er zijn geen extra packages nodig.

```powershell
python main.py
```

Voer dit commando uit vanuit de map met de spelbestanden. Vul daarna een naam in, kies een klasse en begin je avontuur.

## Het spel

Je begint met 20 goud en twee Health Potions. Kies uit drie klassen:

| Klasse | Levenspunten | Aanval | Verdediging | Kritieke kans |
| --- | ---: | ---: | ---: | ---: |
| Krijger | 240 | 40 | 0 | 10% |
| Magiër | 180 | 55 | 0 | 10% |
| Sluipmoordenaar | 210 | 38 | 0 | 40% |

Klik op **Verkennen** om het bos te onderzoeken. Je ontmoet met 75% kans een Goblin, Orc of Draak; anders herstel je 40 HP. Tijdens gevechten kies je tussen aanvallen, verdedigen, een potion of vluchten. Een kritieke treffer doet dubbele schade. Elke derde vijandelijke beurt volgt een zware aanval met 150% aanvalskracht. De interface waarschuwt hiervoor voordat je je actie kiest. **Verdedigen** kost je aanval die beurt, maar blokkeert 65% van de schade. Potions en mislukte vluchtpogingen geven de vijand ook een beurt.

Vluchten lukt bij gewone vijanden met 60% kans. Bij 0 HP verschijnt eerst een verliespagina; je moet op **Verder naar het woud** klikken voordat je verder kunt. Je verliest je goud en één level (minimaal level 1), herstelt met volle HP en krijgt 100 goud herstelgeld om bij de handelaar in te kopen. De automatische levelbonussen en de upgrade die je bij dat level koos, worden teruggedraaid; inventaris blijft behouden.

Elke kill geeft precies één level, ook bij een baas. Per level krijg je automatisch +30 Max HP, +10 aanval en volle HP. Daarnaast kies je één extra upgrade: +40 Max HP en HP, +10 aanval of +2 verdediging (vermindert iedere inkomende treffer). Gewone vijanden krijgen per extra level 8 HP. Hun aanval groeit met 1 per extra level en nog 1 per vijf extra levels. Zonder nederlagen bereik je level 100 na 99 kills.

De handelaar verkoopt Health Potions voor 20 goud. Een potion herstelt 50% van je Max HP, naar beneden afgerond en tot maximaal volle gezondheid. Wapen-upgrades geven 8 aanval. De eerste kost 80 goud; bij `n` gekochte upgrades kost de volgende `80 + 35n + 15n²` goud. Je kunt maximaal `1 + level // 2` upgrades kopen. Elke twee levels komt dus een extra upgrade vrij. Gewone vijanden geven per extra level 2 extra goud.

### De Nachtvorst

Op level 30 verschijnt de Nachtvorst: direct wanneer je die grens bereikt na een overwinning, of bij de volgende verkenning. Hij heeft 1700 HP en 38 aanval. Hij geneest na elke vijandelijke beurt 16 HP, ook wanneer je verdedigt of een potion gebruikt. Je kunt dus rustig nadenken; snel klikken versnelt zijn genezing niet en omzeilt haar ook niet.

Elke derde beurt gebruikt hij drakenvuur met 150% aanvalskracht. Zodra hij bij zijn aanval op halve HP of lager staat, wordt hij blijvend woedend en doet hij dubbele schade. Let op de waarschuwing en plan je verdediging en potions. Vluchten lukt met 35% kans. Na vluchten kun je hem via Verkennen opnieuw uitdagen; na een nederlaag moet je eerst terug level 30 bereiken.

Een overwinning geeft eenmalig 500 goud en één level. Hij is een tussenbaas: daarna ga je door naar level 100. Boven level 30 krijgt de Nachtvorst per extra level 30 HP en 2 aanval. Je voortgang wordt niet opgeslagen wanneer je het spel afsluit. De testnaam `Baas` begint op level 99 met 10.000.000 goud; ook dan geldt de upgradegrens.

### De Gouden Draak

Op level 100 verschijnt de Gouden Draak, direct na je upgradekeuze of bij de volgende verkenning. Hij heeft 12.000 HP en 150 aanval en geneest 60 HP per beurt. Net als de Nachtvorst gebruikt hij elke derde beurt drakenvuur en wordt hij bij halve HP blijvend woedend. Vluchten lukt met 35% kans; daarna kun je hem opnieuw uitdagen. Na een nederlaag moet je eerst opnieuw level 100 bereiken.

Versla hem voor 2000 goud en één level: je hebt het spel uitgespeeld! Het overwinningsscherm laat je een nieuw avontuur beginnen of het spel afsluiten.

## Hoe de code is opgebouwd

- **`main.py`** bevat de spelregels en de Tkinter-interface. Hier worden de speler en vijanden aangemaakt, beurten afgehandeld, XP en levels bijgehouden, de winkel beheerd en het baasgevecht geregeld.
- **`visuals.py`** tekent het bos, de helden, de vijanden en de HUD van beide bazen op een Tkinter Canvas. De Gouden Draak heeft gouden schubben en vleugels. De illustraties worden in code getekend; er zijn geen losse afbeeldingen nodig.
- **`test_boss.py`** bevat regressietests voor onder andere level-ups, het starten en stoppen van het baasgevecht, genezing per beurt, vluchten, de baasbeloning, verkennen, verdedigen en upgradegrenzen.

De belangrijkste spelinstellingen — zoals prijzen, genezing, levelbonussen en de level waarop de baas verschijnt — staan als constanten bovenaan `main.py`. Klasse-statistieken vind je in `KLASSEN`; de basiswaarden en beloningen van gewone vijanden staan in `VIJANDEN`. Voor nieuwe of aangepaste illustraties kun je terecht in `visuals.py`.

## Tests uitvoeren

```powershell
python -m unittest
```

Voer dit commando uit vanuit de map met de spelbestanden.
De tests maken een Tkinter-venster aan. Op systemen zonder grafische omgeving kan daarvoor een display nodig zijn.
