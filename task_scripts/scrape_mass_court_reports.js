var casper = require('casper').create();
//var casper = require('casper').create({
//    verbose: true,
//    logLevel: "debug"
//});
var fs = require('fs');
var org_set = {};
var detail_set = {};

var start_item = 1;
var index_link = '';
var base_link = '';

function login_form(){
    console.log('submitting form...');
    casper.then(function(){
        this.fill('form[id="form1"]', {
        }, true);
        this.wait(2000);

    });
}

function on_list_open(casper){
    casper.then(function(){
        console.log("scraping: " + this.getCurrentUrl());
        var item_links = this.evaluate(function(){
            var result_list = [];
            var item_tags = document.querySelectorAll('div[valign="top"]');
            for( var di=0;di<item_tags.length;di++ ){
                var d = item_tags[di];
                var link = d.querySelector('a.ResultListItemLarge').getAttribute('href');
                var text = d.querySelector('.ResultSubListItem').textContent;
                result_list.push({'link': link, 'text': text});
            }
            return result_list;
        });
        this.capture('step2.png',{top:0,left:0,width:1024,height:768});

        fs.write('./result_list.json', JSON.stringify(item_links)+',', 'a');
        if(this.exists('a[title="Link to next set of documents"]')){	// if there is the next page, click the link
            this.wait(1000, function(){
                this.click('a[title="Link to next set of documents"]');
                this.emit('results.load');
            });
        }
    });
}

function task_scrape_list(){
    
    casper.on('results.load', function(){
		on_list_open(this);
	});
    
    casper.start('http://massreports.com/opinionarchive/default.aspx');
    login_form();
    
    casper.then(function(){
        base_link = this.getCurrentUrl(); 
        index_link = this.evaluate(function(){
            return document.querySelectorAll('div[valign="top"]')[0].querySelector('a').getAttribute("href");
        });
        casper.open(base_link+'&nstartlistitem='+start_item).then(function(){
            this.emit('results.load');
        });
		
	});
    
    casper.run()
}


function task_detail_list(){
    var file_name = './result_list.json';
    if(!fs.isFile(file_name)){
        console.log('file not exist!');
        return;
    }
    
    org_list = JSON.parse('['+fs.read(file_name)+'[]]');
    
    // converting org_list:
    item_list = []
    for(var i=0;i<org_list.length;i++){
        for(var j=0;j<org_list[i].length;j++){
            item_list.push(org_list[i][j]);
        }
    }
    
    console.log('loading '+item_list.length+' results.');
    
    casper.start('http://massreports.com/opinionarchive/default.aspx');
    login_form();
    
    var index=start_item;	//　I need an index out of the then scope for lazy function calling
    for(var i=index;i<item_list.length;i++){
        casper.then(function(){
            var link = item_list[index]['link'];
            var title = item_list[index]['text'];
            casper.open(link).then(function(){
                console.log('fetching: #'+index+' : '+link);
                var content = this.evaluate(function(){
                    return document.querySelector('.Layout_DocumentBody').innerHTML;
                });
                var record = {'l':link,'n':index,'t':title,'c':content};
                fs.write('./result_detail.json', JSON.stringify(record)+',', 'a');
            });
            index++;

        })
    }
    
    casper.run()
}

function task_rinse(){
    var file_name = './result_detail.json';
    if(!fs.isFile(file_name)){
        console.log('file not exist!');
        return;
    }
    
    org_list = JSON.parse('['+fs.read(file_name)+'{}]');
    
    var missing_items = [];
    
    for(var i=0;i<org_list.length-1;i++){
        var item = org_list[i];
        if(item['c'] === null){
            missing_items.push({'link':item['l'], 'text':item['t']});
        }
    }
    
    fs.write('./missing.json', JSON.stringify(missing_items)+',', 'a');
    
    console.log(org_list.length);
}

//
//casper.then(function(){
//    base_link = this.getCurrentUrl(); 
//    index_link = this.evaluate(function(){
//        return document.querySelectorAll('div[valign="top"]')[0].querySelector('a').getAttribute("href");
//    });
//    console.log('opening first page...'+base_link+'&nstartlistitem='+start_item);
//    casper.open(base_link+'&nstartlistitem='+start_item).then(function(){
//        while(true){
//            // get all text and links from the index page
//            var item_links = this.evaluate(function(){
//                var result_list = [];
//                var item_tags = document.querySelectorAll('div[valign="top"]');
//                for( var di in item_tags ){
//                    var d = item_tags[di];
//                    var link = d.querySelector('a').getAttribute('href');
//                    var text = d.querySelector('.ResultSubListItem').textContent;
//                    result_list.push({'link': link, 'text': text});
//                }
//                return result_list;
//            });
//
//            console.log(item_links);
//
//            // scrape every single detail page
//            for(var di in item_links){
//                var item_link = item_links[di];
//                console.log('opening detail page ... '+item_link['link']);
//                casper.open(item_link['link']).then(function(){
//                    var content = casper.evaluate(function(){
//                        return document.querySelector('.Layout_DocumentBody').innerHTML;
//                    });
//                    // write to the file!
//                    console.log({'link':item_link['link'], 'content':content});
//                    fs.write('./result.json', JSON.stringify({'link':item_link['link'], 'title':item_link['text'], 'content':content})+',');
//                });
//                
//            }
//            break;
//            // if there is no next page, break;
//            var exit_criteria = this.evaluate(function(){
//                return document.querySelector('a[title="Link to next set of documents"]') !== null;
//            });
//            if(!exit_criteria) break;
//
//            // scrape next page / next 20 records
//            start_item += 20;
//            console.log('opening next index sheet ... '+base_link+'&nstartlistitem='+start_item);
//            casper.thenOpen(base_link+'&nstartlistitem='+start_item);
//        }
//    });
//});
//
//
//
function main(){
	switch(casper.cli.get(0)){
		case 'scrape':
            if(casper.cli.get(1)){
                start_item = casper.cli.get(1);
            }
            else{
                start_item = 1;
            }
			console.log('[task: Scrape lists from:'+start_item+'] ');
            
			task_scrape_list()
			break;
		case 'detail':
            if(casper.cli.get(1)){
                start_item = casper.cli.get(1);
            }
            else{
                start_item = 0;
            }
			console.log('[task: Detail case from:'+start_item+'] ');
            
			task_detail_list()
			break;
        case 'rinse':
            task_rinse();
            break;
	}

}


main();