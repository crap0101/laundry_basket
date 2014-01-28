/*
  author: Marco Chieppa (aka crap0101)
  year: 2012-2013
  copyright: public domain.

  script per greaseamonkey  per eliminare le "offerte" di lavoro
  delle fottute agenzie interinali da *.bakeka.it e altra merda
  tipo lelemarcheting.
  Scritto di getto e non particolarmente testato.
*/

// ==UserScript==
// @name    bakeka-purge
// @description    delete shit from bakeka.it subdomains
// @version    0.1
//
// @grant    GM_getValue
// @grant    GM_setValue
// @grant    GM_deleteValue 
// @grant    GM_log
// @namespace    https://gitorious.org/~crap0101
// @include    /^http://\w+\.bakeca\.it//
// @run-at    document-end
// ==/UserScript==

var ShitReg = /Il nostro Cliente[:]?|importante azienda cliente|per nostro cliente|Per ditta di servizi|per azienda|per\s(azienda(\scliente)?|cliente)|per(\sun['`a]?)?\s(important[ei]|nostr[ao]|prestigios[iao]|primari[ao]?)\s(client[ei]|azienda|realtà|negozio)|per( una)? società cliente|elektraservices|ali(?= (s\.p\.a\.|spa))|consorzio elpe|Gruppo Elpe|Elpe Global Logistic|ADHR|Viesse|Knet\s+Human|Knet\s+Human Resources|EgoValeo|HUMANGEST(?= (s\.p\.a\.|spa))|MAW|TEMPORARY(?= (s\.p\.a\.|spa))?|Obiettivo Lavoro|articolo 1|YOU\s?AND\s?LONDON|Lavoropi[uù]|Adecco|SVEAC|lavorint|Mirror srl|randstad|manpower|kelly|Openjobmetis|Trenkwalder|Synergie|Viesse|Elite Executive Research|Gi Group|Cooperjob|Start People|GB Job|Workforce|gruppo gedi|Orienta(?= (s\.p\.a\.|spa))|IN JOB|ManpowerGroup|NUOVE FRONTIERE LAVORO|During(?= (s\.p\.a\.|spa))|Tempi Moderni(?= (s\.p\.a\.|spa))|Generazione Vincente|WYSER(?= (s\.r\.l\.|srl))|Quanta(?= (s\.p\.a\.|spa|italia))|unique(?= (s\.p\.a\.|spa))|USG People|Agenzia per il Lavoro|HORECA JOB|IDEALAVORO|AXL(?= (s\.p\.a\.|spa))|OFFICE JOB|IDEA( Ag.)\s*LAVORO|Elite Ricerca e Selezione|Maxwork|Work4you|wintime|Starbytes|CRCC Asia|FM GROUP|MODULO INNOVAZIONE|(per|di) vendita diretta|La filiale di|Herbalife|(entrata|guadagno|reddito) extra|Face to face|(settore|mercato) (del)?\s?benessere|(network |tele)(?=marketing)|teleselling|(Direct|web) Marketing|outbound|(bisogn[oi]( di)*|concedere( un)*|forn[a-z]+|offrire|offriamo|offert[ae]( di)*|un) prestit[io]|prestit[io] di offert[ae]|cerc.*?venditor[ei]|addett[ei] alla vendita|(di|per|vuoi|piacerebbe) arrotondare|in forte espansione|cartomanti|banchiere in pensione|difficoltà finanziarie/im;

var bakekapurge = function () {
    var divs = document.getElementsByTagName("div");
    for (var i=divs.length-1; i >= 0; i--) {
	var div = divs[i];
	if (div.className.indexOf("annuncio-item") == 0) {
	    var elems = div.getElementsByTagName("p");
            //console.log(elems.className);
	    for (var j=0; j<elems.length; j++) {
		var el = elems[j];
		if (el.className == "text" && ShitReg.exec(el.innerHTML)) {
		    //console.log(el.innerHTML);
		    //el.innerHTML = "[PURGED]";
		    div.parentNode.removeChild(div);
		    break;
		}
	    }
	}
    }
};

bakekapurge();

