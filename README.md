# Mapping Roth

Eine interaktive [OpenStreetMap](https://www.openstreetmap.org/)-Karte zu den
Romanen Joseph Roths. Erstes Werk: ***Das Spinnennetz*** (1923), Roths
Debütroman über den Aufstieg des Leutnants a. D. Theodor Lohse im Netz
nationalistischer Geheimbünde — Berlin, Potsdam und die Provinz im Krisenjahr.

- **Live:** <https://hermesj.github.io/mappingRoth/>
- **Engine:** **[litmap](https://github.com/hermesj/litmap)** (Konfiguration +
  Daten, keine Engine-Änderungen). Schwesterprojekte:
  [Mapping Joyce](https://hermesj.github.io/mappingJoyce/),
  [Mapping Perutz](https://hermesj.github.io/mappingPerutz/).
- Weitere Werke (etwa *Radetzkymarsch*) kommen als zusätzliche `works` in
  dieselbe `config.json`.

## Was die Karte zeigt

Die 30 Kapitel als farbige Ebenen, jeweils mit einer zeitlichen Einordnung
(März bis März des folgenden Jahres, mit dem fiktiven Umsturztag des
2. November als Höhepunkt). Jeder Ort trägt eine Glosse, ein wörtliches Zitat
und einen Link **„↗ im Kontext (Gutenberg)“**, der das Kapitel bei Projekt
Gutenberg-DE öffnet und die Stelle hervorhebt. Ein Personenregister listet die
Figuren mit ihren Orten. Ein Halo zeigt, wie sicher die Verortung ist
(*gesichert / straßengenau / hypothetisch*); erfundene Orte sind markiert.
Nur erwähnte Orte liegen auf einer ausgeblendeten eigenen Ebene.

> **Erste Fassung (experimentell).** Roth benennt kaum Straßen; viele Innenräume
> (die Villa Efrussi, Trebitschs Büro, das Haus des Prinzen) sind nur
> hypothetisch gesetzt. Offene Orte stehen in `data/spinnennetz-source.json`
> unter `_open`.

## Textgrundlage

*Das Spinnennetz* erschien 1923 als Fortsetzungsroman in der Wiener
*Arbeiter-Zeitung*. Der Text ist **gemeinfrei** (Roth † 1939; in den USA
veröffentlicht 1923). Der Volltext liegt in `text/raw/`, nach Projekt
Gutenberg-DE (Vorlage: Aufbau-Verlag 1984); siehe [`text/README.md`](text/README.md). Ein Abgleich mit dem
Erstdruck in der *Arbeiter-Zeitung* ist geplant.

## Daten bearbeiten

Alles liegt in einer Quelle, `data/spinnennetz-source.json` (Orte, Routen,
Personen); gerendert wird mit dem generischen Geocoder:

```bash
python3 pipeline/geocode_source.py data/spinnennetz-source.json data/spinnennetz.geojson
python3 text/code/verify_places.py      # Zitate + Link-Fragmente gegen den Text prüfen
python3 pipeline/check.py               # vor jedem Commit
```

Interaktiv: `python3 pipeline/annotate-ui/serve.py --port 8074`.

## Lokale Vorschau

```bash
python3 -m http.server 8084
# → http://localhost:8084/
```

## Lizenzen

- **Code** (`engine/`, `pipeline/`, `text/code/`) — MIT ([`LICENSE`](LICENSE), litmap).
- **Geodaten** (`data/`) — eigener Datensatz, **CC BY-NC 4.0**
  ([`data/NOTICE.md`](data/NOTICE.md)).
- **Quelltext** (`text/raw/`) — gemeinfrei ([`text/raw/NOTICE.md`](text/raw/NOTICE.md)).

Basemap © OpenStreetMap-Mitwirkende © CARTO; Koordinaten und Routen aus
OpenStreetMap (ODbL). Ein nicht-kommerzielles akademisches Projekt.
