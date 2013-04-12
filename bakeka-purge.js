/*
  author: Marco Chieppa (aka crap0101)
  year: 2012
  copyright: public domain.

  script per greaseamonkey  per eliminare le "offerte" di lavoro
  delle fottute agenzie interinali da *.bakeka.it .
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

var ShitReg = /Il nostro Cliente[:]?|per nostro cliente|Per ditta di servizi|per azienda|per\s(azienda(\scliente)?|cliente)|per\s(important[ei]|prestigios[iao]|primari[ao]?)\s(client[ei]|azienda|realtà|negozio)|per( una)? società cliente|elektraservices|ali spa|consorzio elpe|ADHR|Gruppo Elpe|Viesse|Knet Human|Knet Human Resources|HUMANGEST SPA|MAW Divisione Permanent|TEMPORARY SPA|Obiettivo Lavoro|Lavoropiù|Adecco|Mirror srl|randstad|manpower|kelly|Trenkwalder|Synergie|Viesse|Elite Executive Research|Gi Group|Cooperjob|Start People|GB Job|gruppo gedi|Orienta spa|ManpowerGroup|Agenzia per il Lavoro|HORECA JOB|AXL spa|OFFICE JOB|Elite Ricerca e Selezione|Maxwork|Starbytes|La filiale di/im;

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

