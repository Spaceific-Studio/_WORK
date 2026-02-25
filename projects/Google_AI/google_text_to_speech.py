from google import genai
from google.genai import types
import pip
import os
import wave

#os.system(r"pip install google")
#pip.main(['install', 'google-genai'])

"""
client = genai.Client()
response = client.models.generate_content(model="gemini-2.5-flash",contents="Explain how AI works in a few words",)
print(response.text)
"""


 
# Set up the wave file to save the output:
def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
   with wave.open(filename, "wb") as wf:
      wf.setnchannels(channels)
      wf.setsampwidth(sample_width)
      wf.setframerate(rate)
      wf.writeframes(pcm)
 
#client = genai.Client()
client = genai.Client(api_key="AIzaSyDXeKBly1UEiA_HMi1dKNNap-qTtneHZl8")

voiceName = 'callirrhoe'

text = {'1_1':'Předmětem stavby je dílčí rekonstrukce stávajícího zařízení technologické linky úpravny vody Podolí – zařízení čiřič číslo sedm. Čiřiče tvoří v rámci technologické linky úpravy vody první separační stupeň. V objektu A jsou umístěny tři čiřiče sedm, osum a devět. V současné dobějsou všechny tři čiřiče odstavené z provozu.', \
        '1_2':'Přítok surové vody do čiřičů je z přerušovacích nádrží - oxidérů umístěných v budově B pomocí přívodního uzavřeného tlakového železobetonového kanálu. Kanál prochází objektem B, kde jsou z něj napájeny funkční čiřiče tři až šest, dále budovou C do budovy A k čiřičům sedm až devět. Úseky přítokového kanálu umístěné v objektech A a C jsou předmětem řešení této stavby.' ,\
        '2':'Projekt Rekonstrukce čiřiče 7 byl vybrán jako pilotní projekt v rámci zavádění metody BIM včetně využití nástrojů pro tvorbu modelů v aplikaci Revit a Comos a pro automatizované plnění negrafických informací a jejich validaci pomoci nástroje BIM Manager. Jako jednotné datové prostředí pro tvorbu, sdílení informací a koordinaci modelů byla použita platforma Autodesk Construction Cloud. V projektu byly zastoupeny tyto profese: Architektonicko stavební, Strojně technologická, Elektro technologická i Měření a regulace.' ,\
        '4_1':'Plnění negrafických informací řídí aplikace Bim Manager. Její přínos je v procesu plnění klíčový, protože zabezpečuje aktuálnost a konzistenci požadovaných parametrů a jejich detail (takzvaný LOIN), který odpovídá účelům užití. Aplikace je také důležitým prvkem pro integraci dalších systémů a pro výměnu dat, jako je například technický informační systém Helios Tinos pro facility management nebo systém Comos.' ,\
        '4_2':'Pražská vodohospodářská společnost investovala do vývoje aplikace Bim Manager s cílem zlepšit automatizaci plnění dat. Propojení na prostředí Revit umožňuje hromadné vyplňování parametrů včetně číselníkových hodnot na základě aktuální struktury technického informačního systému. Důležitou funkcionalitou je také validátor, který vyhodnotí úplnost vyplněných parametrů vůči aktuálnímu datovému standardu.' ,\
        '5_1':'Revit slouží v rámci tvorby modelu pro prostorovou a dispoziční koordinaci stavby a dalších profesí. Umožňuje vizualizaci prvků spojenou s tvorbou dokumentace, včetně výkazů výměr materiálů z rozměrových parametrů délek, objemů a hmotností. Modulová architektura systému Comos umožňuje jeho využití v celém životním cyklu drobných i rozsáhlých technologických celků. Jeden model integruje disciplíny zahrnující procesní, elektro, automatizační i mechanickou část. ' ,\
        '5_2':'Pro technologickou část lze v Comosu navrhovat schémata, jak strojně-technologických komponent, tak i elektro instalací včetně instrumentace měření a jejich vzájemná propojení.' ,\
        '5_3':'Systém umožňuje vkládání procesních parametrů, které poskytují informace o přesné lokalizaci a sledování například pro zajištění prediktivní údržby. Potenciální je i využití dalších řídících nástrojů Scada, DCS a aj-ou-tý. Další oblastí využití je komplexní správa a evidence až po využití procesů “smart building” s možností sledování spotřeby energie. ' ,\
        '7':'V současnosti probíhá vývoj uživatelského prostředí Comos s cílem funkčního propojení s aplikaci Revit. V této fázi ještě chybí možnost synchronizovat negrafické informace mezi oběma platformami, proto můžeme ukázat pouze návrh karet s parametry podle datového standartu PVS – PVK.' ,\
        '8':'Dále nám systém Comos umožňuje přehledné zobrazení vazeb mezi strojně-technologickou části objektu a elektro částí.' ,\
        '9':'Díky tomu, že objektová hierarchická struktura Comosu zachovává vztahy mezi schématy, je zajištěna konzistence prvků, které obsahují.' ,\
        '12':'Tím, že Comos je založen na es-kjú-el databázi, umožňuje flexibilní tvorbu výkazových seznamů pomocí dotazů.' ,\
        '13_1':'Systém Comos nabízí další modulové nadstavby:   Comos Web:' ,\
        '13_1_1':'Projekty jsou dostupné skrze webové prostředí. Je zachována většina funkcionalit, mimo tvorbu schémat. Vzhled uživatelského prostředí webové verze je možné na základě požadavků upravit.' ,\
        '13_2':'Mobilní aplikace Comos Mobile Worker je dostupná na všech standardně využívaných operačních systémech.  Zajišťuje správu a řešení údržby buď samostatně, nebo na základě informací v projektech systému Comos.' ,\
        '13_3':'Comos Walk-inside -  umožňuje přímé propoiení s 3D modelem provozu.' ,\
        '13_4':'"Comos Integration" - umožňuje propojení na provozní data z platformy Siemens Insights Hub. Insights Hub umožňuje shromažďovat aj-ou-tý data z širokého spektra zdroiů a pracovat s nimi v rámci kyberneticky zabezpečeného prostředí.' ,\
        'Outro_1':'"Digitalizace!"' ,\
        'Outro_2':'"Digitalizace!... Od myšlenky k realitě."' \
        }
current_text_paragraph = 'Outro_2'
response = client.models.generate_content(
   model="gemini-2.5-flash-preview-tts",
   contents=text[current_text_paragraph],
   config=types.GenerateContentConfig(
      response_modalities=["AUDIO"],
      speech_config=types.SpeechConfig(
         voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
               voice_name=voiceName,
            )
         )
      ),
   )
)

data = response.candidates[0].content.parts[0].inline_data.data
file_name=r'C:\Users\gercakd\OneDrive - pvs.cz\Plocha\pracovni\\' + voiceName + '_' + current_text_paragraph + '.wav'
wave_file(file_name, data) # Saves the file