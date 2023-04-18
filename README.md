# Projekt IPP 2022/23
## Analyzátor kódu parse.php
Tento skript načítá ze standardního vstupu kód v jazyce IPPcode23, kontroluje jeho lexikální a syntaktickou správnost a vypisuje na standardní výstup jeho XML reprezentaci dle zadané specifikace.
### Spuštění
parse.php < [IPPCODE23] > [OUTPUT.xml]

### Nápověda
parse.php --help

## Interpret XML reprezentace kódu interpret.py
Tento interpret načítá ze souboru daného parameterem --source XML reprezentaci kódu jazyka IPPCode23.
### Spuštění
    > interpret.py [-h] [--source SOURCE] [--input INPUT]
    > -h, --help       show this help message and exit
    > --source SOURCE  File with XML representation of source code
    > --input INPUT    File with inputs for interpretation of source code

### Průběh programu
Interpret.py v první řadě zrpacuje parametry zadané z příkazové řádky a vytvoří k nim stručnou nápovědu (viz předchozí blok s nadpisem Spuštění). Následně za využití knihovny *xml.etree.ElementTree* postupně načítá jednotlivé XML elementy, kontroluje jejich sémantickou správnost a vytváří nové instance tříd *nstrukcí* a *argumentů*

### Objektový návrh
Tato implementace využívá pouze tři třídy, což se projevilo jako opravdu neoptimální řešení. Tyto třídy jsou *instruction*, *argument* a *variable*. Ve všech třídách používám protected konvenci jazyka Python.\
#### class instruction
- order - pořadí spuštění instrucke
- opcode - identifikuje, jaký příkaz instrukce reprezentuje
- args[] - pole až tří argumentů pro příkaz 
- get_type(), get_value() - gettery na získání hodnot z objektu

#### class argument
- arg_type - typ argumentu
- value - hodnota argumentu
- set_type(), set_value() - settery na přidání hodnot dp objektu
- get_type(), get_value() - gettery na získání hodnot z objektu

#### class variable
- name - název proměnné
- var_type - typ proměnné
- value = hodnota uložená v proměnné
- set_type(), set_value() - settery na přidání hodnot do objektu
    - setter na name není potřeba, jméno proměnné se přidává pouze při inicializaci proměnné a už se nemění
- get_name(), get_type(), get_value() - gettery na získání hodnot z objektu

### Funkce
Protože nevyužívám naplno OO přístupu, využívám velké řady funkcí. Zde je pár nejdůležitějších.
- interpret - stavový automat na interpretaci příkazů, volá funkce interpret_XY, kde XY je název příkazu. Tohle je krásný příklad kódu, který by byl kvalitnější OO. 
- add_arg2ins - přidá instrukci všechny argumenty, při zpětném pohledu mě teď napadá, že by to mohla být být moteoda třídy *instruction*


### Závěr
Na zažátku práce na tomto projektu jsem považoval objektově orientovaný přístup jako překážku, proto jsem také vytvořil pouze minímální návrh, ale nakonec musím uznat, že by mi kvalitní návrh ulehčil nejen samotné programování, ale i by zvýšeil celkovou čitelnost a kvalitu kódu. 