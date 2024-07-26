import docx
from docx.enum.style import WD_STYLE_TYPE
from docx.shared import Pt

def add_heading(document, text, level):
    if level <= 9:  # Word supports up to 9 levels of headings
        document.add_paragraph(text, style=f'Heading {level}')
    else:
        document.add_paragraph(text, style='Normal')

def add_text(document, text):
    paragraph = document.add_paragraph(text)
    paragraph.style = document.styles['Normal']
    paragraph.paragraph_format.left_indent = Pt(36)  # Odsazení zleva pro lepší čitelnost

def create_document_structure():
    doc = docx.Document()

    add_heading(doc, "A Průvodní list", 1)
    add_heading(doc, "A.1 Identifikační údaje", 2)
    add_heading(doc, "A.1.1 Údaje o stavbě", 3)
    add_text(doc, "a) název stavby,")
    add_text(doc, "b) místo stavby – kraj, katastrální území, parcelní čísla pozemků, u budov adresa a čísla popisná, výčet pozemků s právem zákonné služebnosti, parcelní čísla pozemků zařízení staveniště,")
    add_text(doc, "c) předmět dokumentace – nová stavba nebo změna dokončené stavby, trvalá nebo dočasná stavba, účel užívání stavby.")
    
    add_heading(doc, "A.1.2 Údaje o zpracovateli dokumentace", 3)
    add_text(doc, "a) jméno, popřípadě jména a příjmení, obchodní firma, identifikační číslo osoby, bylo-li přiděleno, sídlo (fyzická osoba podnikající) nebo obchodní firma nebo název, identifikační číslo osoby, bylo-li přiděleno, sídlo (právnická osoba),")
    add_text(doc, "b) jméno, popřípadě jména a příjmení hlavního projektanta včetně čísla, pod kterým je zapsán v evidenci autorizovaných nebo registrovaných osob vedené Českou komorou architektů nebo Českou komorou autorizovaných inženýrů a techniků činných ve výstavbě, s vyznačeným oborem, popřípadě specializací jeho autorizace,")
    add_text(doc, "c) jména a příjmení projektantů jednotlivých částí dokumentace včetně čísla, pod kterým jsou zapsáni v evidenci autorizovaných nebo registrovaných osob vedené Českou komorou architektů nebo Českou komorou autorizovaných inženýrů a techniků činných ve výstavbě, s vyznačeným oborem, popřípadě specializací jejich autorizace,")
    add_text(doc, "d) jméno, popřípadě jména a příjmení autorizovaného zeměměřického inženýra včetně čísla položky, pod kterým je veden v rejstříku autorizovaných zeměměřických inženýrů u České komory zeměměřičů.")

    add_heading(doc, "A.2 Seznam vstupních podkladů", 2)

    add_heading(doc, "A.3 TEA – technicko-ekonomické atributy budov", 2)
    add_text(doc, "a) obestavěný prostor,")
    add_text(doc, "b) zastavěná plocha,")
    add_text(doc, "c) podlahová plocha,")
    add_text(doc, "d) počet podzemních podlaží,")
    add_text(doc, "e) počet nadzemních podlaží,")
    add_text(doc, "f) způsob využití,")
    add_text(doc, "g) druh konstrukce,")
    add_text(doc, "h) způsob vytápění,")
    add_text(doc, "i) přípojka vodovodu,")
    add_text(doc, "j) přípojka kanalizační sítě,")
    add_text(doc, "k) přípojka plynu,")
    add_text(doc, "l) výtah.")

    add_heading(doc, "A.4 Atributy stavby pro stanovení podmínek napojení a provádění činností v ochranných a bezpečnostních pásmech dopravní a technické infrastruktury", 2)
    add_text(doc, "a) hloubka stavby,")
    add_text(doc, "b) výška stavby,")
    add_text(doc, "c) předpokládaná kapacita počtu osob ve stavbě,")
    add_text(doc, "d) plánovaný začátek a konec realizace stavby.")

    add_heading(doc, "B Souhrnná technická zpráva", 1)
    add_heading(doc, "B.1 Celkový popis území a stavby", 2)
    add_text(doc, "a) základní popis stavby; u změny stavby údaje o jejím současném stavu, závěry stavebně technického, případně stavebně historického průzkumu a výsledky statického posouzení nosných konstrukcí,")
    add_text(doc, "b) charakteristika území a stavebního pozemku, dosavadní využití a zastavěnost území, poloha vzhledem k záplavovému území, poddolovanému území apod.,")
    add_text(doc, "c) údaje o souladu stavby s územně plánovací dokumentací a územními opatřeními nebo s cíli a úkoly územního plánování, a s požadavky na ochranu kulturně historických, architektonických, archeologických a urbanistických hodnot v území,")
    add_text(doc, "d) výčet a závěry průzkumů,")
    add_text(doc, "e) informace o nutnosti povolení výjimky z požadavků na výstavbu,")
    add_text(doc, "f) stávající ochrana území a stavby podle jiných právních předpisů, včetně rozsahu omezení a podmínek pro ochranu,")
    add_text(doc, "g) vliv stavby na okolní stavby a pozemky, ochrana okolí, vliv stavby na odtokové poměry v území, požadavky na asanace, demolice a kácení dřevin,")
    add_text(doc, "h) požadavky na maximální dočasné a trvalé zábory zemědělského půdního fondu nebo pozemků určených k plnění funkce lesa,")
    add_text(doc, "i) navrhovaná a vznikající ochranná a bezpečnostní pásma, rozsah omezení a podmínky ochrany podle jiných právních předpisů, včetně seznamu pozemků podle katastru nemovitostí, na kterých ochranné nebo bezpečnostní pásmo vznikne, bezpečnostní vzdálenost muničního skladiště s rizikem střepinového účinku určená podle jiného právního předpisu,")
    add_text(doc, "j) navrhované parametry stavby – například zastavěná plocha, obestavěný prostor, podlahová plocha podle jednotlivých funkcí (bytů, služeb, administrativy apod.), typ navržené technologie, předpokládané kapacity provozu a výroby,")
    add_text(doc, "k) limitní bilance stavby – potřeby a spotřeby médií a hmot, hospodaření se srážkovou vodou, celkové produkované množství, druhy a kategorie odpadů a emisí apod.,")
    add_text(doc, "l) požadavky na kapacity veřejných sítí komunikačních vedení a elektronického komunikačního zařízení veřejné komunikační sítě,")
    add_text(doc, "m) základní předpoklady výstavby – časové údaje o realizaci stavby, členění na etapy, věcné a časové vazby stavby, podmiňující, vyvolané a související investice,")
    add_text(doc, "n) základní požadavky na předčasné užívání staveb a zkušební provoz staveb, doba jejich trvání ve vztahu k dokončení a užívání stavby,")
    add_text(doc, "o) seznam výsledků zeměměřických činností podle jiného právního předpisu, pokud mají podle projektu výsledků zeměměřických činností vzniknout v souvislosti s povolením stavby.")

    add_heading(doc, "B.2 Urbanistické a základní architektonické řešení", 2)
    add_text(doc, "Urbanismus – kompozice prostorového řešení a základní architektonické řešení.")

    add_heading(doc, "B.3 Základní stavebně technické a technologické řešení", 2)
    add_heading(doc, "B.3.1 Celková koncepce stavebně technického a technologického řešení", 3)
    add_heading(doc, "B.3.2 Celkové řešení podmínek přístupnosti", 3)
    add_text(doc, "a) celkové řešení přístupnosti se specifikací jednotlivých části, které podléhají požadavkům na přístupnost, včetně dopadů předčasného užívání a zkušebního provozu a vlivu na okolí,")
    add_text(doc, "b) popis navržených opatření – zejména přístup ke stavbě, prostory stavby a systémy určené pro užívání veřejností,")
    add_text(doc, "c) popis dopadů na přístupnost z hlediska uplatnění závažných územně technických nebo stavebně technických důvodů nebo jiných veřejných zájmů.")
    add_heading(doc, "B.3.3 Zásady bezpečnosti při užívání stavby", 3)
    add_heading(doc, "B.3.4 Základní technický popis stavby", 3)
    add_text(doc, "a) popis stávajícího stavu,")
    add_text(doc, "b) popis navrženého stavebně technického a konstrukčního řešení.")
    add_heading(doc, "B.3.5 Technologické řešení – základní popis technických a technologických zařízení", 3)
    add_text(doc, "a) popis stávajícího stavu,")
    add_text(doc, "b) popis navrženého řešení,")
    add_text(doc, "c) energetické výpočty.")
    add_heading(doc, "B.3.6 Zásady požární bezpečnosti", 3)
    add_text(doc, "a) charakteristiky a kritéria pro stanovení kategorie stavby podle požadavků jiného právního předpisu – výška stavby, zastavěná plocha, počet podlaží, počet osob, pro který je stavba určena, nebo jiný parametr stavby, zejména světlá výška podlaží nebo délka tunelu apod.,")
    add_text(doc, "b) kritéria – třída využití, přítomnost nebezpečných látek nebo jiných rizikových faktorů, prohlášení stavby za kulturní památku.")
    add_heading(doc, "B.3.7 Úspora energie a tepelná ochrana budovy", 3)
    add_text(doc, "Zohlednění plnění požadavků na energetickou náročnost, úsporu energie a tepelnou ochranu budov.")
    add_heading(doc, "B.3.8 Hygienické požadavky na stavbu, požadavky na pracovní a komunální prostředí", 3)
    add_text(doc, "Zásady řešení parametrů stavby (větrání, osvětlení, proslunění, stínění, zásobování vodou, ochrana proti hluku a vibracím, odpady apod.) a vlivu stavby na okolí (vibrace, hluk, zastínění, prašnost apod.).")
    add_heading(doc, "B.3.9 Zásady ochrany stavby před negativními účinky vnějšího prostředí", 3)
    add_text(doc, "Protipovodňová opatření, ochrana před pronikáním radonu z podloží, před bludnými proudy, před technickou i přírodní seizmicitou, před agresivní a tlakovou podzemní vodou, před hlukem a ostatními účinky – vliv poddolování, výskyt metanu apod.")

    add_heading(doc, "B.4 Připojení na technickou infrastrukturu", 2)
    add_text(doc, "Napojovací místa technické infrastruktury, přeložky, křížení se stavbami technické a dopravní infrastruktury a souběhy s nimi v případě, kdy je stavba umístěna v ochranném pásmu stavby technické nebo dopravní infrastruktury, nebo je-li ohrožena bezpečnost, připojovací rozměry, výkonové kapacity a délky.")

    add_heading(doc, "B.5 Dopravní řešení", 2)
    add_text(doc, "Popis dopravního řešení, napojení území na stávající dopravní infrastrukturu, přeložky, včetně pěších a cyklistických stezek, doprava v klidu, řešení přístupnosti a bezbariérového užívání.")

    add_heading(doc, "B.6 Řešení vegetace a souvisejících terénních úprav", 2)

    add_heading(doc, "B.7 Popis vlivů stavby na životní prostředí a jeho ochrana", 2)
    add_text(doc, "a) vliv na životní prostředí a opatření vedoucí k minimalizaci negativních vlivů – zejména příroda a krajina, Natura 2000, omezení nežádoucích účinků venkovního osvětlení, přítomnost azbestu, hluk, vibrace, voda, odpady, půda, vliv na klima a ovzduší, včetně zařazení stacionárních zdrojů a zhodnocení souladu s opatřeními uvedenými v příslušném programu zlepšování kvality ovzduší podle jiného právního předpisu,")
    add_text(doc, "b) způsob zohlednění podmínek závazného stanoviska posouzení vlivu záměru na životní prostředí, je-li podkladem,")
    add_text(doc, "c) popis souladu záměru s oznámením záměru podle zákona o posuzování vlivů na životní prostředí, bylo-li zjišťovací řízení ukončeno se závěrem, že záměr nepodléhá dalšímu posuzování podle tohoto zákona,")
    add_text(doc, "d) v případě záměrů spadajících do režimu zákona o integrované prevenci základní parametry způsobu naplnění závěrů o nejlepších dostupných technikách nebo integrované povolení, bylo-li vydáno.")

    add_heading(doc, "B.8 Celkové vodohospodářské řešení", 2)
    add_text(doc, "Zejména zásobování stavby vodou, způsob zneškodňování odpadních vod, využití a nakládání se srážkovými vodami.")

    add_heading(doc, "B.9 Ochrana obyvatelstva", 2)
    add_text(doc, "Splnění základních požadavků z hlediska plnění úkolů ochrany obyvatelstva")
    add_text(doc, "a) způsob zajištění varování a informování obyvatelstva před hrozící nebo nastalou mimořádnou událostí,")
    add_text(doc, "b) způsob zajištění ukrytí obyvatelstva,")
    add_text(doc, "c) způsob zajištění ochrany před nebezpečnými účinky nebezpečných látek u staveb v zónách havarijního plánování,")
    add_text(doc, "d) způsob zajištění ochrany před povodněmi,")
    add_text(doc, "e) způsob zajištění soběstačnosti stavby pro případ výpadku elektrické energie u staveb občanského vybavení,")
    add_text(doc, "f) způsob zajištění ochrany stávajících staveb civilní ochrany v území dotčeném stavbou nebo staveništěm, jejich výčet, umístění a popis možného dotčení jejich funkce a provozuschopnosti.")

    add_heading(doc, "B.10 Zásady organizace výstavby", 2)
    add_text(doc, "a) napojení staveniště na stávající dopravní a technickou infrastrukturu,")
    add_text(doc, "b) ochrana okolí staveniště a požadavky na související asanace, demolice, demontáž, dekonstrukce a kácení dřevin apod.,")
    add_text(doc, "c) vstup a vjezd na stavbu, přístup na stavbu po dobu výstavby, popřípadě přístupové trasy, včetně požadavků na obchozí trasy pro osoby s omezenou schopností pohybu nebo orientace a způsob zajištění bezpečnosti provozu,")
    add_text(doc, "d) maximální dočasné a trvalé zábory pro staveniště,")
    add_text(doc, "e) požadavky na ochranu životního prostředí při výstavbě – zejména opatření k minimalizaci dopadů při provádění stavby na životní prostředí, popis přítomnosti nebezpečných látek při výstavbě, předcházení vzniku odpadů, třídění materiálů pro recyklaci za účelem materiálového využití, včetně popisu opatření proti kontaminaci materiálů, stavby a jejího okolí, opatření při nakládání s azbestem, opatření na snížení hluku ze stavební činnosti a opatření proti prašnosti,")
    add_text(doc, "f) zásady bezpečnosti a ochrany zdraví při práci na staveništi,")
    add_text(doc, "g) bilance zemních prací, požadavky na přísun nebo deponie zemin,")
    add_text(doc, "h) limity pro užití výškové mechanizace,")
    add_text(doc, "i) požadavky na postupné uvádění stavby do provozu (užívání), požadavky na průběh a způsob přípravy a realizace výstavby a další specifické požadavky,")
    add_text(doc, "j) návrh fází výstavby za účelem provedení kontrolních prohlídek,")
    add_text(doc, "k) dočasné objekty.")

    add_heading(doc, "C Situační výkresy", 1)
    add_heading(doc, "C.1 Situační výkres širších vztahů", 2)
    add_text(doc, "a) zákres stavby a jejího napojení na dopravní a technickou infrastrukturu,")
    add_text(doc, "b) vyznačení hranic stavebních pozemků nebo částí pozemků stavby.")

    add_heading(doc, "C.2 Katastrální situační výkres", 2)
    add_text(doc, "a) zákres stavebních pozemků nebo jejich částí a navrhované stavby na podkladu katastrální mapy,")

    add_heading(doc, "C.3 Koordinační situační výkres", 2)
    add_text(doc, "a) měřítko maximálně 1 : 200; u změny stavby, která je kulturní památkou a u stavby v památkové rezervaci nebo v památkové zóně v měřítku 1 : 200,")
    add_text(doc, "b) stávající stavby, dopravní a technická infrastruktura,")
    add_text(doc, "c) hranice pozemků, parcelní čísla,")
    add_text(doc, "d) hranice řešeného území,")
    add_text(doc, "e) stávající výškopis a polohopis,")
    add_text(doc, "f) stanovení nadmořské výšky prvního nadzemního podlaží u budov (± 0, 00) a výšky upraveného terénu; maximální výška staveb,")
    add_text(doc, "g) vyznačení jednotlivých navržených nebo odstraňovaných staveb a technické infrastrukturyvčetně napojení stavby na technickou infrastrukturu,")
    add_text(doc, "h) navrhované komunikace a zpevněné plochy, napojení na dopravní infrastrukturu,")
    add_text(doc, "i) řešení vegetace,")
    add_text(doc, "j) okótované odstupy,")
    add_text(doc, "k) maximální dočasné a trvalé zábory,")
    add_text(doc, "l) hranice staveniště s vyznačením vjezdu,")
    add_text(doc, "m) odstupové vzdálenosti včetně vymezení požárně nebezpečných prostorů, přístupové komunikace a nástupní plochy pro požární techniku a zdroje požární vody.")

    add_heading(doc, "C.4 Speciální výkresy", 2)
    add_text(doc, "Situační výkresy vyhotovené ve vhodném měřítku zobrazující speciální požadavky objektů, technologických zařízení, technických sítí, infrastruktury nebo souvisejících inženýrských opatření, včetně přístupnosti staveb a prvků životního prostředí – soustava chráněných území Natura 2000, územní systém ekologické stability, významné krajinné prvky, zvláště chráněná území apod. Stávající, navrhovaná a vznikající ochranná a bezpečnostní pásma, památkové rezervace, památkové zóny apod. Vyznačení pozemků s právem zákonné služebnosti a věcných břemen. Vyznačení území, kde budou provedeny geotechnické sondy. Situace zásad organizace výstavby včetně vymezení prostorů se zakázanou manipulací a obchozích tras pro osoby s omezenou schopností pohybu nebo orientace.")

    add_heading(doc, "C.5 Dělení nebo scelení pozemků", 2)
    add_text(doc, "Celková situace v měřítku katastrální mapy, včetně parcelních čísel, se zakreslením požadovaného dělení nebo scelení pozemků s vyznačením přímého přístupu z veřejné komunikace ke všem pozemkům, nebo přes pozemek nebo stavbu stejného vlastníka, anebo na základě jiného věcného práva k cizímu pozemku nebo stavbě.")

    add_heading(doc, "D Dokumentace objektů", 1)
    add_heading(doc, "D.1 Stavební a technologická část", 2)
    add_heading(doc, "D.1.1 Architektonicko – stavební řešení", 3)
    add_heading(doc, "D.1.1.1 Technická zpráva", 4)
    add_text(doc, "Zejména základní architektonické řešení, stavebně technické řešení, provozní řešení, požadavky na technické vlastnosti stavby a podmínky přístupnosti.")
    add_heading(doc, "D.1.1.2 Výkresová část", 4)
    add_heading(doc, "D.1.1.2.1 Charakteristické půdorysy", 5)
    add_text(doc, "Půdorysy všech podlaží se zohledněním statických prvků konstrukce a s popisem funkčních ploch.")
    add_heading(doc, "D.1.1.2.2 Charakteristické řezy", 5)
    add_text(doc, "Typický svislý řez vedený schodištěm nebo řezy zejména s návazností na stávající zástavbu a s ohledem na hloubku založení navrhované stavby a staveb stávajících.")
    add_heading(doc, "D.1.1.2.3 Základní pohledy", 5)
    add_text(doc, "Základní pohledy včetně pohledů dokumentujících začlenění stavby do stávající zástavby nebo krajiny.")

    add_heading(doc, "D.1.2 Technologické řešení", 3)
    add_heading(doc, "D.1.2.1 Technická zpráva", 4)
    add_text(doc, "Zejména základní popis a skladba technických a technologických zařízení, základní popis procesu výroby, údaje o spotřebě energií, vody a jiných medií.")
    add_heading(doc, "D.1.2.2 Výkresová část", 4)
    add_heading(doc, "D.1.2.2.1 Charakteristické půdorysy", 5)
    add_text(doc, "Půdorysy se schématickým rozmístěním technických a technologických zařízení.")
    add_heading(doc, "D.1.2.2.2 Charakteristické řezy", 5)
    add_heading(doc, "D.1.2.2.3 Základní pohledy", 5)

    add_heading(doc, "D.2 Základní stavebně konstrukční řešení", 2)
    add_heading(doc, "D.2.1 Technická zpráva", 3)
    add_text(doc, "Návrh stavebně konstrukčního systému stavby včetně založení; navržené materiály a hlavní konstrukční prvky; uvažované zatížení při návrhu nosné konstrukce; podmínky postupu prací, které by mohly ovlivnit stabilitu vlastní konstrukce, případně sousední stavby; zásady pro provádění bouracích a podchycovacích prací a zpevňovacích konstrukcí či prostupů.")
    add_heading(doc, "D.2.2 Základní statický výpočet", 3)
    add_text(doc, "Údaje o zatíženích a materiálech; ověření základního koncepčního řešení nosné konstrukce; posouzení stability konstrukce; stanovení rozměrů hlavních prvků nosné konstrukce včetně jejího založení; dynamický výpočet, pokud na konstrukci působí dynamické namáhání.")
    add_heading(doc, "D.2.3 Výkresová část", 3)
    add_text(doc, "Výkres základů a výkresy nosné konstrukce stavby.")

    add_heading(doc, "D.3 Požárně bezpečnostní řešení", 2)
    add_text(doc, "Požárně bezpečnostní řešení se zpracuje podle požadavku stanoveného v položce Zásady požární bezpečnosti. Obsah a rozsah požárně bezpečnostního řešení je stanoven podle požadavků jiného právního předpisu.")

    add_heading(doc, "Dokladová část", 1)
    add_text(doc, "Dokladová část obsahuje doklady o splnění požadavků podle jiných právních předpisů vydané příslušnými správními orgány nebo příslušnými osobami a dokumentaci zpracovanou osobami oprávněnými podle jiných právních předpisů.")
    
    add_heading(doc, "1. Závazná stanoviska, stanoviska, rozhodnutí, vyjádření dotčených orgánů", 2)
    
    add_heading(doc, "2. Doklad podle jiného právního předpisu", 2)
    add_text(doc, "Pokud je dokumentace zpracována pro stavbu nebo soubor staveb, jejichž součástí je výrobek plnící funkci stavby, přikládá se doklad výrobce, dovozce nebo distributora, prokazující shodu vlastností tohoto výrobku s technickými požadavky na stavby v rozsahu příslušných základních požadavků, které se na výrobek ve funkci stavby vztahují.")
    
    add_heading(doc, "3. Vyjádření vlastníků veřejné dopravní a technické infrastruktury", 2)
    add_heading(doc, "3.1. Vyjádření vlastníků veřejné dopravní a technické infrastruktury k možnosti a způsobu napojení, vyznačená například na situačním výkrese.", 3)
    add_heading(doc, "3.2. Vyjádření vlastníka k podmínkám zřízení stavby, provádění prací a činností v dotčených ochranných a bezpečnostních pásmech podle jiných právních předpisů.", 3)
    
    add_heading(doc, "4. Projekt zpracovaný báňským projektantem", 2)
    
    add_heading(doc, "5. Ostatní stanoviska, vyjádření, posudky, studie a výsledky jednání vedených v průběhu zpracování dokumentace", 2)
    
    add_heading(doc, "6. Průzkumy", 2)
    
    add_heading(doc, "7. Projekt výsledků zeměměřických činností pro stavbu vyhotovený autorizovaným zeměměřickým inženýrem, kterým bude určeno, jaké výsledky zeměměřických činností podle jiného právního předpisu mají ve kterých fázích výstavby vzniknout", 2)
    
    add_heading(doc, "8. Soubor výsledků zeměměřických činností podle jiného právního předpisu, které mají podle projektu výsledků zeměměřických činností vzniknout v souvislosti s povolením stavby, vyhotovených autorizovaným zeměměřickým inženýrem", 2)

    # Uložení dokumentu
    doc.save('dokumentace_stavby.docx')
    print("Dokument byl úspěšně vytvořen a uložen jako 'dokumentace_stavby.docx'.")

if __name__ == "__main__":
    create_document_structure()