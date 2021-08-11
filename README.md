# SignalDatabase

Webová služba pro ukládání a analýzu signálů

# POŽADAVKY

Libovolné vývojové prostředí pro jazyk Python (program byl testován v prostředí Spyder).
Instalace následujícíh knihoven:

-numpy (pip install numpy)
-dash (pip install dash)
-dash_table (pip install dash-table)
-flask (pip install Flask)
-dash_html_components (pip install dash-html-components)
-dash_core_components (pip install dash-core-components)
-plotly (pip install plotly)
-werkzeug (pip install Werkzeug)
-pymongo (pip install pymongo)
-pandas (pip install pandas)
-scipy (pip install scipy)
-heartpy (pip install heartpy)

Služba se poté spouští otevřením a spuštěním skriptu app.py, který se nachází v kořenovém adresáři. Ke službě uživatel přistupuje přes 
webový prohlížeč na adrese localhost http://127.0.0.1:8050/

---------------------------------------------------------------------------------------------------------------------------------------

# OVLÁDÁNÍ ÚVODNÍ STRÁNKY

Úvodní stránka se skládá ze dvou záložek. „Search" slouží k procházení signálů uložených v databázi. „Upload signal" slouží k 
nahrávání signálů na lokální/mongoDB úložiště a jejich procházení. U lokálního úložiště se signály ukládají do složky signals, který se 
, pokud neexistuje, sám vytvoří v kořenovém adresáři aplikace.

Ovládací prvky v záložce Search:

Signal Source - Zde si uživatel vybírá zda si přeje načítat signál z lokálního úložiště, nebo cloudové databáze Atlas DB,
Find signals by - Zde si uživatel vybírá, podle kterých metadat chce signál vyhledávat.

Prazdný textový box slouží k zadávání výrazu, podle kterého si přeje uživatel signál vyhledávat. Po zobrazení tabulky a vypsání signálů 
stačí dvakrát kliknout na buňku v tabulce žádaného signálu, který se poté otevře v nové zálžce, kde je možné prováděť jeho vizualizaci.


Ovládací prvky v záložce Upload signal:

Import from MONGODB - Importuje všechny signály z cloudové databáze.
Delete Signal - Odstraní signál z databáze.
Open - Otevře signál k jeho zpracování.
Upload Signal - Slouží pro nahrávání signálů.
Edit Metadata - Slouží pro editaci metadat označeného signálu.

---------------------------------------------------------------------------------------------------------------------------------------

# OLÁDÁNÍ STRÁNKY S VIZUALIZACÍ

Tato stránska se skládá ze tří záložek. Original signal slouží k vizualizaci signálu, Filters slouží k aplikaci filtrů, Fourier transform 
slouží k zobrazení frekvenčního spektra.

Ovládací prvky v záložce Original signal:

Signal properties - Tato záložka zobrazuje vlastnosti signálu zásadních pro EMG analýzu
Annotations - Slouží pro přidávání anotací. Uživatel nejprve musí kliknout na bod v signálu, kam si přeje anotaci přidat. Label poté představuje
typ anotace. Notes představuje konrétní text u anotace uvedený. Po vyplnění údajů a kliknutí na „Add annotation to graph" se anotace vloží do grafu.
Pokud je uživatel s anotací spokojení, kliknutím na „Save annotation" se anotace uloží do signálu trvale.

Ovládací prvky v záložce Filters:

Lowpass - Aplikuje lowpass variaci na Butterwortha filtru 
Highpass - Aplikuje highpass variaci na Butterwortha filtru 
Bandpass - Aplikuje Bandpass variaci na Butterwortha filtru 
Bandstop - Aplikuje Bandstop variaci na Butterwortha filtru 
Filter channels - volba na který kanál chceme filtr aplikovat. Pokud prázdný, aplikuje se na všechny.
Filter order - přesnost filtru
