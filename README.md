# reaper-bot

havesting TICKER DATA since $(date +%s)

```
[currencyPair, last, lowestAsk, highestBid, percentChange, baseVolume, quoteVolume, isFrozen, 24hrHigh, 24hrLow]
```

## USAGE:

Print mysql INSERTS INTO terminal
```
python3.5 reaper3.py 
```
Log mysql INSERTS INTO console.log
```
sudo stdbuf -oL -eL python3.5 reaper3.py | tee /dev/tty > console.log
```
Pipe mysql INSERTS INTO mysql db -- database parameters must be configured prior to execution
```
stdbuf -oL -eL python3.5 reaper3.py | tee /dev/tty | sudo mysql -v -u root -ppassword bot
```
## CONFIG:

Pipe test mysql INSERTS INTO mysql db -- database parameters must be configured prior to execution
```
js testsql3.js | sudo -u root -ppassword mysql bot
```
