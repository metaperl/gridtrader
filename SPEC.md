# Summary:

Trading program name: ADSactly Gridtrading Robot(hereafter referred to as "bot")
Exchange: all exchanges supported by [ccxt](https://github.com/ccxt/ccxt).

## Functionality:

For a given order book, DASH/BTC for example:
1. At start, place SELL LIMIT orders at higher then market, monitor
these orders and when they get filled: place buy orders at lower
levels. Also at start, place buy orders at lower then market, monitor
these orders and when they get filled: place sell orders at higher
levels.
1. Allow the user to start and stop the robot and change its configuration settings
1. E-mail alert if the bot halts or crashes. And also the ability to
login to the VPS session to view if the bot is actually running and
monitoring the orders. So a basic dashboard that displays all balances
and open orders and some trade history.

# DETAILS:

USER DEFINED values:


ICP: 1000 (INITIAL CORE POSITION)
ALERT e-mail address: validemailaddress
PAIRS: DASH/BTC
TPML: 20% (TAKEPROFIT_MAJOR_LEVEL)
TPS: 30% (TAKEPROFITSIZE: This is the % of ICP to spread across the number of the two variables below)
TPNUM: 10 (TAKEPROFIT_NUMBEROFORDERS)
TPINCR: 1% (TAKEPROFITINCREMENTS)
*To avoid confusion, I am using different variable valuables for each config type as I explain in program logic below, in practice these variables may have the same values as above)
RBML: 25% (REBUYMAJORLEVEL)
RBS: 21% (REBUYSIZE)
RBNUM: 8  (REBUY_NUMBEROFORDERS)
RBDECR: 2% (REBUY_DECREMENTS)

Program Logic:
    1) Query the ICP from config
    2) Query the balance for DASH/BTC (all polopairs in config)
    3) Display these values on the dashboard(simple text dashboard) as well as all values read from the config file
    4) Query current market price of polo pair ex: 0.01704200 BTC/DASH(As of Feb 10 2017), call this CMP from now on.
    5) Take CMP and add TPML. 0.01704200*1.2= 0.0204504 and consider this the starting price to place sell orders.
    6) Place 10 SELL orders(TPNUM) in total beginning at 0.0204504 and increasing by 1%(TPINCR) increments. The order size for each order should be the same and is calculated as follows: TPS * ICP / TPNUM. So: 30% x 1000 / 10 = 30 DASH per order.
        a. So the bot should place the following 10 orders:
TPONID
Order Size
Order Type
Price
1
30
SELL
0.0204504
2
30
SELL
0.0206549
3
30
SELL
0.0208615
4
30
SELL
0.0210701
5
30
SELL
0.0212808
6
30
SELL
0.0214936
7
30
SELL
0.0217085
8
30
SELL
0.0219256
9
30
SELL
0.0221449
10
30
SELL
0.0223663
    7) Note the TPONID field, the bot should keep track of this order it and the actual order ID that POLO returns for use later. Also note that the price of order 2 is 1.01x the price of order 1. Use the TPINCR variable to continuously multiply the last calculated price. Order 3 is 1.01 x Order 2 and so on up to Order 10.
    8) INITIAL TASK COMPLETE. We now have a state where there are 10 sell orders placed starting at 20% above CMP and are waiting to be filled, we now move on to doing the same thing on the buy side below market
    9) Take CMP and subtract RBML as follows:  0.01704200*.79=0.01346318
    10) Place 8 BUY orders (RBNUM) in total beginning at 0.01346318 and decreasing by 2%(RBDECR). The order size for each order should be the same and is calculated as follows: RBS * ICP / RBNUM. So: 21% x 1000 / 8 = 26.25 DASH per order.
        a. So the bot should place the following 10 orders:
RBONID
Order Size
Order Type
Price
1
26.25
BUY
0.01346318
2
26.25
BUY
0.0131939
3
26.25
BUY
0.0129300
4
26.25
BUY
0.0126714
5
26.25
BUY
0.0124180
6
26.25
BUY
0.0121696
7
26.25
BUY
0.0119263
8
26.25
BUY
0.0116877
9
26.25
BUY
0.0114540
10
26.25
BUY
0.0112249
    11) Again note the RBONID, the bot should keep track of this order and the actual order ID that POLO returns for use later.
    12) We now have 20 orders placed total(10 SELL above market and 10 BUY below market). The bot will simply no WAIT and monitor these orders until they get filled:
    13) Now monitor the sell orders: If a sell order gets filled, the bot should first CANCEL ALL RBONID BUY orders. And then proceed to re-create the RBONID buy grid as per steps 9 through 11 with one difference, do not query CMP, instead  consider CMP the fill price of TPONID 1, in this case 0.0204504. As each TPONID's get filled on the way up, cancel all BUY orders and RE-RUN steps 9 through 11.
    14) IF the last SELL order gets filled( TPONID 10). Then re-run steps 5 though 8 and place new sell orders and consider CMP the fill price of order 10 in TPONID, in this case 0.0223663. So the bot should start placing a set of 10 new orders starting at 0.0223663*1.2=0.02683956 as a starting point.
    15) In the case where buy orders get filled when the market moves down, for each buy order that is filled place a corresponding sell order at the same order size as RBONID order size and at the price of RBONID PRICE + TPS. So in the example where the buy order for 26.25 DASH gets filled at 0.01346318, place a sell order for 26.25 DASH at 0.016155816 (0.01346318*1.2)
    16) When the last RBONID order 10 is filled place the corresponding buy order as per step 15 but we are now in a situation here we have no more buy orders. Just as we did in step 14 on the take profit sell side, we must do the same on the buy side. So take RBONID order 10 PRICE of 0.0112249 and run steps 9 through 11 and begin to place 10 BUY orders starting at 0.008867671(0.0112249*.79)
    17) On any order fill, send an e-mail alert to the e-mail in config file with MINIMAL details for privacy and security reasons ex: SUBJECT: BOT ORDER FILL, BODY: BUY ORDER was filled at a price of 0.01346318. Create a toggle setting that allows the user to turn e-mail alerts for order fills on or off.

# Exceptions, Error Handling, Crashes, bugs and testing

This is the hardest part of the job,  when the bot crashes and
resumes, it needs to know which orders have
been placed and what state it was in, it needs to monitor the orders
on the exchange to make sure the exchange does not cancel the orders,
so I suggest a require of polo order state every 1 hour.
If the API requests get blocked or banned by polo there needs to be error
handling and e-mail alerts sent.

Decimal precision, different orderbooks handle precision differently, api calls must be done with correct precision.
Orderbook pair logic, QUOTE currency in DASH/BTC pair for example must be properly queried and understood, math calculations
done on DASH/BTC price must be done correctly. Order Cancelling via API may fail.
This and much more needs to be thoroughly tested and accounted for.
