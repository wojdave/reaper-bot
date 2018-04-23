currencyPair="USDT_LTC"
//i=0;

testObj3 = [{ type: 'orderBookModify',
    data: { type: 'bid', rate: '67.50000000', amount: '43.47049314' } },
{ type: 'orderBookRemove',
    data: { type: 'ask', rate: '67.79948723' } },
{ type: 'orderBookRemove',
    data: { type: 'bid', rate: '67.5' } },
{ type: 'orderBookModify',
    data: { type: 'ask', rate: '67.79948716', amount: '94.78022288' } },
{ type: 'orderBookModify',
    data: { type: 'bid', rate: '67.50000000', amount: '43.47049314' } },
{ type: 'newTrade',
    data: 
     { amount: '29.20177400',
       date: '2017-11-17 03:03:43',
       rate: '67.50000000',
       total: '1971.11974500',
       tradeID: '2727533',
       type: 'sell' } },
{ type: 'orderBookRemove',
    data: { type: 'ask', rate: '67.79948723' } },
  { type: 'orderBookModify',
    data: { type: 'ask', rate: '67.79948716', amount: '94.78022288' } }];

testObj3.forEach(function (element) {

    //console.log(element);
    //  console.log(i);   //counter
    //  i++;              //counter

    if( element.type == 'newTrade' )
    {
        var amount = element.data.amount;
        var date = element.data.date;
        var rate = element.data.rate;
        var total = element.data.total;
        var tradeID = element.data.tradeID;
        var type = element.data.type;
        console.log("INSERT INTO market (currencyPair,amount,date,rate,total,tradeID,type)  "+
                    "VALUES ('"+currencyPair+"',"+amount+",'"+date+"',"+rate+","+total+","+tradeID+",'"+type+"');");

    }
    else if( element.type == 'orderBookModify' )
    {
        var type = element.data.type;
        var rate = element.data.rate;
        var amount = element.data.amount;
        console.log("INSERT INTO orderBook (currencyPair,type,rate) VALUES ('"+currencyPair+"','"+type+"',"+rate+") ON DUPLICATE KEY UPDATE amount=amount+"+amount+";");
        //console.log("INSERT INTO orderBook (currencyPair,type,rate,amount)  "+
        //            "VALUES ('"+currencyPair+"','"+type+"',"+rate+","+amount+");");

    }
    else if( element.type == 'orderBookRemove' )
    {
        var type = element.data.type;
        var rate = element.data.rate;
        console.log("DELETE FROM orderBook "+
	                "WHERE type = '"+type+"' AND rate = '"+rate+"';");

    }
});

