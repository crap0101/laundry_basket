/*
  author: Marco Chieppa (aka crap0101)
  year: 2013
  copyright: public domain.

*/

// ==UserScript==
// @name    raisilvercrapgetvideo
// @description    get video url(s) from rai.tv (fuck silverlight)
// @version    0.1
//
// @grant    GM_getValue
// @grant    GM_setValue
// @grant    GM_deleteValue 
// @grant    GM_log
// @namespace    https://gitorious.org/~crap0101
// @include    /^http://www.rai.tv/dl/RaiTV/programmi/media/ContentItem-.*/
// @run-at    document-end
// ==/UserScript==


var make_link = function (name, url) {
    var videolink = document.createElement('a');
    var text = document.createTextNode(name);
    videolink.appendChild(text);
    videolink.title = name;
    videolink.href = url;
    return videolink;
};

var table_add = function (table, name, url) {
    var row = table.insertRow(-1);
    var cell = row.insertCell(0);
    var videolink = document.createElement('a');
    var text = document.createTextNode(name);
    videolink.setAttribute("href", url);
    text.title = name;
    cell.appendChild(videolink);
    videolink.appendChild(text);
};

var get_video_link = function () {
    var arr = document.head.getElementsByTagName("meta");
    var mediaItem = document.getElementById("mediaItem");
    var table = document.createElement("table");
    mediaItem.insertBefore(table, mediaItem.firstChild);
    for (var i=0; i<arr.length; i++) {
        var el = arr[i].getAttribute("name");
        if (el && el.match(/^videourl/)) {
            var url = arr[i].getAttribute("content");
            console.log(url);
            table_add(table, el, url);
            //console.log(make_link(el, url));
        }
    }
}

get_video_link();
