
from understanding.rules import rule_based_extract

TEST_QUERIES = [
    "şäheriň içinde maňa iň arzan we gowy pizza taýýarlap berýän restorany tapyp ber",
    "häzir agşam giç boldy, şu wagt hem işleýän we bahalary gaty gymmat bolmadyk restoran nirede bar",
    "maňa täze telefon satyn almak gerek, bahasy arzanrak we saýlamasy köp bolan telefon dükanyny gözleýärin",
    "öýüme iň ýakyn ýerde ýerleşýän we häzir açyk bolan dermanhanany tapyp ber",
    "işden soň kofe içip oturmak isleýärin, rahat we ýakyn ýerde gowy kofe dükany barmy",
    "täze aýakgap almak isleýärin, erkekler üçin saýlawy köp we bahalary amatly bolan dükany gözleýärin",
    "çagamyň doglan güni üçin oýnawaç almak isleýärin, çagalar üçin oýnawaçlary köp bolan dükany tapyp ber",
    "toý üçin saçymy we makiýažymy etdirip boljak gowy gözellik salony nirede ýerleşýär",
    "şäherde iň gowy hyzmat edýän we müşderileri köp razy edýän gözellik salonyny gözleýärin",
    "maşynym ýolda birden döwüldi, häzir maňa mümkin boldugyça ýakyn awtoulag abatlaýyş hyzmaty gerek",
    "maşynymy barlatmak we motoryndaky meseläni düzetmek üçin gowy awtoservis gözleýärin",
    "ýolda benzin gutardy, şu ýere iň ýakyn benzin stansiýasyny nireden tapyp bilerin",
    "gije sagat on iki bolanda hem azyk satyn alyp boljak açyk market ýa-da dükan barmy",
    "elim kesildi we häzir gan akýar, mümkin boldugyça tiz kömek alyp boljak ýeri görkez",
    "kelläm düýn agşamdan bäri gaty agyrýar, öýde näme edip bilerin ýa-da haýsy lukmana ýüz tutmaly",
    "dogan-garyndaşymyň doglan güni ýakynlaşýar, oňa laýyk gowy sowgat satyn alyp boljak dükany gözleýärin",
    "ýakyn ýerlerde dürli görnüşli sowgatlar satylýan sowgatlyk dükany barmy",
    "ejeňe sowgat hökmünde gül buketi sargyt etmek isleýärin, eltip berýän gül dükanyny tapyp ber",
    "maňa bank hyzmatlary gerek, häzirki ýerleşýän ýerime iň ýakyn bank şahamçasyny görkez",
    "täze maşyn almak üçin kredit almak isleýärin, kredit hyzmaty hödürleýän banklary nireden tapyp bilerin",
    "noutbugym açylmaýar we abatlatmak gerek, ygtybarly kompýuter abatlaýyş hyzmatyny gözleýärin",
    "täze telefon almak isleýärin, kamerasy gowy we bahasy orta derejede bolan modelleri satýan dükany gözle",
    "öýde oturyp burger sargyt etmek isleýärin, eltip berme hyzmaty bolan burger restoranlary nirede",
    "gowy etli döner iýesim gelýär, golaýymda arzan we tagamly döner satýan ýer barmy",
    "dostlarym bilen suşi iýmek isleýäris, şäherde iň arzan we gowy bahalandyrylan suşi restoranyny tapyp ber",
    "agşam dostlarym bilen steýk iýmäge gitmek isleýäris, gowy et taýýarlap berýän restoran nirede",
    "daşary ýurt naharlary däl-de, hakyky milli tagamlary dadyp boljak gowy restoran gözleýärin",
    "maňa türk aşhanasynyň dürli tagamlaryny hödürleýän we maşgala bilen baryp boljak restoran gerek",
    "aziýa aşhanasyny halaýaryn, hytaý, koreý ýa-da ýapon naharlary bolan restoranlary nireden tapyp bilerin",
    "uniwersitetiň golaýynda kitap satyn alyp boljak, okuw kitaplary hem bar bolan kitap dükanyny gözleýärin",
    "maňa täze sagat almak gerek, golaýymda erkekler üçin sagat satýan gowy dükan barmy",
    "öý üçin täze haly almak isleýärin, dürli ölçegdäki we dürli bahadaky halylary satýan dükany tapyp ber",
    "täze öýe göçdüm, şonuň üçin divan, stol we oturgyç ýaly mebel satýan uly dükany gözleýärin",
    "öý üçin sowadyjy, kir ýuwujy maşyn we beýleki hojalyk tehnikalaryny bir ýerden satyn alyp bolýarmy",
    "köne kir ýuwujy maşynym bozuldy, ony abatlatmak ýa-da täze maşyn satyn almak üçin dükan gözleýärin",
    "maňa kompýuter üçin monitor, klawiatura we syçan hem satýan uly kompýuter dükany gerek",
    "kiçi biznesim üçin täze web sahypa ýasadyp bermäge ukyply ýerli kompaniýa ýa-da hyzmat gözleýärin",
    "resminamalar üçin professional foto düşürmek gerek, golaýymda surat studiýasy ýa-da foto salon barmy",
    "toý dabaramda janly aýdym aýtmak üçin aýdymçy ýa-da saz toparyny kärendesine almak isleýärin",
    "dostlarym bilen dynç almak isleýäris, şäherde gije karaoke aýdyp boljak gowy ýer barmy",
    "dynç güni maşgalam bilen söwda etmäge gitmek isleýärin, içinde köp dükan bolan uly söwda merkezi nirede",
    "restorandan nahar sargyt etjek, ýöne öýe eltip bermek hyzmatynyň bardygyny öňünden bilmek isleýärin",
    "gyşky paltolarymy we beýleki eşiklerimi professional himiki arassalaýyşda arassalatmak gerek, golaýda şeýle ýer barmy",
    "täze kwartira satyn almak isleýärin, maňa kwartira tapmaga kömek edip biljek emläk agentligini gözleýärin",
    "şäheriň gowy etraplarynyň birinden ýaşamak üçin kwartira satyn almak ýa-da kärendesine almak isleýärin",
    "gözlerimi barlatmak we täze äýnek almak üçin optika dükany ýa-da göz lukmanynyň ýanyna gitmek gerek",
    "gözlerim üçin täze äýnek gerek, bahasy amatly we saýlawy köp bolan optika dükanyny tapyp ber",
    "dynç gün dostlarym bilen täze film görmäge gitmek isleýäris, golaýda kino teatry barmy",
    "doglan gün dabaram üçin uly bolmadyk, ýöne tagamly we owadan tort sargyt etmek isleýärin",
    "şu yssy howada sowuk doňdurma iýesim gelýär, golaýymda dürli tagamly doňdurma satýan ýer barmy",
]

def run():
    for q in TEST_QUERIES:
        result = rule_based_extract(q)
        status = "OK" if result["category"] else "MISS"
        print(f"[{status}] {q} -> {result}")


if __name__ == "__main__":
    run()