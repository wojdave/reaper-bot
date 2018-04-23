# reaper-bot

```
#------------------------------------------------------------------
#[REAPER] HARVESTBOT: havesting TICKER DATA since $(date +%s)
#[ currencyPair, last, lowestAsk, highestBid, percentChange, baseVolume, quoteVolume, isFrozen, 24hrHigh, 24hrLow ]
#------------------------------------------------------------------
```

## USAGE:

```
python3.5 reaper3.py 
```
```
stdbuf -oL -eL python3.5 reaper3.py | tee /dev/tty | sudo mysql -v -u root -ppassword bot
```

