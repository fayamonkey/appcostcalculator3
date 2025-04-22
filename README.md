# Code Line Counter & Effort Estimator

Eine Streamlit-Anwendung zur Analyse von Codebasen, Zählung von Code-Zeilen und Schätzung des Entwicklungsaufwands.

## Funktionen

- **Codebasis-Analyse**: Zählt Code-Zeilen in verschiedenen Programmiersprachen unter Ausschluss von Leerzeilen und Kommentaren
- **Dateityp-Statistik**: Zeigt Verteilung der Code-Zeilen nach Programmiersprache
- **Aufwandsschätzung**: Berechnet geschätzten Entwicklungsaufwand in Personenmonaten
- **Kostenberechnung**: Schätzt Entwicklungskosten basierend auf Teamgröße und Gehältern
- **Visualisierungen**: Bietet verschiedene Diagramme und Grafiken zur Analyse

## Installation

1. Klonen Sie das Repository:
```
git clone https://github.com/IhrBenutzername/code-line-counter.git
cd code-line-counter
```

2. Installieren Sie die erforderlichen Abhängigkeiten:
```
pip install -r requirements.txt
```

## Verwendung

1. Starten Sie die Streamlit-App:
```
streamlit run app.py
```

2. Öffnen Sie Ihren Browser und navigieren Sie zu `http://localhost:8501`

3. Geben Sie den Pfad zu Ihrem Projekt ein oder laden Sie eine ZIP-Datei hoch

4. Passen Sie bei Bedarf die Parameter für die Aufwandsschätzung an

5. Klicken Sie auf "Analysieren", um detaillierte Statistiken zu erhalten

## Berechnungsmethodik

Die Aufwandsschätzung basiert auf Branchenstandards und Erfahrungswerten:

- Kleine Projekte (< 5.000 Zeilen): ~150 Zeilen Code pro Entwickler pro Tag
- Mittlere Projekte (5.000-50.000 Zeilen): ~100 Zeilen Code pro Entwickler pro Tag
- Große Projekte (> 50.000 Zeilen): ~80 Zeilen Code pro Entwickler pro Tag

Diese Werte berücksichtigen nicht nur das reine Codieren, sondern auch Planung, Design, Dokumentation, Tests und Fehlerbehebung.

## Streamlit Cloud

Sie können diese App auch auf Streamlit Cloud deployen:

1. Forken Sie dieses Repository auf GitHub
2. Melden Sie sich bei [Streamlit Cloud](https://streamlit.io/cloud) an
3. Wählen Sie "New app" und verbinden Sie es mit Ihrem GitHub-Repository
4. Wählen Sie "app.py" als Hauptdatei aus

## Lizenz

MIT 