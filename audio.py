"""Kleine, gegenereerde avonturenmelodie voor Windows."""

import math
import struct
import tempfile
import wave
from pathlib import Path


class AchtergrondMuziek:
    """Speel een rustige, herhalende RPG-melodie zonder extra packages."""

    def __init__(self):
        self._winsound = None
        self._tijdelijke_map = None
        self._bestand = None

    def start(self):
        if self._winsound is None:
            try:
                import winsound
            except ImportError as fout:
                raise RuntimeError(
                    "Achtergrondmuziek is alleen beschikbaar op Windows."
                ) from fout
            self._winsound = winsound

        if self._bestand is None:
            self._tijdelijke_map = tempfile.TemporaryDirectory(prefix="mini-rpg-")
            self._bestand = Path(self._tijdelijke_map.name) / "avonturenmelodie.wav"
            self._maak_melodie(self._bestand)

        self._winsound.PlaySound(
            str(self._bestand),
            self._winsound.SND_FILENAME | self._winsound.SND_ASYNC | self._winsound.SND_LOOP,
        )

    def stop(self):
        if self._winsound is not None:
            self._winsound.PlaySound(None, 0)
        if self._tijdelijke_map is not None:
            self._tijdelijke_map.cleanup()
        self._tijdelijke_map = None
        self._bestand = None

    @staticmethod
    def _maak_melodie(bestand):
        sample_rate = 11025
        telduur = 0.72
        noten = (62, 69, 65, 69, 60, 67, 64, 67, 58, 65, 62, 65, 57, 64, 60, 64)
        akkoorden = ((50, 53, 57), (48, 52, 55), (46, 50, 53), (45, 48, 52))
        totale_tijd = len(noten) * telduur
        frames = bytearray()

        def frequentie(midi_noot):
            return 440 * 2 ** ((midi_noot - 69) / 12)

        for frame in range(round(sample_rate * totale_tijd)):
            tijd = frame / sample_rate
            tel = min(len(noten) - 1, int(tijd / telduur))
            tel_tijd = tijd % telduur
            noot_fase = 2 * math.pi * frequentie(noten[tel]) * tel_tijd
            noot_omhulsel = min(1.0, tel_tijd / 0.035) * max(0.0, 1 - tel_tijd / telduur)
            melodie = (math.sin(noot_fase) + 0.25 * math.sin(2 * noot_fase)) * noot_omhulsel

            akkoord_tijd = tijd % (telduur * 4)
            akkoord = akkoorden[tel // 4]
            akkoord_omhulsel = 0.55 + 0.45 * math.sin(
                math.pi * akkoord_tijd / (telduur * 4)
            )
            begeleiding = sum(
                math.sin(2 * math.pi * frequentie(midi_noot) * akkoord_tijd)
                for midi_noot in akkoord
            ) / len(akkoord)
            sample = 0.14 * melodie + 0.045 * akkoord_omhulsel * begeleiding
            sample = max(-1.0, min(1.0, sample))
            frames.extend(struct.pack("<h", round(sample * 32767)))

        with wave.open(str(bestand), "wb") as melodiebestand:
            melodiebestand.setnchannels(1)
            melodiebestand.setsampwidth(2)
            melodiebestand.setframerate(sample_rate)
            melodiebestand.writeframes(frames)
