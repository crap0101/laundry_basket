/*
  author: Marco Chieppa (aka crap0101)
  year: 2016
  copyright: public domain.

  script per greaseamonkey per eliminare dai risultati egosearch
  di phpBB quelli marcari come risolti (per il forum ubuntu-it.org).
*/

// ==UserScript==
// @name         RFubu
// @description  egosearch filter
// @version      0.1
//
// @grant    GM_getValue
// @grant    GM_setValue
// @grant    GM_deleteValue 
// @grant    GM_log
// @namespace    https://gitorious.org/~crap0101
// @include      http://forum.ubuntu-it.org/search.php?search_id=egosearch
// @run-at       document-end
// ==/UserScript==

var egofilter = function () {
    //console.log("~~ EGOFILTER ~~");
    var Reg = /^\[?risolto/im;
    var getAuthor = function () { return 1; };
    var topics = document.getElementsByClassName("topiclist topics")[0];
    var topic = topics.getElementsByTagName("li");
    for (var i=topic.length-1; i >= 0; i--) {
        var title = topic[i].getElementsByClassName("topictitle")[0];
        //console.log("TITLE: " + title.innerHTML);
        if (Reg.test(title.innerHTML) && getAuthor()) {
	    topic[i].parentNode.removeChild(topic[i]);
            console.log("PURGED: " + title.innerHTML);
        }
    }
};

egofilter();
