from datetime import datetime
import pandas as pd

from flask import Flask, request, jsonify
from passwords import mt5_clear_password
from passwords import infinox

from mt5exchange.mt5exchange import MTrader
import MetaTrader5 as mt5
from flask_cors import CORS
import time
import sys

app = Flask(__name__)
CORS(app)

"""
def symbol_info_to_dict(resultado):
    if resultado is None:
        return None
    return resultado._asdict()
"""

@app.route('/symbol_select',    methods=['GET']) #done
def symbol_select():
    symbol    = request.args.get("symbol")
    symbol = symbol.upper()
    resultado = conn.symbol_select(symbol)
    return jsonify({
        "result": resultado
    })

@app.route('/read_all_info',    methods=['GET']) #done
def read_all_info():
    symbol    = request.args.get("symbol")
    conn.symbol_select(symbol)
    resultado = conn.read_all_info(symbol)
    if resultado is not None:
        resultado = resultado._asdict()
    return jsonify({
        "result" : resultado
    })

@app.route('/read_candles',     methods=['GET']) #done
def read_candles():
    symbol = request.args.get("symbol")
    tf     = request.args.get("tf")
    n      = int(request.args.get("n"))
    conn.symbol_select(symbol)
    resultado = conn.read_candles(symbol,tf,n)
    resultado['time'] = resultado['time'].astype(str)
    return jsonify({
        "result": resultado.to_dict(orient='records')
    })

@app.route('/read_ticks',       methods=['GET']) #done
def read_ticks():
    symbol = request.args.get("symbol")
    start_time = datetime.strptime(request.args.get("start_time"), '%Y-%m-%d %H:%M:%S')
    end_time =   datetime.strptime(request.args.get("end_time"),   '%Y-%m-%d %H:%M:%S')
    conn.symbol_select(symbol)
    resultado = conn.read_ticks(symbol, start_time, end_time)
    df = pd.DataFrame(resultado)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df["volume"] = df["volume"].astype(float)
    resultado_json = df.to_dict(orient="records")
    return jsonify({
        "result": resultado_json
})

@app.route('/get_account_info', methods=['GET']) #done
def get_account_info():
    resultado = conn.get_account_info()
    resultado['_pnl_nao_realizado'] = 0
    return jsonify({
        "result": resultado
    })

@app.route('/read_OHLC',        methods=['GET']) #done
def read_OHLC():
    symbol = request.args.get("symbol")
    tf     = request.args.get("tf")
    n      = int(request.args.get("n"))
    conn.symbol_select(symbol)
    resultado = conn.read_OHLC(symbol,tf,n)
    resultado['time'] = resultado['time'].astype(str)
    return jsonify({
        "result": resultado.to_dict(orient='records')
    })

@app.route('/order',            methods=['GET'])
def order():
    print(f"====================> /order <====================")
    buy_sell = request.args.get("buy_sell")
    symbol   = request.args.get("symbol")
    volume_aux = request.args.get("volume")
    volume   = float(volume_aux)
    price    = float(request.args.get("price"))
    symb_sel_result = conn.symbol_select(symbol)
    order_result    = conn.order(buy_sell, symbol, volume, price)
    position = _read_positions(symbol)
    return jsonify({
        "symb_sel_result" : symb_sel_result,
        "order_result"    : order_result,
        "position"        : position,
    })

@app.route('/read_orders',      methods=['GET'])
def read_orders():
    symbol   = request.args.get("symbol")
    symb_sel_result    = conn.symbol_select(symbol)
    read_orders_result = conn.read_orders(symbol)
    resultado = []
    for order in read_orders_result:
        resultado.append(order._asdict())
    return jsonify({
        "symb_sel_result" : symb_sel_result,
        "order_result"    : read_orders_result
    })

@app.route('/read_info',        methods=['GET']) #done
def read_info():
    symbol = request.args.get("symbol")
    conn.symbol_select(symbol)
    ultimo_valor, preco_venda, preco_compra = conn.read_info(symbol)
    return jsonify({
        "ultimo_valor": ultimo_valor,
        "preco_venda":  preco_venda,
        "preco_compra": preco_compra
    })

@app.route('/read_price_day',   methods=['GET']) #done
def read_price_day():
    symbol = request.args.get("symbol")
    conn.symbol_select(symbol)
    last_close, current_open, current_value = conn.read_price_day(symbol)
    return jsonify({
        "last_close": last_close,
        "current_open":  current_open,
        "current_value": current_value
    })

@app.route('/read_position',    methods=['GET'])
def read_position():
    symbol = request.args.get("symbol")
    conn.symbol_select(symbol)
    time.sleep(0.01)
    position = conn.read_position(symbol)
    resposta = jsonify(position)
    return resposta

@app.route('/read_positions',   methods=['GET'])
def read_positions():
    symbol = request.args.get("symbol")
    positions = _read_positions(symbol)
    resposta = jsonify({
        positions
    })
    return resposta

def _read_positions(symbol):
    conn.symbol_select(symbol)
    positions = conn.read_positions(symbol)
    print(f"positions: {positions}")
    position = {
                'volume' : positions[3],
                'type'   : positions[2]
            }


    resposta = jsonify({
        positions
    })
    return positions

@app.route("/get_book",         methods=["GET"])
def get_book():
    symbol = request.args.get("symbol")
    conn.symbol_select(symbol)
    book = conn.get_book(symbol)
    if book is None:
        return jsonify({"erro": "Símbolo inválido"}), 400
    return jsonify({
        "book": book
    })

@app.route("/preco",            methods=["GET"])
def preco():
    symbol = request.args.get("symbol")
    contador = 0
    while contador < 100:
        resultado = conn.symbol_select(symbol)
        tick = conn.read_all_info(symbol)
        contador += 1
        if tick: 
            if tick.ask != 0.0 and tick.bid != 0.0:
                break
        time.sleep(0.02)
    if tick is None:
        return jsonify({"erro": "Símbolo inválido"}), 400
    return jsonify({
        "symbol": symbol,
        "bid":    tick.bid,
        "ask":    tick.ask,
        "last":   tick.last
    })

@app.route("/allinfo",          methods=["GET"])
def allinfo():
    simbolo = request.args.get("simbolo")
    result = conn.symbol_select(simbolo)
    if result:
        tick = conn.read_all_info(simbolo)
        if tick is None:
            return jsonify({
                "status":  "ok",
                "result":  "nok",
                "message": "Símbolo inválido",}), 400
        try:
            data = datetime.fromtimestamp(tick.expiration_time)
            data_formatada = data.strftime("%Y-%m-%d")
        except:
            data_formatada = ''
        return jsonify({
            "status":             "ok",
            "result":             "ok",
            "codigo":             tick.name,
            "strike":             tick.option_strike,
            "vencimento":         data_formatada,
            "option_right":       tick.option_right,
            "description":        tick.description,
            "bid":                tick.bid,
            "ask":                tick.ask,
            "last":               tick.last,
            "option_mode":        tick.option_mode,
            "price_change":       tick.price_change, 
            "price_volatility":   tick.price_volatility, 
            "price_theoretical":  tick.price_theoretical, 
            "price_greeks_delta": tick.price_greeks_delta, 
            "price_greeks_theta": tick.price_greeks_theta, 
            "price_greeks_gamma": tick.price_greeks_gamma, 
            "price_greeks_vega":  tick.price_greeks_vega, 
            "price_greeks_rho":   tick.price_greeks_rho, 
            "price_greeks_omega": tick.price_greeks_omega, 
            "price_sensitivity":  tick.price_sensitivity 
        })
    else:
        return jsonify({
                "status":  "ok",
                "result":  "nok",
                "message": "Símbolo inválido",})

@app.route("/candles",          methods=["GET"])
def candles():
    simbolo = request.args.get("simbolo")
    tf = request.args.get("tf")
    n = int(request.args.get("n"))

    rates = conn.read_candles(simbolo,tf,n)
    rates['time'] = pd.to_datetime(rates['time'])
    rates['data_curta'] = rates['time'].dt.strftime('%d/%m/%y')
    rates['hora_curta'] = rates['time'].dt.strftime('%H:%M')
    rates['data_hora_curta'] = rates['time'].dt.strftime('%d/%m/%y %H:%M')
    data_json = rates.to_dict(orient='records')
    return jsonify(data_json)

@app.route("/posicoes")
def posicoes():
    pos = conn.cliet.positions_get()
    res = [{
        "ticket": p.ticket,
        "symbol": p.symbol,
        "price_open": p.price_open,
        "volume": p.volume,
        "type": p.type
    } for p in pos]
    return jsonify(res)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print('Falta parâmetro do Broker')
        exit()

    brokers = ['clear', 'infinox']

    if sys.argv[1] == 'clear':
        server, login, password = mt5_clear_password()
    elif sys.argv[1] == 'infinox':
        server, login, password = infinox()
    else:
        exit()
    conn = MTrader(server, login, password, log_debug=False)

    app.run(host="0.0.0.0", port=5000) #, ssl_context=('cert.pem', 'key.pem'))
