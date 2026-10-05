"""Schaalbare Canvas-illustraties, zonder externe afbeeldingen of pakketten."""

import math
import random


def landschap(canvas, breedte, hoogte, tijd=0):
    """Een gelaagd maanverlicht bos met stabiele, reproduceerbare details."""
    canvas.delete("landschap")
    def polygon(*punten, **opties):
        canvas.create_polygon(*punten, tags="landschap", outline="", **opties)

    for y in range(0, int(hoogte), 4):
        t = y / hoogte
        kleur = "#%02x%02x%02x" % (int(12 + 13*t), int(22 + 26*t), int(37 + 19*t))
        canvas.create_rectangle(0, y, breedte, y+4, fill=kleur, outline="", tags="landschap")
    rng = random.Random(27)
    for _ in range(65):
        x, y = rng.random()*breedte, rng.random()*hoogte*.48
        r = rng.choice([.6, .8, 1.2])
        canvas.create_oval(x-r, y-r, x+r, y+r, fill="#748fa3", outline="", tags="landschap")
    mx, my = breedte*.79, hoogte*.20
    for r, kleur in [(49, "#1c3344"), (39, "#294351"), (29, "#47616a"), (23, "#e6d8ab")]:
        canvas.create_oval(mx-r, my-r, mx+r, my+r, fill=kleur, outline="", tags="landschap")
    polygon(0, hoogte*.54, breedte*.12, hoogte*.25, breedte*.27, hoogte*.52,
            breedte*.44, hoogte*.24, breedte*.63, hoogte*.57,
            breedte*.86, hoogte*.29, breedte, hoogte*.50, breedte, hoogte, 0, hoogte, fill="#203745")
    polygon(0, hoogte*.67, breedte*.20, hoogte*.44, breedte*.37, hoogte*.68,
            breedte*.64, hoogte*.39, breedte, hoogte*.62, breedte, hoogte, 0, hoogte, fill="#234149")
    for laag, kleur in [(0, "#24464b"), (1, "#193a3d"), (2, "#112f33")]:
        for i in range(19):
            x = (i/18)*breedte + rng.uniform(-20, 20)
            basis = hoogte*(.64+laag*.09)
            h = rng.uniform(.13, .31)*hoogte
            canvas.create_rectangle(x-3, basis-h*.2, x+3, basis+10, fill=kleur, outline="", tags="landschap")
            for j in range(3):
                top = basis-h+j*h*.20
                radius = h*(.23+j*.06)
                polygon(x, top, x-radius, top+h*.48, x+radius, top+h*.48, fill=kleur)
    polygon(0, hoogte*.86, breedte*.26, hoogte*.74, breedte*.50, hoogte*.83,
            breedte*.77, hoogte*.73, breedte, hoogte*.83, breedte, hoogte, 0, hoogte, fill="#1b3735")
    polygon(breedte*.51, hoogte*.66, breedte*.57, hoogte*.66, breedte*.71, hoogte,
            breedte*.33, hoogte, fill="#34443d")
    polygon(breedte*.53, hoogte*.66, breedte*.55, hoogte*.66, breedte*.61, hoogte,
            breedte*.45, hoogte, fill="#3c4b42")
    for _ in range(75):
        x, y = rng.random()*breedte, rng.uniform(.82, 1)*hoogte
        canvas.create_line(x, y, x-3, y-5, fill=rng.choice(["#345448", "#45604d", "#284b41"]), tags="landschap")
    for x, h in [(-8, .76), (breedte*.09, .55), (breedte*.94, .66), (breedte+4, .85)]:
        basis = hoogte*.97
        canvas.create_rectangle(x-8, basis-h*hoogte, x+8, basis, fill="#11282c", outline="", tags="landschap")
        for j in range(4):
            top = basis-h*hoogte+j*hoogte*.095
            radius = hoogte*(.08+j*.035)
            polygon(x, top, x-radius, top+hoogte*.25, x+radius, top+hoogte*.25, fill="#102c30")
    for i in range(16):
        x = rng.uniform(.12, .89)*breedte
        y = rng.uniform(.53, .90)*hoogte + math.sin(tijd+i)*3
        canvas.create_oval(x-1.5, y-1.5, x+1.5, y+1.5, fill="#b9c987", outline="", tags="landschap")


def baas_balk(canvas, breedte, vijand, schaduwvuur=False, genezing=12):
    """Een brede baasindicator boven de bomen; blijft leesbaar bij schalen."""
    links, rechts = breedte * .18, breedte * .82
    tag = "baas_hud"
    canvas.create_rectangle(links-16, 12, rechts+16, 114, fill="#1e202b",
                            outline="#ae795e", width=2, tags=tag)
    canvas.create_text(breedte/2, 30, text="NACHTVORST  ·  HEERSER VAN HET MAANWOUD",
                       fill="#f2c66d", font=("Segoe UI", 12, "bold"), tags=tag)
    canvas.create_rectangle(links, 46, rechts, 66, fill="#382b36",
                            outline="#79555b", tags=tag)
    verhouding = max(0, min(1, vijand["hp"] / vijand["max_hp"]))
    if verhouding:
        canvas.create_rectangle(links+2, 48, links+2+(rechts-links-4)*verhouding, 64,
                                fill="#e48b63" if vijand["woedend"] else "#bf5e70",
                                outline="", tags="baas_hp")
    canvas.create_text(breedte/2, 56, text=f"{vijand['hp']} / {vijand['max_hp']} HP",
                       fill="#fff0de", font=("Segoe UI", 9, "bold"), tags=tag)
    fase = "WOEDEND  ·  2× schade" if vijand["woedend"] else "FASE I  ·  De schaduw ontwaakt"
    waarschuwing = "SCHADUWVUUR: VOLGENDE BEURT!" if schaduwvuur else "Schaduwvuur elke derde beurt"
    canvas.create_text(breedte/2, 83, text=f"{fase}   |   {waarschuwing}",
                       fill="#ffbd86" if schaduwvuur else "#c6afaa",
                       font=("Segoe UI", 9), tags=tag)
    canvas.create_text(breedte/2, 102, text=f"ZELFGENEZING  +{genezing} HP / beurt",
                       fill="#83c98a", font=("Segoe UI", 9), tags=tag)


def personage(canvas, x, y, soort, schaal=1):
    """Teken een held of monster in lokale coördinaten."""
    tag = "personage"
    def punten(coords):
        return [v for a, b in zip(coords[::2], coords[1::2]) for v in (x+a*schaal, y+b*schaal)]
    def poly(coords, kleur, rand=""):
        canvas.create_polygon(*punten(coords), fill=kleur, outline=rand, width=2, tags=tag)
    def oval(coords, kleur, rand=""):
        canvas.create_oval(*punten(coords), fill=kleur, outline=rand, width=2, tags=tag)
    def lijn(coords, kleur, dikte=3):
        canvas.create_line(*punten(coords), fill=kleur, width=dikte*schaal, capstyle="round", tags=tag)

    oval([-34, -5, 34, 8], "#102726")
    if soort in ("Krijger", "Magiër", "Sluipmoordenaar"):
        magie = soort == "Magiër"
        sluip = soort == "Sluipmoordenaar"
        mantel = "#7766a5" if magie else "#314553" if sluip else "#a34f4d"
        poly([-15,-69, 12,-69, 28,-9, -30,-9], mantel)
        poly([-14,-59, 13,-59, 17,-27, -17,-27], "#343d58" if magie else "#72909d")
        poly([-14,-58, 0,-52, 13,-58, 8,-33, -9,-33], "#576988" if magie else "#9cb1b7")
        lijn([-8,-26,-9,-4], "#27323b", 9)
        lijn([8,-26,10,-4], "#27323b", 9)
        lijn([-13,-2,-5,-2], "#78868b", 5)
        lijn([6,-2,15,-2], "#78868b", 5)
        oval([-12,-88,12,-64], "#d4ad86")
        if magie:
            poly([-20,-83, 3,-117, 16,-83], "#7c71b1")
            ligne = [23,-8,27,-91]
            lijn(ligne, "#b4976c", 4)
            oval([18,-104,36,-86], "#3c5e77")
            oval([22,-100,32,-90], "#99dfdf")
            lijn([13,-53,25,-43], "#d4ad86", 6)
        elif sluip:
            poly([-15,-73,-13,-91,0,-99,14,-88,14,-73,0,-81], "#344654")
            poly([-12,-74,12,-74,8,-65,-8,-65], "#344654")
            lijn([15,-52,24,-37], "#758d99", 6)
            poly([23,-43,40,-64,33,-36], "#d4dfe1")
        else:
            poly([-14,-78,-12,-92,0,-98,13,-91,14,-78,3,-84], "#a0b6bf")
            lijn([0,-94,0,-83], "#d7e1de", 2)
            lijn([16,-56,25,-39], "#9cb1b7", 8)
            lijn([27,-22,34,-74], "#d6e4df", 5)
            lijn([19,-34,37,-31], "#dfb878", 4)
            poly([-30,-56,-13,-60,-11,-31,-22,-21,-33,-35], "#486577", "#b7c7c4")
            lijn([-23,-52,-21,-30], "#dfb878", 2)
        lijn([-14,-27,14,-27], "#be9c64", 4)
        oval([-3,-30,3,-24], "#f0d494")
    elif soort in ("Draak", "Nachtvorst"):
        baas = soort == "Nachtvorst"
        vleugel = "#493d62" if baas else "#8c4e55"
        huid = "#655473" if baas else "#ab615a"
        rand = "#d7a872" if baas else "#ca7b68"
        if baas:
            oval([-68,-126,68,7], "#29303e")
            poly([-20,-76,-34,-104,-32,-40], "#d7a872")
            poly([20,-76,35,-104,32,-40], "#d7a872")
        poly([-14,-68,-69,-122,-62,-53,-33,-29], vleugel, rand)
        poly([9,-70,60,-121,70,-57,34,-28], vleugel, rand)
        lijn([-16,-68,-60,-104], "#bf7666", 2)
        lijn([15,-68,59,-103], "#bf7666", 2)
        poly([19,-22,67,-11,84,-38,75,-5,35,2], huid)
        oval([-31,-80,31,-8], huid)
        oval([-17,-63,17,-12], "#ae8a79" if baas else "#d49c79")
        poly([-25,-64,-29,-101,-5,-115,23,-100,31,-72,12,-61], huid if baas else "#be7564")
        poly([-23,-100,-29,-120,-12,-109], "#ded0a2")
        poly([13,-106,29,-122,25,-98], "#ded0a2")
        ligne = [-22,-7,-35,-3]
        lijn(ligne, "#be7564", 10)
        lijn([21,-8,34,-3], "#be7564", 10)
        oval([-18,-95,-9,-87], "#f9d67a")
        oval([7,-95,16,-87], "#f9d67a")
        lijn([-17,-76,17,-76], "#5b343d", 3)
        if baas:
            poly([-22,-110,-27,-135,-10,-123,0,-138,10,-123,27,-135,22,-109],
                 "#d7a872", "#f4d699")
            oval([-4,-126,4,-118], "#b34e67")
            for hoogte in (-54, -40, -26):
                lijn([-9,hoogte,9,hoogte], "#796277", 2)
    else:
        orc = soort == "Orc"
        huid = "#789071" if orc else "#8ca775"
        poly([-22,-67,-40,-83,-31,-57,25,-57,40,-83,21,-68], huid)
        oval([-24,-89,24,-51], huid)
        poly([-19,-53,18,-53,27,-17,-27,-17], "#775e49")
        poly([-14,-51,13,-51,14,-28,-15,-28], "#9b8060")
        lijn([-14,-17,-16,-3], huid, 10)
        lijn([14,-17,16,-3], huid, 10)
        lijn([-21,-47,-31,-27], huid, 9)
        lijn([23,-48,33,-30], huid, 9)
        lijn([34,-12,38,-65], "#907b59", 5)
        if orc:
            poly([31,-68,53,-76,52,-51,34,-53], "#a1ada9", "#cbd2bd")
            poly([-18,-56,-12,-66,-8,-55], "#ede0b7")
            poly([8,-55,12,-66,18,-56], "#ede0b7")
        else:
            poly([34,-44,42,-78,44,-41], "#c6d0ba")
        oval([-15,-76,-6,-69], "#edcb7c")
        oval([6,-76,15,-69], "#edcb7c")
        lijn([-11,-61,11,-61], "#3c493d", 2)
