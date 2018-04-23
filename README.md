# reaper-bot

```
#------------------------------------------------------------------
#[REAPER] HARVESTBOT: havesting TICKER DATA since $(date +%s)
#[ currencyPair, last, lowestAsk, highestBid, percentChange, baseVolume, quoteVolume, isFrozen, 24hrHigh, 24hrLow ]
#------------------------------------------------------------------
```

## USAGE:

Print mysql INSERTS INTO terminal
```
python3.5 reaper3.py 
```

Pipe mysql INSERTS INTO mysql db
```
stdbuf -oL -eL python3.5 reaper3.py | tee /dev/tty | sudo mysql -v -u root -ppassword bot
```

