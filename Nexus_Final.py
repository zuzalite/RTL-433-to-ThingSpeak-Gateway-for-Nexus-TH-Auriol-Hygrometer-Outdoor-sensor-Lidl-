import sys
import re
import time
import requests

# ThingSpeak Beállítások
API_KEY = "xxxxxxxxxx"
CÉL_URL = "https://api.thingspeak.com/update.json"

print("--- PÁRATARTALOM KÜLDÉS (UNIVERZÁLIS API + IDŐZÍTŐ) INDUL ---", flush=True)

is_my_device = False
aktuális_pára = None
utolsó_küldés_ideje = 0  # Itt figyeljük, mikor küldtünk utoljára

for line in sys.stdin:
    clean_line = line.strip()
    
    # 1. Beazonosítjuk, ha a te konkrét eszközöd blokkja kezdődik (House Code: 91)
    if "model" in clean_line:
        if "Nexus-TH" in clean_line and re.search(r"House\s*Code\s*:\s*91", clean_line):
            is_my_device = True
        else:
            is_my_device = False
            
    # 2. Páratartalom kiszedése, ha a te eszközödről van szó
    if is_my_device and "Humidity" in clean_line:
        match = re.search(r"Humidity\s*:\s*([0-9]+)", clean_line)
        if match:
            érték = int(match.group(1))
            if 0 <= érték <= 100:
                aktuális_pára = érték
            
        # 3. Küldési kísérlet
        if amire_vagyunk := aktuális_pára is not None:
            mostani_idő = time.time()
            
            # CSAK AKKOR KÜLDÜNK, HA ELTELT LEGALÁBB 16 MÁSODPERC AZ UTOLSÓ SIKERES KÜLDÉS ÓTA!
            if mostani_idő - utolsó_küldés_ideje >= 16:
                paraméterek = {
                    'api_key': API_KEY,
                    'field1': aktuális_pára
                }
                try:
                    # A hivatalos update.json-ra küldjük el az adatot
                    res = requests.post(CÉL_URL, data=paraméterek, timeout=10)
                    
                    if res.status_code == 200:
                        print(f"[ThingSpeak SIKER] Páratartalom elmentve: {aktuális_pára}% | Entries száma növekedett!", flush=True)
                        utolsó_küldés_ideje = mostani_idő  # Frissítjük az időbélyeget, ha sikeres volt
                    else:
                        print(f"[ThingSpeak Elutasítva] Kód: {res.status_code}", flush=True)
                except Exception as e:
                    print(f"[ThingSpeak HIBA] Hálózati hiba: {e}", flush=True)
            else:
                # Ha még nem telt le a 16 másodperc, csendben kihagyjuk, hogy ne tiltsanak le
                print(f"[Időzítő] Adat észlelve ({aktuális_pára}%), de várunk a 15 másodperces korlát miatt...", flush=True)
            
            # Alaphelyzetbe állítás a következő adásig
            aktuális_pára = None
            is_my_device = False
