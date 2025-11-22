import sys
from passwords import mt5_cleardemo_password
from passwords import mt5_Genial_DayTrade_password
from passwords import mt5_Genial_SwingTrade_password
from passwords import mt5_infinox_live
from mt5exchange.mt5exchange import MTrader





server,login,password = mt5_Genial_SwingTrade_password()
conn = MTrader(server,login,password)

code = 'PETR4'
conn.symbol_select(code)

print('\nfunctio read_info:')
current_price , current_sell_price, current_buy_price = conn.read_info(code)
print(f'current_price: {current_price} , current_sell_price: {current_sell_price}, current_buy_price: {current_buy_price}')

print('\nfunction read_price_day:')
last_close, current_open, current_value = conn.read_price_day('PETR4')
print(f'last_close: {last_close}, current_open: {current_open}, current_value: {current_value}')

print('\nfunction read_positions:')
pos = conn.read_positions('PETR4')
print(f'pos.ticket: {pos.ticket}, pos.time: {pos.time}, pos.volume: {pos.volume}')

print('\nfunction read_position:')
pos = conn.read_position('PETR4')
print(pos)

print('\nverify_position:')
pos = conn.verify_position(code, 0)
print(pos)

print('\nread_order:')
order = conn.read_order(code)
print(order)

print('\nFunction verify_order:')
a,b,c,d = conn.verify_order(code,0)
print(a,b,c)

print('\nFunction read_candles:')
df_candles = conn.read_candles(code,'5m',n=1)
print(df_candles)
df_candles = conn.read_candles(code,'5m',n=10)
print(df_candles)

print('\nFunction read_OHLC:')
df = conn.read_OHLC(code, '5m', n=1)
print(df)
df = conn.read_OHLC(code, '5m', n=10)
print(df)

print('\nFunction get_book:')
df = conn.get_book(code)
print(df)


