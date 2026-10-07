"""PNG-achtergronden en sprites voor het Tkinter Canvas."""

from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageTk


ASSETS = Path(__file__).resolve().parent / "assets"
SPRITES = {
    "Krijger": "krijger.png",
    "Magiër": "magier.png",
    "Sluipmoordenaar": "sluipmoordenaar.png",
    "Goblin": "goblin.png",
    "Orc": "orc.png",
    "Draak": "draak.png",
    "Nachtvorst": "nachtvorst.png",
    "Gouden Draak": "gouden_draak.png",
}
ACHTERGRONDEN = ("maanwoud_menu.png", "maanwoud_scene.png")
SPRITE_BREEDTE = 165
SPRITE_HOOGTE = 152
SPRITE_VOET = (75, 142)


@lru_cache(maxsize=16)
def _bronafbeelding(bestandsnaam):
    """Laad elke PNG eenmaal, onafhankelijk van de huidige werkmap."""
    with Image.open(ASSETS / bestandsnaam) as afbeelding:
        return afbeelding.convert("RGBA")


def _canvas_afbeelding(canvas, bestandsnaam, breedte, hoogte):
    """Bewaar PhotoImages op hun Canvas, zodat Tkinter ze niet opruimt."""
    cache = getattr(canvas, "_png_afbeeldingen", None)
    if cache is None:
        cache = canvas._png_afbeeldingen = {}
    grootte = (max(1, round(breedte)), max(1, round(hoogte)))
    vorige = cache.get(bestandsnaam)
    if vorige is None or vorige[0] != grootte:
        bron = _bronafbeelding(bestandsnaam)
        geschaald = bron.resize(grootte, Image.Resampling.LANCZOS)
        afbeelding = ImageTk.PhotoImage(geschaald, master=canvas)
        cache[bestandsnaam] = (grootte, afbeelding)
    return cache[bestandsnaam][1]


def landschap(canvas, breedte, hoogte, tijd=0):
    """Toon het maanwoud; kies de PNG die het beste bij het Canvas past."""
    canvas.delete("landschap")
    verhouding = max(1, breedte) / max(1, hoogte)
    bestandsnaam = min(
        ACHTERGRONDEN,
        key=lambda naam: abs(
            _bronafbeelding(naam).width / _bronafbeelding(naam).height - verhouding
        ),
    )
    afbeelding = _canvas_afbeelding(canvas, bestandsnaam, breedte, hoogte)
    canvas.create_image(0, 0, image=afbeelding, anchor="nw", tags="landschap")
    canvas.tag_lower("landschap")


def baas_balk(canvas, breedte, vijand, schaduwvuur=False, genezing=12):
    """Een brede baasindicator boven de bomen; blijft leesbaar bij schalen."""
    links, rechts = breedte * .18, breedte * .82
    tag = "baas_hud"
    canvas.create_rectangle(links - 16, 12, rechts + 16, 114, fill="#1e202b",
                            outline="#ae795e", width=2, tags=tag)
    canvas.create_text(breedte / 2, 30,
                       text=("GOUDEN DRAAK  ·  EINDBAAS VAN DE WILDERNIS" if vijand.get("eindbaas")
                             else "NACHTVORST  ·  HEERSER VAN HET MAANWOUD"),
                       fill="#f2c66d", font=("Segoe UI", 12, "bold"), tags=tag)
    canvas.create_rectangle(links, 46, rechts, 66, fill="#382b36",
                            outline="#79555b", tags=tag)
    verhouding = max(0, min(1, vijand["hp"] / vijand["max_hp"]))
    if verhouding:
        canvas.create_rectangle(links + 2, 48, links + 2 + (rechts - links - 4) * verhouding, 64,
                                fill="#e48b63" if vijand["woedend"] else "#bf5e70",
                                outline="", tags="baas_hp")
    canvas.create_text(breedte / 2, 56, text=f"{vijand['hp']} / {vijand['max_hp']} HP",
                       fill="#fff0de", font=("Segoe UI", 9, "bold"), tags=tag)
    fase = "WOEDEND  ·  2× schade" if vijand["woedend"] else "FASE I  ·  De schaduw ontwaakt"
    waarschuwing = "DRAKENVUUR: VOLGENDE BEURT!" if schaduwvuur else "Drakenvuur elke derde beurt"
    canvas.create_text(breedte / 2, 83, text=f"{fase}   |   {waarschuwing}",
                       fill="#ffbd86" if schaduwvuur else "#c6afaa",
                       font=("Segoe UI", 9), tags=tag)
    canvas.create_text(breedte / 2, 102, text=f"ZELFGENEZING  +{genezing} HP / beurt",
                       fill="#83c98a", font=("Segoe UI", 9), tags=tag)


def personage(canvas, x, y, soort, schaal=1):
    """Plaats een transparante sprite met zijn voeten op (x, y)."""
    if schaal <= 0:
        return
    bestandsnaam = SPRITES.get(soort, SPRITES["Goblin"])
    afbeelding = _canvas_afbeelding(
        canvas, bestandsnaam, SPRITE_BREEDTE * schaal, SPRITE_HOOGTE * schaal
    )
    canvas.create_image(
        x - SPRITE_VOET[0] * schaal,
        y - SPRITE_VOET[1] * schaal,
        image=afbeelding,
        anchor="nw",
        tags="personage",
    )
