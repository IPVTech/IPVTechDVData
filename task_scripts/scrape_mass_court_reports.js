var casper = require('casper').create();
var fs = require('fs');
var org_set = {};
var detail_set = {};

var start_item = 1;
var index_link = '';
var base_link = '';

casper.start();
casper.thenOpen('http://massreports.com/opinionarchive/default.aspx');

casper.then(function(){
    this.fill('form[id="form1"]', {
    }, true);
    this.wait(2000);
     
});

casper.then(function(){
    base_link = this.getCurrentUrl(); 
    index_link = this.evaluate(function(){
        return document.querySelectorAll('div[valign="top"]')[0].querySelector('a').getAttribute("href")
    });
});

casper.then(function(){
    console.log(base_link);
    console.log(base_link.replace('nstartlistitem=1', 'nstartlistitem=10'));
    this.capture('step2.png',{top:0,left:0,width:1024,height:768});
});



casper.run();