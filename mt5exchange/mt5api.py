VERSION = "0.1.3"
import requests
import pandas as pd
import subprocess
import os

BASE_URL = "http://127.0.0.1:5000"

class MT5api():
    def __init__(self): #(self,servidor,user_login,senha,verbose=True, log_debug=False):
        pass
        #env = os.environ.copy()
        #env["WINEPREFIX"] = os.path.expanduser("~/.mt5")
        #subprocess.Popen(
        #    ["wine", "python", "api_mt5.py"],
        #    env=env
        #)
        return
        if verbose:
            print(f"mt5exchange - Version {VERSION}{' - log para debug ativado' if log_debug else ''}")
            print("Estabelecendo Conexão com Metatrader 5:")
            print("  Server: "+servidor)
            print("  Login:  "+str(user_login))
        return
        self.client = mt5.initialize(login=user_login,server=servidor,password=senha)
        self.log_debug = log_debug
        if not self.client:
            print("Initialize() failed, error code =",mt5.last_error())
            self.error = True
        else:
            self.error = False

    def _pnl_nao_realizado(self, symbol) -> float:
        position = self.read_positions(symbol) # print -> {'type': 1, 'volume': 1.0} type = 1 Vendido, type = 0 Comprado
        print(f"========================> Position")
        print(position)
        if position['volume'] == 0: # self.position da classe MT5Simulator: -1 Vendido, 0 Líquido, 1 Comprado
            return 0.0
        info = self.read_info(symbol)  # print -> 'info: (176460.0, 176465.0, 176460.0)' (last, bid, ask)
        print(f"info: {info}")
        print(f"info[1]: {info[1]}")
        if position['type'] == 0:
            preco_atual = info[2]
        else:
            preco_atual = info[1]
        preco_medio = 0
        valor_por_ponto = 0.2 # self._valor_por_ponto(self.simulator.ativo)
        resposta = position['volume'] * (preco_atual - preco_medio) * valor_por_ponto
        """
        tick = self.simulator.obter_tick_atual('_pnl_nao_realizado')
        preco_atual = tick['last'] # tick['bid'] if self.position == 2 else tick['ask']
        valor_por_ponto = self._valor_por_ponto(self.simulator.ativo)
        return self.position * (preco_atual - self.preco_medio) * valor_por_ponto
        """

    def symbol_select(self, symbol): #done
        url           = f"{BASE_URL}/symbol_select"
        params        = {"symbol": symbol}
        response      = requests.get(url, params=params)
        return response.json()

    def read_all_info(self,symbol): #done
        url           = f"{BASE_URL}/read_all_info"
        params        = {"symbol": symbol}
        response      = requests.get(url, params=params)
        if response.status_code != 200:
            return None
        data = response.json()["result"]
        return data

    def read_info(self,papel): #done
        url           = f"{BASE_URL}/read_info"
        params        = {"symbol": papel}
        response      = requests.get(url, params=params)
        dados         = response.json()
        return dados['ultimo_valor'], dados['preco_compra'], dados['preco_venda']

    def read_price_day(self,papel): #done
        url           = f"{BASE_URL}/read_price_day"
        params        = {"symbol": papel}
        response      = requests.get(url, params=params)
        dados         = response.json()
        return {
            'last_close'   : dados['last_close'],
            'current_open' : dados['current_open'],
            'current_value': dados['current_value']
        }

    def order(self, buy_sell, symbol, volume, price):
        url           = f"{BASE_URL}/order"
        params        = {"buy_sell": buy_sell ,"symbol": symbol, "volume": volume, "price": price}
        response      = requests.get(url, params=params)
        order_result  = response.json()
        return order_result

    def read_position(self,symbol):
        url           = f"{BASE_URL}/read_position"
        params        = {"symbol": symbol}
        response      = requests.get(url, params=params)
        dados         = response.json()
        return (dados)

    def read_positions(self, symbol):
        url           = f"{BASE_URL}/read_positions"
        params        = {"symbol": symbol}
        response      = requests.get(url, params=params)
        dados         = response.json()
        return (dados)

    def verify_position(self, symbol, position_verify):
        url           = f"{BASE_URL}/verify_position"
        params        = {"symbol": symbol, "position_verify": position_verify}
        response      = requests.get(url, params=params)
        book          = response.json()
        return book

    def read_orders(self,ativo):
        url           = f"{BASE_URL}/read_orders"
        params        = {"symbol": ativo}
        response      = requests.get(url, params=params)
        order         = response.json()
        return order

    def verify_order(self,ativo, order_verify):
        url           = f"{BASE_URL}/verify_order"
        params        = {"symbol": ativo, "order_verify": order_verify}
        response      = requests.get(url, params=params)
        order         = response.json()
        return False,0,0,0

    def read_candles(self,symbol,tf,n=1): #done
        url           = f"{BASE_URL}/read_candles"
        params        = {"symbol": symbol, "tf": tf, "n": n}
        response      = requests.get(url, params=params)
        response_dict = response.json()["result"]
        df = pd.DataFrame(response_dict)
        df["time"] = pd.to_datetime(df["time"])
        df["volume"] = df["volume"].astype(float)
        df["tick_volume"] = df["tick_volume"].astype(float)
        #df.set_index("time", inplace=True)
        return df

    def read_OHLC(self,symbol,tf,n=1):
        url           = f"{BASE_URL}/read_OHLC"
        params        = {"symbol": symbol, "tf": tf, "n": n}
        response      = requests.get(url, params=params)
        df            = pd.DataFrame(response.json()["result"])
        df["time"]    = pd.to_datetime(df["time"])
        df.set_index("time", inplace=True)
        return df
 
    def read_ticks(self,symbol,start_time,end_time):
        url           = f"{BASE_URL}/read_ticks"
        params        = {"symbol": symbol, "start_time": start_time, "end_time": end_time}
        response      = requests.get(url, params=params)
        response_dict = response.json()["result"]
        df = pd.DataFrame(response_dict)
        try:
            df["time"] = pd.to_datetime(df["time"])
            df["volume"] = df["volume"].astype(float)
            #df.set_index("time", inplace=True)
        except:
            pass
        return df

    def get_book(self, symbol):
        url           = f"{BASE_URL}/get_book"
        params        = {"symbol": symbol}
        response      = requests.get(url, params=params)
        book          = response.json()
        return book

    def close_orders(self, verbose=False):
        url           = f"{BASE_URL}/close_orders"
        params        = {}
        response      = requests.get(url, params=params)
        close_result  = response.json()
        return close_result

    def get_account_info(self):
        url           = f"{BASE_URL}/get_account_info"
        params        = {}
        response      = requests.get(url)
        dic           = response.json()
        return dic["result"]

class Position:
    def __init__(self):
        self.len             = 0
        self.ticket          = 0
        self.time            = ''
        self.time_msc        = ''
        self.time_update     = ''
        self.time_update_msc = ''
        self.type            = 0
        self.magic           = 0
        self.identifier      = 0
        self.reason          = 0
        self.volume          = 0.0
        self.price_open      = 0.0
        self.sl              = 0.0
        self.tp              = 0.0
        self.price_current   = 0.0
        self.swap            = 0
        self.profit          = 0
        self.symbol          = ''
        self.comment         = ''
        self.external_id     = 0

class Order:
    def __init__(self):
        self.len             = 0
        self.status          = False
        self.boleta          = 0          # ticket
        self.time_setup      = 0          # time_setup
        self.time_setup_msc  = 0          # time_setup_msc
        self.time_expiration = 0          # time_expiration
        self.type            = 0          # type
        self.type_time       = 0          # type_time
        self.type_filling    = 0          # type_filling
        self.state           = 0          # state
        self.magic           = 0          # magic
        self.volume_current  = 0.0        # volume_current
        self.price_open      = 0.0        # price_open
        self.sl              = 0.0        # sl
        self.tp              = 0.0        # tp
        self.price_current   = 0.0        # price_current
        self.symbol          = ''         # symbol

