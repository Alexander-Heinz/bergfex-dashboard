gib mir ideen für hobbyprojekte mit langchain bzw deepagents
15s nachgedacht

Faustregel: LangChain für kompakte, kontrollierte Tool-Workflows; Deep Agents für längere Aufgaben mit Planung, Dateisystem, Memory und Subagents. Deep Agents bringt diese Fähigkeiten bereits als Harness mit. LangChain-Vergleich, Deep-Agents-Überblick

Gute Projektideen
Projekt	Idee	Stack	Schwierigkeit
PR Archaeologist	Analysiert Git-Historie, Issues und Code und erklärt, warum eine fragwürdige Stelle existiert	Deep Agents: Code-, Git- und Issue-Subagent	Mittel
Local Research OS	Nimmt ein Thema, erstellt Rechercheplan, sammelt Quellen, widerspricht sich selbst und erzeugt einen Report	Deep Agents: Planung, Filesystem, Subagents	Mittel
Incident Postmortem Agent	Verknüpft Logs, Deployments und Alerts zu Timeline, Root Cause und Actions	LangChain + strukturierter Output	Mittel
Repo Onboarding Agent	Erstellt Architekturübersicht, Glossar, relevante Einstiegspunkte und erste „Good First Issues“	Deep Agents	Leicht–mittel
SQL Investigation Agent	Untersucht eine Datenfrage iterativ, schreibt Queries und prüft Resultate auf Widersprüche	Deep Agents + read-only DB	Mittel
Agentic Benchmark Lab	Lässt mehrere Agent-Strategien dieselben Tasks lösen und vergleicht Kosten, Laufzeit und Qualität	LangChain/LangGraph	Schwer
Personal Learning Coach	Plant Lernziele, generiert Übungen, bewertet Antworten und merkt sich Schwächen	LangChain + Long-term Memory	Leicht–mittel
Dependency Upgrade Scout	Analysiert Changelogs und Code, prognostiziert Breaking Changes und erstellt einen Migrationsplan	Deep Agents	Mittel
Prompt Regression Tester	Erstellt automatisch Testfälle und bewertet Prompt-/Modelländerungen gegen frühere Runs	LangChain + LangSmith	Mittel
Home-Lab Operator	Diagnostiziert Docker-/Kubernetes-Probleme und schlägt Aktionen vor; Ausführung nur nach Freigabe	Deep Agents + Human-in-the-loop	Schwer
Meeting Decision Tracker	Extrahiert Entscheidungen, offene Fragen und Verantwortlichkeiten aus Transkripten	LangChain + Structured Output	Leicht
Contrarian News Researcher	Erstellt zu einer Behauptung Pro-, Contra- und Fact-Checker-Berichte	Deep Agents mit drei Subagents	Mittel

Meine drei Favoriten:

PR Archaeologist – tatsächlich nützlich und zeigt, weshalb agentische Suche mehr ist als RAG mit hübscher Schleife.
Agentic Benchmark Lab – hervorragendes Portfolio-Projekt für einen AI Engineer.
Dependency Upgrade Scout – klar begrenzbar, realer Nutzen und gut evaluierbar.

Für ein Wochenend-MVP würde ich den PR Archaeologist nehmen:

Eingabe: Repository + Datei/Funktion + Frage
Tools: git log, git blame, Code-Suche, optional GitHub Issues
Subagents: Codeanalyse, Historie, Issues
Ergebnis: strukturierter Report mit Evidenz und Unsicherheiten
Sicherheitsregel: ausschließlich read-only

Deep Agents unterstützt dafür passend Filesystem-Kontext, persistentes Memory und Subagents; Tool-Aufrufe können gestreamt und nachvollzogen werden. Memory, Streaming-Quickstart

Was ich vermeiden würde: noch ein „Chat with your PDF“. Das ist mittlerweile das Todo-App-Tutorial der LLM-Welt – pädagogisch okay, aber niemand muss Nummer 800.001 davon sehen.

kannst du hier nachschauen ob man vlt auf eines der projekte aufbauen kann? ODer macht es mehr Sinn ein neues zu starten?


https://github.com/Alexander-Heinz?tab=repositories
1m 54s nachgedacht

Ja. Du solltest vorhandene Komponenten wiederverwenden, aber nicht zwanghaft alles in ein altes Repo quetschen.

Meine Empfehlung

Baue einen Deep Research / Documentation Agent und verwende scrape-web-tool als Tool-Layer. Für den Agent selbst würde ich ein neues Repo starten, beispielsweise deep-research-agent.

Warum:

Das Repo stellt bereits fetch_page und search_docs über MCP bereit.
Dein aktuelles main.py implementiert den Agent-Loop noch manuell mit OpenAI-Tool-Calls.
Deep Agents kann Planung, Filesystem-Kontext, Memory und Subagents übernehmen. Deep Agents
Tool und Agent bleiben getrennt und unabhängig testbar.

Das wäre echtes Weiterbauen statt „ich habe LangChain über bestehenden Code gekippt und bete jetzt zur Dependency-Göttin“.

Bewertung deiner bestehenden Projekte
Bestehendes Repo	Mögliches Agent-Projekt	Eignung	Empfehlung
scrape-web-tool	Local Research OS / Dependency Scout	9/10	Neues Agent-Repo, MCP-Tool weiterverwenden
bergfex-dashboard + bergfex-scraper	Ski Trip Planning Agent	9/10	Direkt als Feature ergänzen
vdi_chatbot	Funding Application Copilot	8/10	Bestehendes Repo modernisieren
GenauTapi	Personal Learning Coach	7/10	Technisch passend, aber Fork beachten
Berliner-Luft	Environmental SQL Analyst	6/10	Möglich, Datenumfang aktuell etwas schmal
collaborative-coder	PR Archaeologist	3/10	Neues Repo; kaum relevante Überschneidung
LLM_Zoomcamp / Kurs-Repos	beliebiger Agent	2/10	Als Lernarchiv behalten
Zweitbeste Option: Bergfex Agent

Das ist wahrscheinlich das stärkste Portfolio-Gesamtprojekt, weil du schon Folgendes hast:

Datenpipeline für über 700 Skigebiete
BigQuery
FastAPI
React-Frontend
Tests, Docker und Terraform
ein sichtbares Endprodukt

Ergänzung:

„Finde mir für Samstag ein Gebiet unter drei Stunden Fahrt, mit viel Neuschnee, niedriger Lawinengefahr und mindestens 70 % geöffneten Pisten.“

Mögliche Tools:

search_resorts
query_snow_history
get_weather_forecast
get_avalanche_report
calculate_travel_time

Subagents:

Conditions Analyst
Safety Analyst
Travel Planner
Recommendation Critic

Das gehört direkt in das bestehende bergfex-dashboard: kleiner Python-Agent-Service beziehungsweise FastAPI-Endpoint plus eine neue UI-Seite. Kein drittes Bergfex-Repo – zwei reichen bereits, wir müssen aus dem Hobbyprojekt kein Behördenorganigramm machen.

VDI-Chatbot sinnvoll weiterentwickeln

Der vorhandene Chatbot hat bereits Hybrid Search, Evaluation, Elasticsearch, Monitoring und Docker. Das ist eine stärkere Grundlage als ein frischer RAG-Prototyp. Statt eines simplen FAQ-Bots könntest du daraus einen Funding Application Copilot machen:

Förderprogramm recherchieren
Voraussetzungen extrahieren
Projektidee auf Eignung prüfen
fehlende Angaben erkennen
Antragsskizze kritisieren
Aussagen mit Quellen belegen

Das wäre ein echter Sprung von „RAG antwortet“ zu „Agent erledigt einen mehrstufigen Prozess“.

Klares Urteil
Deep Agents lernen und saubere Architektur zeigen: neues deep-research-agent-Repo, das scrape-web-tool konsumiert.
Stärkstes sichtbares Portfolio-Projekt: Bergfex um einen Ski-Planungsagenten erweitern.
Schnellstes MVP: den manuellen Agent-Loop in scrape-web-tool/main.py durch LangChain oder Deep Agents ersetzen.
PR Archaeologist: komplett neu starten; keines deiner Repos ist dafür ein sinnvoller Kern.

Ich würde den Research Agent + bestehendes MCP-Tool wählen. Der Scope ist beherrschbar und zeigt Tooling, Orchestrierung, Subagents, Memory, strukturierte Artefakte und Evaluation, ohne dass du zuerst noch eine halbe Plattform bauen musst.

Bergfex agent find ich super. vielleicht könnte man noch weitere sinnvolle werte mit reinnehmen bzw externe APIs? Denk an maps (Fahrtzeit), Luftdaten, aktuelle Nachrichten, auslastung der Unterkünfte (booking.com oder ähnliches), aktuelle Ticketpreise, websuche (?)...?
3m 31s nachgedacht

Ja — aber der Mehrwert kommt nicht von möglichst vielen APIs, sondern von fünf erklärbaren Signalen: Schnee, Wetter, Anfahrt, Andrang und Gesamtkosten.

Sinnvolle Erweiterungen
Bereich	Werte	Quelle	Priorität
Anfahrt	Fahrzeit, Distanz, erwarteter Verkehr	OpenRouteService oder TomTom	Sehr hoch
Bergwetter	Neuschnee, Regen, Wind, Sicht, Gefriergrenze, Sonne	Open-Meteo	Sehr hoch
Sicherheit	Lawinenstufe, Höhenbereich, Exposition, Wetterwarnungen	EAWS/CAAML, Avalanche.report	Hoch
Andrang	Ferien, Wochenende, Verkehr, Events, Unterkunftsknappheit	OpenHolidays + weitere Signale	Hoch
Kosten	Skipass, Fahrt, Maut, Unterkunft	Resortshops + Booking	Mittel
Betrieb	Liftstatus, Sperrungen, kurzfristige Meldungen	Resortseiten/Websuche	Hoch
Luft	AQI, Feinstaub, Saharastaub, UV	Open-Meteo Air Quality	Optional
Webcam	Sicht, Bewölkung, Parkplatz-/Pistenandrang	Webcam + Visionmodell	Später
1. Anfahrt: unbedingt

Da dein Dashboard bereits Leaflet nutzt, würde ich zunächst OpenRouteService nehmen:

Fahrzeit und Distanz
Route als GeoJSON
passt direkt zu Leaflet/OpenStreetMap
Matrix-Abfrage für mehrere Skigebiete

Für realen und prognostizierten Verkehr wäre TomTom interessanter: Dessen Routing berücksichtigt aktuellen Verkehr und typische Geschwindigkeiten für Wochentag und Uhrzeit. TomTom Routing

Google Routes kann ebenfalls Traffic und Route-Matrizen, ist aber in Verbindung mit einer Leaflet-Karte wegen der aktuellen EEA-Nutzungsbedingungen kein automatischer No-Brainer; Teile der Routes-Ausgabe dürfen nicht mit beliebigen Karten kombiniert werden. Google EEA Terms

Wichtig: nicht alle 700 Resorts routen.

Luftlinie und bestehende Daten → Top 30
Routing-Matrix → Top 10
Detaillierte Route mit Verkehr → Top 3
2. Bergwetter statt normalem Wetter

Open-Meteo eignet sich sehr gut und bietet unter anderem:

Neuschnee und Schneehöhe
Regen
Gefriergrenze
Sichtweite
Windböen
gefühlte Temperatur
Sonnenscheindauer und UV
bis zu 16 Tage Vorhersage

Außerdem kannst du die Höhe explizit übergeben. Deshalb würde ich jedes Gebiet zweimal abfragen: Talstation und Bergstation. Ein einzelner Wetterpunkt für ein Gebiet mit 2.000 Metern Höhenunterschied wäre meteorologisches Würfeln. Open-Meteo Forecast API

Daraus lassen sich verständliche Werte ableiten:

powder_quality
rain_risk
wind_closure_risk
visibility_score
bluebird_score
snow_reliability
3. Crowd Pressure statt behaupteter Auslastung

Booking liefert keine echte prozentuale Hotelauslastung. Über die Demand API bekommst du verfügbare Unterkünfte und Preise für konkrete Reisedaten; Zugang erfordert allerdings Affiliate-ID und Token. Booking Demand API, Bulk Availability

Daher besser ehrlich benennen:

lodging_scarcity, nicht occupancy

Crowd Pressure könnte sich zusammensetzen aus:

Wochenende
Schulferien am Herkunftsort
Ferien und Feiertage in der Zielregion
verfügbare Unterkünfte
Preisniveau gegenüber Normalwert
Verkehr Richtung Resort
Neuschnee am Wochenende
lokale Events

Ferien und Feiertage liefert die offene OpenHolidays API.

Das ist sogar als kleines ML-Projekt interessant: Später könntest du den Crowd Score gegen Verkehr, Parkplatz-Webcams oder echte Wartezeiten kalibrieren.

4. Skipasspreise: sinnvoll, aber nervig

Eine einheitliche offene API für europäische Skipasspreise existiert praktisch nicht. Anbieter wie SKIDATA stellen Integrationen eher Partnern als Hobbyprojekten bereit.

Pragmatische Lösung:

nur für die Top-3-Gebiete recherchieren
offizielle Ticketshops als bevorzugte Quelle
Preis, Tariftyp, Datum und URL speichern
maximal 12–24 Stunden cachen
bei dynamischen Preisen immer „ab X €“ anzeigen
mittelfristig kleine Adapter je Shop-System bauen

Daraus entsteht:

value_score = offene_pisten_km / gesamtkosten

Gesamtkosten:

Skipass
Kraftstoff beziehungsweise Ladekosten
Maut
Unterkunft
optional Verleih
5. Websuche: ja, aber gezielt

Keine generische „News über Ischgl“-Suche. Das produziert überwiegend Marketingmarmelade.

Sinnvolle Suchziele:

kurzfristige Liftsperrungen
Straßen- und Passsperrungen
Sturmschäden
Events mit hohem Besucheraufkommen
geänderte Öffnungszeiten
aktuelle Ticketpreise

Dein vorhandenes scrape-web-tool passt perfekt:

Neues Tool search_web über Tavily oder Brave ergänzen.
Ergebnisse auf offizielle Resort-, Straßen- und Wetterdomains priorisieren.
Gefundene Seiten mit fetch_page extrahieren.
Nur Meldungen der letzten 72 Stunden berücksichtigen.
Jede Aussage mit Quelle und Aktualisierungszeit ausgeben.

Tavily unterstützt News-, Datums- und Domainfilter direkt. Tavily Search

6. Luftdaten: nett, aber kein Kernfeature

Open-Meteo liefert europäischen AQI, PM2.5, PM10, Ozon, Staub und UV. Air Quality API

Für Skifahrer sind vermutlich wichtiger:

UV-Index
Saharastaub
Sichtweite
Wind
Ozon bei empfindlichen Personen

Ich würde Luftqualität als optionales Nutzerprofil behandeln, nicht standardmäßig in den Hauptscore werfen.

7. Lawineninformationen

EAWS-Bulletins besitzen mit CAAML einen standardisierten Austauschstandard; einzelne Regionen wie avalanche.report stellen offene Daten bereit. CAAML EAWS, Avalanche.report Open Data

Aber bitte nicht als simplen Sicherheits-Score verstecken:

offizielle Warnstufe anzeigen
betroffene Höhenlagen und Hangrichtungen
Originalquelle verlinken
klar zwischen gesicherten Pisten und Freeride unterscheiden
Empfohlener Ablauf

Der Agent sollte nicht selbst rechnen. Python berechnet die transparenten Scores; der Agent recherchiert fehlende Informationen, prüft Widersprüche und erklärt die Empfehlung.

Ich würde diese Teilwerte einführen:

snow_score
weather_comfort_score
access_score
crowd_pressure
value_score
data_confidence

Der bestehende shred_score wird anschließend nur noch eine personalisierte Gewichtung daraus. Für einen Tagestrip zählt Anfahrt stärker, für ein Wochenende Unterkunft und Preis. So bleibt nachvollziehbar, weshalb ein Gebiet empfohlen wird.

Mein MVP-Schnitt

Zuerst implementieren:

Open-Meteo für Tal und Berg
OpenRouteService für Fahrzeit
OpenHolidays für Crowd Pressure
gezielte Websuche für Sperrungen und Meldungen
data_confidence mit Quelle und Aktualität

Danach Booking und Skipasspreise. Webcam-Auswertung wäre anschließend das visuell beeindruckende Bonusfeature — aber nicht bevor die eigentliche Empfehlung zuverlässig funktioniert.

ich dachte eher an einen chatbot-agenten, den man optional statt des dashboards nutzt, und der bei Angabe des derzeitigen Standortes und weiteren Bedürfnissen dir die passendsten Gebiete im Dashboard rausfiltert oder direkt im Chat ausgibt - booking auch eher dann aktuelle Unterkunftspreise bei Angabe von Vorstellungen (zb. "hostel" oder "3bettzimmer mit kind") ausgibt, und preise der gebiete können direkt im bergfex gescraped werden und sind dann in meiner DB verfügbar. 

Es muss halt mehr können als chatgpt schon kann, das ist der Mehrwert.
1m 14s nachgedacht

Ja — so ergibt es deutlich mehr Sinn. Ich hatte den Agenten vorher zu sehr als Dashboard-Feature gedacht. Eigentlich baust du einen vertikalen Ski-Trip-Optimizer mit Chat-Interface, wobei das Dashboard nur eine mögliche Darstellung ist.

Der echte Mehrwert gegenüber ChatGPT
Normales ChatGPT	Dein Bergfex-Agent
findet einige bekannte Gebiete per Websuche	vergleicht systematisch alle ~700 Gebiete
kennt Preise und Öffnung oft nur ungefähr	nutzt normalisierte, zeitgestempelte DB-Daten
schätzt Entfernungen	berechnet Fahrzeiten vom aktuellen Standort
liefert allgemeine Hotelvorschläge	sucht verfügbare Zimmer für exakte Gäste- und Reisedaten
schreibt Empfehlungen	filtert und öffnet das Dashboard direkt
ignoriert harte Constraints gelegentlich	garantiert Budget-, Fahrzeit- und Personenvorgaben
beginnt bei jeder Nachricht neu	unterstützt Folgefragen und What-if-Vergleiche

Beispiel:

„Ich bin Freitag in München. Zwei Erwachsene und ein achtjähriges Kind, maximal drei Stunden Fahrt, mindestens 70 % offene Pisten und ein Hostel oder Dreibettzimmer unter insgesamt 600 €.“

Der Agent sollte darauf:

fehlende Daten erfragen, etwa Rückreisedatum,
alle Resorts in deiner DB filtern,
Fahrzeiten für die Shortlist berechnen,
konkrete Unterkünfte suchen,
Skipass- und Fahrtkosten berechnen,
die besten drei Optionen erklären,
optional das Dashboard auf genau diese Gebiete filtern.
Der wichtigste Agent-Workflow

Die LLM sollte dabei nicht rechnen oder frei SQL erzeugen. Sie versteht die Anfrage, wählt Tools und erklärt Ergebnisse. Filterung, Kosten und Ranking bleiben normaler, testbarer Python-Code.

Strukturierte Anfrage
origin
checkin / checkout
departure_at
adults
children_ages
skill_level
max_drive_minutes
budget_eur
accommodation_type
room_requirements
preferred_countries
priorities

Gerade children_ages ist wichtig: Ein „Kind“ hat je nach Unterkunft und Skigebiet überraschend viele semantische Zustände. Offenbar war „kleiner Mensch“ als Datenmodell zu unkompliziert.

Sinnvolle Tools
find_resorts(request)
filtert offene Gebiete, Pistenanteil, Schnee, Skill-Level und Budget
get_route_times(origin, resort_ids, departure_at)
zunächst nur für die besten 20–30 Kandidaten
search_accommodations(resort_id, dates, guests, preferences)
Hostel, Apartment, Dreibettzimmer, maximale Entfernung und Preis
calculate_trip_cost(resort_id, guests, route, stay)
Skipässe, Unterkunft, Fahrt und optional Maut
get_live_alerts(resort_ids)
kurzfristige Sperrungen und Betriebsinformationen
compare_resorts(resort_ids, priorities)
deterministischer Vergleich
apply_dashboard_filter(resort_ids, filters)
liefert eine URL oder strukturierte Frontend-Action
Booking richtig integrieren

Die Unterkunftssuche würde ich erst für die Top 5 ausführen. Sonst fragst du für hunderte Resorts Preise ab und verwandelst eine einfache Empfehlung in einen Lasttest.

Booking benötigt konkrete Angaben:

Check-in und Check-out
Erwachsene
Alter der Kinder
Anzahl Zimmer
Unterkunftstyp
optional Preislimit

Die Demand API liefert verfügbare Produkte, Preise und Gebühren, benötigt aber Affiliate-Zugang und Credentials. Booking Demand API

Wichtig:

„Dreibettzimmer mit Kind“ zunächst in Gäste und Kapazität übersetzen.
Zimmer nur empfehlen, wenn die strukturierte Belegung passt.
Preis als Gesamtpreis inklusive bekannter Gebühren zeigen.
Keine Belegung aus Beschreibungstexten halluzinieren.
Provider hinter einem AccommodationProvider-Interface kapseln.
Skipasspreise aus Bergfex

Das passt sehr gut in deine bestehende Pipeline. Ich würde nicht nur einen einzelnen Preis speichern:

resort_id
ticket_duration_days
age_group
price
currency
valid_from
valid_to
source_url
scraped_at

Dann kann der Agent echte Gruppenkosten berechnen. Falls nur Erwachsenenpreise vorhanden sind, zeigt er eine Spanne oder kennzeichnet Kinderpreise als unbekannt. Ein gescrapter Bergfex-Preis sollte außerdem als „gelisteter Preis“ bezeichnet werden, nicht automatisch als garantierter Checkout-Preis.

Agentische Funktionen, die wirklich nützlich sind

Besonders stark wären:

Constraint Relaxation:
„Unter 2 Stunden gibt es keinen Treffer. Bei 2:18 Stunden gäbe es zwei passende Gebiete.“
What-if-Fragen:
„Und wenn wir schon Freitagabend fahren?“
Der Agent verwendet den bisherigen Kontext und berechnet neu.
Pareto-Vergleich:
„A hat besseren Schnee, B ist 45 Minuten näher, C ist mit Unterkunft 120 € günstiger.“
Direkte Dashboard-Aktion:
Antwort enthält resort_ids, Kartenposition und aktive Filter.
Datenvertrauen:
Jede Empfehlung zeigt updated_at, fehlende Werte und einen Confidence-Wert.
Personalisierung:
Optional Heimatort, Fahrzeitlimit, Fahrkönnen und typische Gruppengröße merken.
Framework-Empfehlung

Für den MVP würde ich LangChain create_agent plus einen kleinen deterministischen Workflow verwenden, nicht sofort Deep Agents.

Der Ablauf ist klar und begrenzt. Deep Agents wäre erst interessant für offene Aufgaben wie:

„Plane mir das komplette Wochenende, recherchiere kurzfristige Sperrungen, vergleiche Unterkünfte und prüfe widersprüchliche Quellen.“

Planung und Subagents für jede normale Resortsuche wären hauptsächlich zusätzliche Kosten mit Agenten-Cosplay. LangChain ist für einen konfigurierbaren Tool-Agent gedacht; Deep Agents ergänzt unter anderem längere Planung, Filesystem und Subagents. Framework-Vergleich

Mein MVP
Chat-Panel im bestehenden Dashboard
strukturierte TripRequest
Resortfilter gegen BigQuery
Fahrzeitberechnung
Top-3-Empfehlungen mit Begründung
Button „Im Dashboard anzeigen“
Folgefragen wie „günstiger“, „näher“ oder „mehr Neuschnee“
danach Booking und Gesamtkosten






----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


gib mir ideen für hobbyprojekte mit langchain bzw deepagents
21s nachgedacht

Deep Agents lohnt sich vor allem für längere Aufgaben mit Planung, Dateien, Subagenten und Memory. Für einen simplen Tool-Calling-Bot reicht LangChain – sonst baust du einen Kleinwagen mit Flugzeugcockpit. Deep Agents basiert dabei auf LangGraph und bringt Persistenz, Streaming und Human-in-the-Loop mit. LangGraph

Meine besten Ideen:

Agent-Eval-Arena
Derselbe Aufgabensatz wird von create_agent, Deep Agents und einem eigenen LangGraph gelöst. Vergleiche Erfolgsrate, Kosten, Laufzeit und Tool-Fehler.
Lernwert: extrem hoch, weil du echte Agent-Reliability statt Demo-Magie untersuchst.
Repository Archaeologist
Analysiert fremde Repositories, erstellt Architekturübersichten, findet Dead Code und plant Änderungen. Subagenten übernehmen einzelne Module.
Deep-Agents-Fit: Filesystem, isolierte Subagenten, langer Kontext.
Incident Investigator
Bekommt Logs, Deployment-Diffs und Alerts. Erstellt Timeline, Hypothesen und evidenzbasierte Root-Cause-Analyse.
Extra: Jede Behauptung muss auf konkrete Logzeilen verweisen.
Documentation Gardener
Vergleicht Code, Tests und Dokumentation, erkennt veraltete Beispiele und schlägt minimale Patches vor. Änderungen erst nach Freigabe.
Claim Auditor
Zerlegt Blogposts oder Papers in überprüfbare Aussagen. Recherche-Agenten suchen Primärquellen und bewerten jede Aussage als belegt, widersprochen oder unklar.
Local Data Analyst
Untersucht SQLite-/Postgres-Daten, plant Abfragen, validiert SQL und erstellt einen Analysebericht. Schreibende Queries benötigen Human Approval – genau dafür unterstützt Deep Agents unterbrechbare Tool-Aufrufe. Human-in-the-Loop
Personal Learning Agent
Erstellt aus Dokumentationen und Repositories einen Lernplan, generiert Übungen und merkt sich Wissenslücken über Sessions hinweg.
Strategy-Game Master
Persistente Spielwelt mit NPC-, Economy- und Story-Subagenten. Entscheidungen verändern Dateien oder Datenbankzustand. Weniger nützlich, aber hervorragend zum Testen von Memory und widersprüchlichen Agentenzielen.
Home-Lab Operator
Analysiert Docker-Compose-Dateien, Logs und Servicezustände, schlägt Reparaturen vor und führt gefährliche Aktionen nur nach Bestätigung aus.
Agentic Wiki Maintainer
Baut aus einem Repository eine lebende Wiki, erkennt widersprüchliche Seiten, repariert Links und dokumentiert Änderungen. Ein ähnliches Muster existiert bereits als offizielles LLM-Wiki-Beispiel.

Meine Empfehlung: Agent-Eval-Arena oder Incident Investigator. Beide sind überschaubar, technisch interessant und deutlich portfolio-tauglicher als der 847. „Chatte mit deinem PDF“-Bot.

kannst du hier nachschauen ob man vlt auf eines der projekte aufbauen kann? ODer macht es mehr Sinn ein neues zu starten?


https://github.com/Alexander-Heinz?tab=repositories
4m 52s nachgedacht

Ja. Ein komplett neues Projekt wäre teilweise Verschwendung. Meine klare Empfehlung ist:

1. Beste Wahl: SnowPilot auf Bergfex aufbauen

Nutze bergfex-dashboard zusammen mit bergfex-scraper.

Der Agent könnte Fragen lösen wie:

„Finde drei offene Skigebiete maximal vier Stunden von München entfernt, mit mindestens 20 cm Neuschnee und Lawinenstufe ≤ 2. Berücksichtige den Trend der letzten Woche.“

Du hast bereits:

aktuelle Daten für über 700 Skigebiete
BigQuery und historische Messwerte
FastAPI-Backend
React-UI, Karten und Charts
eigenen Shred Score
Tests und Deployment

Das ergibt ein echtes Produkt statt „LLM ruft SQL auf und tut wichtig“.

Technischer Aufbau

Im bestehenden bergfex-dashboard ergänzen:

server/
├── services/resorts.py
├── tools/resorts.py
├── tools/weather.py
├── agent.py
└── server.py

Agent-Tools:

find_resorts(...)
get_resort_history(resort_id)
get_weather_forecast(latitude, longitude)
später estimate_travel_time(...)

Zunächst würde ich LangChains create_agent verwenden. Deep Agents lohnt sich erst, wenn mehrere Resorts parallel untersucht, Berichte geschrieben und Nutzerpräferenzen dauerhaft gespeichert werden. Genau diese Abgrenzung empfiehlt auch LangChain: normaler Agent für einen schlanken Tool-Loop, Deep Agents für Planung, Filesystem und Subagenten. LangChain-Übersicht

Vorher solltest du zwei Dinge reparieren:

server/server.py mischt BigQuery, Mapping und API-Logik in einer großen Datei.
Der Backend-Test erwartet ein Array, /api/resorts liefert aber ein Response-Objekt. Dein Test und deine API führen aktuell eine Fernbeziehung.
Weitere Kandidaten
Repository	Projektidee	Empfehlung
scrape-web-tool	Claim Auditor oder Repository Archaeologist	Neues Agent-Repo erstellen und dieses Repo als MCP-Tool weiterverwenden
vdi_chatbot	Förderantrags-Copilot	Neues Repo, aber FAQ-Daten, Scraper und Evaluation übernehmen
Berliner-Luft	Air-Quality Research Agent	Technisch solide Basis, aber Gefahr eines langweiligen Text-to-SQL-Wrappers
collaborative-coder	AI Pair Programmer	Cool, aber deutlich größer wegen sicherer Codeausführung und Agent-Sandbox
GenauTapi	Lernagent mit langfristigem Memory	Bereits ein Fork und schon nah am Agent-Thema; weniger geeignet für ein eigenständiges Portfolio-Projekt
Falls du explizit Deep Agents lernen willst

Dann wäre mein Favorit ein neues Grant Application Copilot-Repo:

Dokumente und Evaluation aus vdi_chatbot
Web-/Dokumentensuche über scrape-web-tool
Subagenten für Förderfähigkeit, Budget, Risiken und Quellenprüfung
Filesystem für Checklisten und Antragsentwürfe
Human Approval vor dem Schreiben finaler Dokumente

Das passt natürlicher zu den Deep-Agent-Fähigkeiten als ein einfacher Chatbot. Deep Agents

Kurz gesagt:

Bestes Gesamtprojekt: SnowPilot im bestehenden bergfex-dashboard
Schnellstes Deep-Agent-Projekt: neues Claim-Auditor-Repo mit scrape-web-tool
Tiefster Deep-Agent-Use-Case: neues Grant-Copilot-Repo mit Assets aus vdi_chatbot
Bergfex agent find ich super. vielleicht könnte man noch weitere sinnvolle werte mit reinnehmen bzw externe APIs? Denk an maps (Fahrtzeit), Luftdaten, aktuelle Nachrichten, auslastung der Unterkünfte (booking.com oder ähnliches), aktuelle Ticketpreise, websuche (?)...?
 Unter welchen Umständen macht deepagents sinn? 
2m 36s nachgedacht

Ja. Der Bergfex-Agent wird richtig interessant, sobald er nicht nur „viel Schnee = gut“ rechnet, sondern einen kompletten Wochenendtrip bewertet. Wichtig: Die Datenbeschaffung und Scores bleiben deterministischer Code; das LLM orchestriert und erklärt. Sonst lässt du GPT Fahrtzeiten würfeln – kreative Mobilitätsplanung.

Sinnvolle Daten, priorisiert
Signal	Umsetzung/API	Wert
Wetter auf Berg- und Talhöhe	Open-Meteo mit expliziter elevation	Sehr hoch
Fahrtzeit und Entfernung	Google Routes Matrix oder zunächst OpenRouteService	Sehr hoch
Verkehr, Straßensperren	Traffic-aware Google Routing oder TomTom Traffic Incidents	Hoch
Historischer Schneetrend	Eigene BigQuery-Daten	Sehr hoch
Lawinenbulletins	Offizielle regionale EAWS-Dienste/CAAML, zusätzlich zu Bergfex	Hoch, aber nur als Information
Aktuelle Betriebsstörungen	Websuche mit offiziellen Domains und Zeitfilter	Hoch
Ticketpreise	Offizielle Resortseiten, zunächst kuratierte Adapter	Mittel
Unterkunftspreise/-verfügbarkeit	Booking/Expedia API oder zunächst Deeplinks	Mittel
Luftqualität, Staub, UV	Open-Meteo Air Quality	Eher optional
Auslastung	Nur als Proxy aus Ferien, Events und Unterkunftsverfügbarkeit	Experimentell
Besonders wertvolle Wetterwerte

Open-Meteo liefert unter anderem Schneefall, Regen, Schneehöhe, Nullgradgrenze, Sichtweite, Windböen und gefühlte Temperatur. Außerdem kann die Prognose explizit auf Tal- beziehungsweise Bergstationshöhe heruntergerechnet werden. API-Parameter

Daraus kannst du einen besseren snow_quality_score berechnen:

Neuschnee der letzten und nächsten 48 Stunden
Regen auf bestehende Schneedecke
Nullgradgrenze relativ zur Tal- und Berghöhe
Freeze-thaw-Zyklen
Windverfrachtung und starke Böen
Sichtweite
Alter und Trend der Schneedecke
Aktualität der Daten

Das ist deutlich aussagekräftiger als „Schneehöhe 180 cm“. 180 cm Betonplatte mit Regen sind schließlich auch 180 cm – nur halt mit dem Charme eines Parkhauses.

Fahrtzeit

Für ein gegebenes Startziel zuerst die besten beispielsweise 30 Resorts aus BigQuery filtern und anschließend in einer einzigen Route-Matrix-Anfrage berechnen:

Startort × 30 Resorts → Fahrtzeit, Entfernung, Verkehr

Google kann aktuelle Verkehrsdaten berücksichtigen und teilweise Mautkosten liefern. Für einen günstigeren MVP reicht OpenRouteService, allerdings ohne dieselbe Live-Traffic-Qualität. TomTom wäre interessant, wenn Straßensperren und Verkehrsvorfälle ein zentrales Feature werden.

Zusätzliche Werte:

Ankunftszeit bei gewünschter Abfahrt
erwartete Rückfahrtzeit
Maut- und geschätzte Kraftstoffkosten
Winterbedingte Straßenvorfälle
Distanz vom Parkplatz zur Talstation, falls verfügbar
Unterkünfte: Vorsicht mit „Auslastung“

Booking.com hat eine offizielle Demand API für Preise und Verfügbarkeit. Zugang setzt aber eine Registrierung als Managed Affiliate Partner samt Vertrag und API-Zugang voraus. Booking-Voraussetzungen

Außerdem gilt:

Anzahl verfügbarer Booking-Unterkünfte ≠ tatsächliche Hotelauslastung.

Es ist lediglich ein brauchbarer Knappheitsindikator. Für den MVP würde ich:

Unterkünfte über Places in Resortnähe anzeigen.
Einen Deeplink mit vorausgefüllten Reisedaten erzeugen.
Preise und Verfügbarkeit erst integrieren, wenn du offiziellen API-Zugang bekommst.

Booking.com direkt zu scrapen würde ich nicht einplanen.

Ticketpreise

Hier gibt es keine brauchbare universelle öffentliche API. Viele Resorts verwenden dynamische Preise und unterschiedliche Shops.

Pragmatische Lösung:

zunächst nur Top-10- oder Top-20-Resorts
pro Resort ein Adapter für die offizielle Ticketseite
speichern: price, date, source_url, checked_at, confidence
fehlender Preis bleibt null und verlinkt zur Originalseite

Später kann dein vorhandenes scrape-web-tool als MCP-Service helfen. Das LLM darf Preise extrahieren, aber niemals ohne Quelle und Datum als Fakt ausgeben.

Aktuelle Nachrichten und Websuche

Keine allgemeine „News-Stimmung“ berechnen. Für die Fahrt nach Ischgl interessiert niemanden ein SEO-Artikel über die zehn schönsten Après-Ski-Socken.

Suche gezielt nach:

Lift- oder Gondelausfällen
Straßensperren
Sturmwarnungen
Großveranstaltungen und erwarteter Überfüllung
kurzfristigen Betriebseinschränkungen
offiziellen Lawinen- und Wetterwarnungen

Dafür eignen sich Brave News Search oder Tavily Search, jeweils mit:

maximal 72 Stunden Aktualität
bevorzugten offiziellen Domains
Quellenlinks
klarer Trennung zwischen offiziell bestätigt und unbestätigt
Wann Deep Agents sinnvoll ist
Aufgabe	Richtige Lösung
Scores aus Wetter, Fahrtzeit und Preisen berechnen	Normaler Python-Code
Nutzerfrage in Filter übersetzen und 3–5 Tools aufrufen	LangChain create_agent
Fester Ablauf mit kontrollierten Verzweigungen	Eigenes LangGraph
Längerer Trip-Research mit vielen Quellen, parallelen Resortanalysen und Bericht	Deep Agents

Deep Agents lohnt sich konkret, wenn mehrere dieser Bedingungen zutreffen:

10–30 Tool-Aufrufe pro Anfrage
der nächste Schritt hängt von Zwischenergebnissen ab
mehrere Resorts können parallel recherchiert werden
große Webseiten oder Dokumente müssen ausgelagert werden
widersprüchliche Quellen müssen verglichen werden
Berichte oder Reisepläne werden als Dateien erzeugt
Nutzerpräferenzen sollen über Sessions bestehen bleiben
der Lauf muss pausieren und fortgesetzt werden können
Aktionen wie Reservierungen benötigen Freigabe

Deep Agents bringt dafür Filesystem, Kontextkompression, Subagenten, Memory und Human-in-the-Loop bereits mit. Deep-Agents-Überblick

Meine Architektur-Empfehlung

Zwei Modi im bestehenden bergfex-dashboard:

Quick Match

Ein normaler LangChain-Agent:

Nutzerkriterien strukturiert extrahieren.
Resorts deterministisch vorfiltern.
Wetter und Fahrtzeiten abrufen.
Score berechnen.
Top-Ergebnisse erklären.

Ziel: wenige Sekunden.

Deep Trip Plan

Ein Deep Agent:

Deterministisch Top 10 bestimmen.
Für die besten 3–5 Resorts parallele Research-Subagenten starten.
Jeder prüft Wetter, Route, Preise, Unterkünfte und aktuelle Störungen.
Coordinator vergleicht die strukturierten Assessments.
Reiseplan mit Quellen, Kosten und Unsicherheiten erstellen.

So ist Deep Agents ein echtes Feature und keine teure Matroschka aus Agenten, die gemeinsam herausfinden, dass Sölden weit weg ist.

Meine Reihenfolge wäre:

Open-Meteo auf Tal- und Berghöhe plus neuer Snow-Quality-Score.
Route Matrix und Fahrtkosten.
Websuche für Betriebsstörungen.
Kuratierte Ticketpreis-Adapter.
Quick-Match-Agent.
Deep-Trip-Plan als separater Modus.
Unterkunfts-API erst bei offiziellem Zugang.
ich dachte eher an einen chatbot-agenten, den man optional statt des dashboards nutzt, und der bei Angabe des derzeitigen Standortes und weiteren Bedürfnissen dir die passendsten Gebiete im Dashboard rausfiltert oder direkt im Chat ausgibt - booking auch eher dann aktuelle Unterkunftspreise bei Angabe von Vorstellungen (zb. "hostel" oder "3bettzimmer mit kind") ausgibt, und preise der gebiete können direkt im bergfex gescraped werden und sind dann in meiner DB verfügbar. 

Es muss halt mehr können als chatgpt schon kann, das ist der Mehrwert. Denk dran, es soll ein offensichtlich agentisches Projekt sein, und nicht bloß ein Dashboard-Feature.
1m 24s nachgedacht

Du hast recht: Ich hatte es zu sehr als Dashboard-Feature gedacht. Eigentlich ist es ein Chat-first Ski-Trip-Agent; das Dashboard ist nur eine optionale Darstellung beziehungsweise Aktion des Agenten.

Der echte Mehrwert gegenüber ChatGPT

Nur einen LLM-Chat vor APIs zu hängen reicht nicht. ChatGPT kann ebenfalls googeln. Dein Agent gewinnt durch:

vollständige Suche über deine normalisierten 700+ Gebiete
historische und aktuelle Bergfex-Daten
exakte Routenberechnung vom Nutzerstandort
aktuelle, gruppenspezifische Ticketkosten aus deiner DB
echte Unterkunftsverfügbarkeit für konkrete Daten und Belegung
reproduzierbares Ranking statt frei formulierter Empfehlungen
iterative Anpassung: „billiger“, „näher“, „mehr für Anfänger“
direkte Aktion: passende Gebiete im Dashboard markieren und filtern
Quellen, Zeitstempel und Datenqualität für jede Empfehlung

Beispiel:

„Wir sind Freitag bis Sonntag unterwegs, zwei Erwachsene und ein achtjähriges Kind, maximal vier Stunden Fahrt, ein Dreibettzimmer unter 180 € pro Nacht und möglichst anfängerfreundlich.“

Der Agent:

Erkennt Standort, Zeitraum, Gruppe, Budget und Präferenzen.
Fragt nur fehlende Pflichtangaben nach.
Filtert alle Gebiete anhand deiner DB.
Berechnet Fahrtzeiten für die Vorauswahl.
Prüft Wetter, Liftbetrieb und Schneetrend.
Erkennt. Berechnet Skipasskosten für genau diese Gruppe.
Sucht passende verfügbare Unterkünfte.
Prüft offizielle Meldungen und Zufahrtsprobleme.
Gibt drei Empfehlungen mit Kosten und Trade-offs aus.
Kann dieselben Gebiete direkt im Dashboard anzeigen.

Das ist ein Agent. „Sortiere Gebiete nach Shred Score“ ist dagegen eine SQL-Abfrage mit Sprachkostüm.

Sinnvolle Tools
resolve_location(...)
shortlist_resorts(...)
get_route_matrix(...)
get_mountain_forecasts(...)
calculate_ticket_cost(...)
search_accommodations(...)
search_resort_alerts(...)
apply_dashboard_filters(...)
save_user_preferences(...)

Wichtig: Die Tools liefern typisierte Daten. Das LLM berechnet weder Preise noch Fahrtzeiten selbst.

Unterkunftsanfrage

Aus „Dreibettzimmer mit Kind“ muss der Agent eine strukturierte Anfrage erzeugen:

check_in
check_out
adults
children_ages
rooms
accommodation_types
max_total_price
max_distance_to_lift

Das Alter des Kindes muss er gegebenenfalls erfragen, weil Preise und erlaubte Zimmerbelegung davon abhängen.

Die Booking Demand API kann verfügbare Unterkünfte und aktuelle Preise liefern, benötigt aber den Zugang als Managed Affiliate Partner. Booking-Voraussetzungen, Accommodation Search

Ohne offiziellen Zugang würde ich Anbieter-Deeplinks anbieten, aber keine Booking-Seiten scrapen.

Skipasspreise

Deine DB sollte nicht nur ticket_price=63 speichern, sondern ungefähr:

resort_id
valid_date
product_type
duration_days
age_group
price
currency
source_url
scraped_at

Dann kann calculate_ticket_cost() beispielsweise zwei Erwachsene und ein achtjähriges Kind korrekt zusammenrechnen. Bei dynamischen Preisen sind Datum und Aktualität zwingend.

Chat und Dashboard verbinden

Der Agent sollte strukturiert antworten:

{
  "message": "Meine drei Empfehlungen ...",
  "recommended_resort_ids": ["abc", "def", "ghi"],
  "dashboard_filters": {
    "max_drive_minutes": 240,
    "open_only": true
  }
}

Die Chat-UI kann daraus Resort- und Unterkunftskarten rendern. „Im Dashboard anzeigen“ übernimmt anschließend IDs und Filter in die bestehende Ansicht.

Damit ist das Dashboard ein Werkzeug des Agenten – nicht der Agent ein angeklebter Chatbutton des Dashboards.

Wann Deep Agents hier Sinn ergibt

Für diese Produktidee würde ich zwei Ausführungspfade bauen:

Anfrage	Ausführung
„Zeig offene Gebiete maximal zwei Stunden entfernt“	normaler LangChain-Agent
„Plane unser Skiwochenende inklusive Unterkunft, Kosten und aktuellen Problemen“	Deep Agent

Der Deep Agent arbeitet dann so:

Coordinator erstellt einen Plan und bestimmt eine erste Auswahl.
Batch-Tools reduzieren 700 Gebiete deterministisch auf etwa zehn.
Für die besten drei bis fünf Gebiete laufen parallele resort_researcher-Subagenten.
Jeder untersucht Unterkunft, Preise, Wetter und aktuelle Meldungen.
Der Coordinator vergleicht strukturierte Ergebnisse und erzeugt den Reiseplan.

Deep Agents lohnt sich hier, weil die Recherche:

viele voneinander abhängige Tool-Aufrufe besitzt
Kandidaten parallel untersuchen kann
unvollständige oder widersprüchliche Quellen verarbeitet
längeren Kontext und Zwischenergebnisse erzeugt
nach Nutzerfeedback neu planen muss
Präferenzen über Sessions speichern kann

Genau dafür bringt Deep Agents Planung, isolierte Subagenten, Filesystem, Kontextkompression und Memory mit. Deep-Agents-Überblick

Damit es sichtbar agentisch wirkt

Im Chat nicht einfach einen Spinner anzeigen, sondern den Ablauf streamen:

✓ Anforderungen verstanden
✓ 742 Skigebiete durchsucht
✓ 18 Gebiete innerhalb der Fahrtzeit
◌ Wetter und Schneetrends vergleichen
◌ Unterkünfte für 5 Kandidaten prüfen
◌ Aktuelle Betriebsmeldungen verifizieren

Bei paralleler Recherche bekommt jedes Gebiet eine eigene Statuskarte. Das macht die Planung nachvollziehbar und zeigt den Agentencharakter, ohne ein Multi-Agenten-Puppentheater nur für die README zu veranstalten.

Mein Produktschnitt wäre daher:

/assistant: primäre Chat-Oberfläche
Quick Search mit normalem LangChain-Agent
Deep Trip Planning mit Deep Agents
strukturierte Ergebnis- und Unterkunftskarten
synchronisierte Dashboard-Filter
persistente Nutzerpräferenzen
vollständige Kosten: Unterkunft + Skipass + Fahrt/Maut
Quellen und Aktualitätszeitpunkt pro Ergebnis

Damit ist es nicht „ChatGPT mit Ski-Prompt“, sondern eine spezialisierte Such- und Optimierungsmaschine, die ChatGPT ohne deine Daten, Tools und Dashboard-Steuerung nicht reproduzieren kann.
