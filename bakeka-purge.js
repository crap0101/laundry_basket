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

var ShitReg = /Il nostro Cliente[:]?|Per ditta di servizi|per azienda|per\s(azienda(\scliente)?|cliente)|per\s(important[ei]|prestigios[iao]|primari[ao]?)\s(client[ei]|azienda|realtà)|ali spa|consorzio elpe|Gruppo Elpe|Viesse|Knet Human Resources|HUMANGEST SPA|TEMPORARY SPA|Adecco|randstad|manpower|kelly|Synergie|Viesse|Gi Group|Cooperjob|Agenzia per il Lavoro/im;

var bakekapurge = function () {
    var divs = document.getElementsByTagName("div");
    for (var i=0; i<divs.length; i++) {
	var div = divs[i];
	if (div.className.indexOf("annuncio-item") == 0) {
	    var elems = div.getElementsByTagName("p");
            //console.log(elems.className);
	    for (var j=0; j<elems.length; j++) {
		var el = elems[j];
		if (el.className == "text" && ShitReg.exec(el.innerHTML)) {
		    //console.log(el.innerHTML);
		    div.parentNode.removeChild(div);
		    break;
		}
	    }
	}
    }
};

bakekapurge();

