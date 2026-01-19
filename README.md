# Škola Online CLI (Textual TUI)
Terminálová aplikace postavená na knihovně Textual pro rychlé prohlížení dat ze Škola Online (známky, rozvrh, zprávy, úkoly, chování) přes oficiální SOL API.

## Požadavky
- Python 3.10+ (ověřeno na Linux)
- Přístupové údaje do Škola Online

## Instalace
```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install textual requests
```

## Spuštění
```bash
python main.py
```
- Přihlašovací údaje se zadávají přímo v TUI (nezapisují se na disk).
- Ukončení kdykoli klávesou `q`.

## Co aplikace umí
- Známky: seznam s váhou a tématem.
- Rozvrh: aktuální týden s časy, předměty a učebnami.
- Zprávy: poslední přijaté/odeslané (směr IN/OUT).
- Úkoly: aktivní domácí úkoly s termínem.
- Chování: přehled událostí chování.

## Ladění
- Pokud je `DEBUG = True` v `main.py`, vytváří se soubor `debug.log` s informacemi o volání API a UI událostech.
- Chyby přihlášení nebo načítání se zobrazí jako notifikace v aplikaci.

## Známá omezení
- Aplikace je demonstrace; Neneseme za ní žádnou zodpovědnost.
- Struktura API se může měnit; při změnách může být nutný update endpointů.
