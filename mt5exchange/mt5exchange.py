VERSION = "0.1.5"
import pandas as pd
from datetime import datetime

class MTrader():
    def __init__(self,servidor,user_login,senha,verbose=True, log_debug=False):
        import MetaTrader5 as mt5
        self.mt5 = mt5
        if verbose:
            print(f"mt5exchange - Version {VERSION}{' - log para debug ativado' if log_debug else ''}")
            print("Estabelecendo Conexão com Metatrader 5:")
            print(f"  ServeR: {servidor}")
            print(f"  Login:  {str(user_login)}")
        self.client = self.mt5.initialize(login=user_login,server=servidor,password=senha)
        self.log_debug = log_debug
        if not self.client:
            print("Initialize() failed, error code =",self.mt5.last_error())
            self.error = True
        else:
            self.error = False
        self.dictionary_tf = {
            '1m'    : self.mt5.TIMEFRAME_M1,
            '2m'    : self.mt5.TIMEFRAME_M2,
            '3m'    : self.mt5.TIMEFRAME_M3,
            '4m'    : self.mt5.TIMEFRAME_M4,
            '5m'    : self.mt5.TIMEFRAME_M5,
            '6m'    : self.mt5.TIMEFRAME_M6,
            '10m'   : self.mt5.TIMEFRAME_M10,
            '12m'   : self.mt5.TIMEFRAME_M12,
            '15m'   : self.mt5.TIMEFRAME_M15,
            '20m'   : self.mt5.TIMEFRAME_M20,
            '30m'   : self.mt5.TIMEFRAME_M30,
            '1h'    : self.mt5.TIMEFRAME_H1,
            '2h'    : self.mt5.TIMEFRAME_H2,
            '3h'    : self.mt5.TIMEFRAME_H3,
            '4h'    : self.mt5.TIMEFRAME_H4,
            '8h'    : self.mt5.TIMEFRAME_H8,
            '12h'   : self.mt5.TIMEFRAME_H12,
            '1d'    : self.mt5.TIMEFRAME_D1,
            '1w'    : self.mt5.TIMEFRAME_W1,
            '1M'    : self.mt5.TIMEFRAME_MN1
        }

    def symbol_select(self, symbol):
        if self.log_debug: print(f"função symbol_select, input: {symbol}")
        result = self.mt5.symbol_select(symbol, True)
        if self.log_debug: print(f"função symbol_select, self.mt5.symbol_select({symbol}, True): {result}")
        return result

    def read_all_info(self,papel):
        if self.log_debug: print(f"função read_all_info, input: {papel}")
        symbol_info=self.mt5.symbol_info(papel)
        if self.log_debug: print(f"função read_all_info, self.mt5.symbol_info({papel}): {symbol_info}")
        if symbol_info!=None:
            return symbol_info
        else:
            return None

    def read_info(self,papel):
        symbol_info=self.mt5.symbol_info(papel)
        if symbol_info!=None:
            return symbol_info.last,symbol_info.bid,symbol_info.ask
        else:
            return 0,0,0

    def read_price_day(self,papel):
        rates = self.mt5.copy_rates_from_pos(papel, self.mt5.TIMEFRAME_D1, 0, 2)
        last_close = rates[0][4]
        current_value = rates[1][4]
        current_open = rates[1][1]
        return last_close, current_open, current_value

    def order(self, buy_sell, symbol, volume, price=0.0, stop=0.0, take=0.0):
        # 1. Verificar conexão com MT5
        if not self.mt5.initialize():
            print(f"MT5 não inicializado: {self.mt5.last_error()}")
            return None

        # 2. Verificar terminal info
        terminal = self.mt5.terminal_info()

        # 3. Verificar símbolo
        symbol_info = self.mt5.symbol_info(symbol)
        if symbol_info is None:
            print(f"Símbolo {symbol} não encontrado: {self.mt5.last_error()}")
            return None
        
        # 4. Garantir que o símbolo está visível no Market Watch
        if not symbol_info.visible:
            if not self.mt5.symbol_select(symbol, True):
                print(f"Falha ao selecionar símbolo: {self.mt5.last_error()}")
                return None
        slippage             = 5
        magic_number         = 434343

        action_mercado       = self.mt5.TRADE_ACTION_DEAL
        action_stop          = self.mt5.TRADE_ACTION_PENDING
        action_limit         = self.mt5.TRADE_ACTION_PENDING
        
        type_filling_mercado = self.mt5.ORDER_FILLING_IOC
        type_filling_stop    = self.mt5.ORDER_FILLING_RETURN
        type_filling_limit   = self.mt5.ORDER_FILLING_RETURN

        type_time_mercado    = self.mt5.ORDER_TIME_GTC
        type_time_stop       = self.mt5.ORDER_TIME_DAY
        type_time_limit      = self.mt5.ORDER_TIME_DAY

        symbol_info = self.mt5.symbol_info(symbol)

        if buy_sell in ['buy', 'sell']:
            order_request = {
                "action"       : action_mercado,
                "symbol"       : symbol,
                "volume"       : float(volume),  # garantir que é float
                "type"         : self.mt5.ORDER_TYPE_BUY if buy_sell == 'buy' else self.mt5.ORDER_TYPE_SELL,
                "price"        : symbol_info.ask if buy_sell == 'buy' else symbol_info.bid,
                "deviation"    : slippage,
                "magic"        : magic_number,
                "comment"      : f"mt5exchange {VERSION}",
                "type_filling" : type_filling_mercado,
                "type_time"    : type_time_mercado,
            }
        elif buy_sell in ['buy_stop', 'sell_stop']:
            order_request = {
                "action": action_stop,
                "symbol": symbol,
                "volume": float(volume),  # garantir que é float
                "type": self.mt5.ORDER_TYPE_BUY_STOP if buy_sell == 'buy_stop' else self.mt5.ORDER_TYPE_SELL_STOP,
                "price": float(price),
                "deviation": slippage,
                "magic": magic_number,
                "comment": f"mt5exchange {VERSION}",
                "type_filling": type_filling_stop,
                "type_time": type_time_stop,
            }
        elif buy_sell in ['buy_limit', 'sell_limit']:
            order_request = {
                "action": action_limit,
                "symbol": symbol,
                "volume": float(volume),  # garantir que é float
                "type": self.mt5.ORDER_TYPE_BUY_LIMIT if buy_sell == 'buy_limit' else self.mt5.ORDER_TYPE_SELL_LIMIT,
                "price": float(price),
                "deviation": slippage,
                "magic": magic_number,
                "comment": f"mt5exchange {VERSION}",
                "type_filling": type_filling_limit,
                "type_time": type_time_limit,
            }
        # {'action': 1, 'symbol': 'WINQ26', 'volume': 1.0, 'type': 1, 'price': 178260.0, 'slippage': 5, 'magic': 434343, 'comment': 'Ordem mercado mt5exchange 0.1.4', 'type_filling': 1, 'type_time': 0}
        order_result = self.mt5.order_send(order_request)
        if order_result is None:
            pass

            erro = self.mt5.last_error()
            print(f"order_send falhou. Código: {erro[0]}, Descrição: {erro[1]}")
        else:
            pass

        return order_result

    def order_ajust(self, symbol, stop=0.0, take=0.0, ticket=None):
        # 1. Verificar conexão com MT5
        if not self.mt5.initialize():
            print(f"MT5 não inicializado: {self.mt5.last_error()}")
            return None

        # 2. Verificar terminal info
        terminal = self.mt5.terminal_info()

        # 3. Verificar símbolo
        symbol_info = self.mt5.symbol_info(symbol)
        if symbol_info is None:
            print(f"Símbolo {symbol} não encontrado: {self.mt5.last_error()}")
            return None
        
        # 4. Garantir que o símbolo está visível no Market Watch
        if not symbol_info.visible:
            if not self.mt5.symbol_select(symbol, True):
                print(f"Falha ao selecionar símbolo: {self.mt5.last_error()}")
                return None
        slippage             = 5
        magic_number         = 434343

        action_mercado       = self.mt5.TRADE_ACTION_DEAL
        action_stop          = self.mt5.TRADE_ACTION_PENDING
        action_limit         = self.mt5.TRADE_ACTION_PENDING
        
        type_filling_mercado = self.mt5.ORDER_FILLING_IOC
        type_filling_stop    = self.mt5.ORDER_FILLING_RETURN
        type_filling_limit   = self.mt5.ORDER_FILLING_RETURN

        type_time_mercado    = self.mt5.ORDER_TIME_GTC
        type_time_stop       = self.mt5.ORDER_TIME_DAY
        type_time_limit      = self.mt5.ORDER_TIME_DAY

        symbol_info = self.mt5.symbol_info(symbol)
        if ticket == None:
            positions = self.mt5.positions_get(symbol=symbol)
            if positions:
                position = positions[-1]
                ticket   = position.ticket
                stop_loss   = stop
                take_profit = take
                print("Ticket:", ticket)
                print("Preço de abertura:", position.price_open)
                print("Type:", position.type)
        else:
            stop_loss   = stop
            take_profit = take
            
        order_request = {
            "action"   : self.mt5.TRADE_ACTION_SLTP,
            "symbol"   : symbol,
            "position" : ticket,
            "sl"       : stop_loss,
            "tp"       : take_profit,
        }
        order_result = self.mt5.order_send(order_request)
        if order_result is None:
            pass

            erro = self.mt5.last_error()
            print(f"order_send falhou. Código: {erro[0]}, Descrição: {erro[1]}")
        else:
            pass

        return order_result

    def read_positions(self, ativo):
        position = Position()
        aux = self.mt5.positions_get(symbol=ativo)
        for i in range(len(aux)):
            position.ticket          = aux[0][0]
            position.time            = str(pd.to_datetime(aux[0][1],unit='s'))[11:]
            position.time_msc        = pd.to_datetime(aux[0][2],unit='ms')
            position.time_update     = pd.to_datetime(aux[0][3],unit='ms')
            position.time_update_msc = pd.to_datetime(aux[0][4],unit='ms')
            position.type            = aux[0][5]   # definir aqui o que é type
            position.magic           = aux[0][6]
            position.identifier      = aux[0][7]
            position.reason          = aux[0][8]
            position.volume          = aux[0][9]
            position.price_open      = aux[0][10]
            position.sl              = aux[0][11]
            position.tp              = aux[0][12]
            position.price_current   = aux[0][13]
            position.swap            = aux[0][14]
            position.profit          = aux[0][15]
            position.symbol          = aux[0][16]
            position.comment         = aux[0][17]
            position.external_id     = aux[0][18]
        return position

    def read_position(self, ativo):
        info_posicoes = self.mt5.positions_get(symbol=ativo)
        if len(info_posicoes) == 0:
            return {}
        posicao_dic = info_posicoes[0]._asdict()
        return posicao_dic

    def verify_position(self,ativo,position_verify):
        position = Position()
        aux = self.mt5.positions_get(symbol=ativo)
        if len(aux) >= 1:
            return True,aux[0].price_open,aux[0].sl,aux[0].tp
        return False,0,0,0

    def read_orders(self,ativo):
        order = Order()
        aux = self.mt5.orders_get(symbol=ativo)
        for i in range(len(aux)):
            order.len             = aux[0][0]
            order.status          = str(pd.to_datetime(aux[0][1],unit='s'))[11:]
            order.boleta          = pd.to_datetime(aux[0][2],unit='ms')
            order.time_setup      = pd.to_datetime(aux[0][3],unit='ms')
            order.time_setup_msc  = pd.to_datetime(aux[0][4],unit='ms')
            order.time_expiration = aux[0][5]
            order.type            = aux[0][6]
            order.type_time       = aux[0][7]
            order.type_filling    = aux[0][8]
            order.state           = aux[0][9]
            order.magic           = aux[0][10]
            order.volume_current  = aux[0][11]
            order.price_open      = aux[0][12]
            order.sl              = aux[0][13]
            order.tp              = aux[0][14]
            order.price_current   = aux[0][15]
            order.symbol          = aux[0][16]
        return order

    def verify_order(self,ativo,order_verify):
        order = Order()
        aux = self.mt5.orders_get(symbol=ativo)
        for i in range(len(aux)):
            if order_verify == aux[i].ticket:
                return True,aux[i].price_open,aux[i].sl,aux[i].tp
        return False,0,0,0

    def read_candles(self,symbol,tf,n=1):
        # symbol = 'PETR4'
        # tf = '1m' / '5m' / '1h' / '1d' / ...
        # n = 0 (opened candle)
        # n = 1 (last closed candle)
        # n = 2.. (las 2.. closed candles)
        tamanho_bloco = 99998
        n_blocos = n//tamanho_bloco
        residual = n % tamanho_bloco
        n = n + 1
        timef = self.dictionary_tf[tf]
        if n_blocos>0:
            df = pd.DataFrame(self.mt5.copy_rates_from_pos(symbol, timef, (n_blocos-1)*tamanho_bloco+residual, tamanho_bloco))
            for i in range(n_blocos-1):
                df_aux = pd.DataFrame(self.mt5.copy_rates_from_pos(symbol, timef, (n_blocos-2-i)*tamanho_bloco+residual, tamanho_bloco))
                df = pd.concat([df,df_aux])
            if residual>0:
                df_aux = pd.DataFrame(self.mt5.copy_rates_from_pos(symbol, timef, 0, residual))
                df = pd.concat([df,df_aux])
        else:
            df = pd.DataFrame(self.mt5.copy_rates_from_pos(symbol, timef, 0, residual))
        df = df.rename({'real_volume': 'volume'}, axis=1)
        try:
            df['volume'] = df['volume'].astype(float)
        except:
            df['volume'] = 0
        try:
            df['tick_volume'] = df['tick_volume'].astype(float)
        except:
            df['tick_volume'] = 0
        df['time'] = pd.to_datetime(df['time'],unit='s')
        df.drop(["spread"], axis=1,inplace=True)
        return df

    def read_candles_from(self, symbol, tf, initial_date, n):
        print(f"read_candles_from(symbol: {symbol}, tf: {tf}, initial_date: {initial_date}, n: {n})")
        timef = self.dictionary_tf[tf]
        #initial_date = datetime.strptime('2026-07-20 10:00:00', '%Y-%m-%d %H:%M:%S')
        print(f"read_candles_from(symbol: {symbol}, timef: {timef}, initial_date: {initial_date}, n: {n})")
        rates = self.mt5.copy_rates_from(symbol, timef, initial_date, n)
        print(f"rates: {rates}")
        print(f"last_error: {self.mt5.last_error()}")
        df    = pd.DataFrame(rates)
        print(f"df:")
        print(df)
        df = df.rename({'real_volume': 'volume'}, axis=1)
        df['volume'] = df['volume'].astype(float)
        df['time'] = pd.to_datetime(df['time'],unit='s')
        #df.drop(["tick_volume"], axis=1,inplace=True)
        df.drop(["spread"], axis=1,inplace=True)
        return df

    def read_candles_range(self, symbol, tf, initial_date, final_date):
        print(f"read_candles_range(symbol: {symbol}, tf: {tf}, initial_date: {initial_date}, final_date: {final_date})")
        timef = self.dictionary_tf[tf]
        #initial_date = datetime.strptime('2026-07-20 10:00:00', '%Y-%m-%d %H:%M:%S')
        print(f"read_candles_range(symbol: {symbol}, timef: {timef}, initial_date: {initial_date}, final_date: {final_date})")
        rates = self.mt5.copy_rates_range(symbol, timef, initial_date, final_date)
        print(f"rates: {rates}")
        print(f"last_error: {self.mt5.last_error()}")
        df    = pd.DataFrame(rates)
        print(f"df:")
        print(df)
        df = df.rename({'real_volume': 'volume'}, axis=1)
        df['volume'] = df['volume'].astype(float)
        df['time'] = pd.to_datetime(df['time'],unit='s')
        #df.drop(["tick_volume"], axis=1,inplace=True)
        df.drop(["spread"], axis=1,inplace=True)
        return df

    def read_OHLC(self,symbol,tf,n=1):
        # symbol = 'PETR4'
        # tf = '1m' / '5m' / '1h' / '1d' / ...
        # n = 0 (last open candle)
        # n = 1 (last closed candle)
        # n = 2.. (las 2.. closed candles)
        n = n + 1
        timef = self.dictionary_tf[tf]
        df = pd.DataFrame(self.mt5.copy_rates_from_pos(symbol, timef, 0, n))
        df = df.rename({'real_volume': 'volume'}, axis=1)
        df['volume'] = df['volume'].astype(float)
        df['time'] = pd.to_datetime(df['time'],unit='s')
        df.drop(["tick_volume"], axis=1,inplace=True)
        df.drop(["spread"], axis=1,inplace=True)
        return df

    def read_ticks(self, symbol, start_time, end_time):
        # formato do dado: (time, bid, ask, last, volume, time_msc, flags, volume_real)
        # time     : Timestamp Unix em segundos.
        # time_msc : Timestamp em milissegundos desde 01/01/1970.
        # flags    : TICK_FLAG_BID    = 2  (00000010)
        #            TICK_FLAG_ASK    = 4  (00000100)
        #            TICK_FLAG_LAST   = 8  (00001000)
        #            TICK_FLAG_VOLUME = 16 (00010000)
        #            TICK_FLAG_BUY    = 32 (00100000)
        #            TICK_FLAG_SELL   = 64 (01000000)

        ticks = self.mt5.copy_ticks_range(
            symbol,
            start_time,
            end_time,
            self.mt5.COPY_TICKS_ALL
        )
        if ticks is None:
            erro = self.mt5.last_error()
            raise RuntimeError(f"MT5 copy_ticks_range falhou: {erro}")
        return ticks

    def get_book(self, symbol):
        if self.mt5.market_book_add(symbol):
            book = self.mt5.market_book_get(symbol)
            self.mt5.market_book_release(symbol)
        else:
            print("Erro ao assinar o book de ofertas:", self.mt5.last_error())
        return book

    def close_orders(self, verbose=False):
        positions = self.mt5.positions_get()

        if positions is None or len(positions) == 0:
            if verbose:
                print("Nenhuma posição aberta encontrada.")
            return False

        # Escolher a posição que deseja fechar (exemplo: a primeira posição)
        position = positions[0]
        ticket = position.ticket
        symbol = position.symbol
        volume = position.volume
        order_type = position.type

        # Obter preço atual de mercado para fechamento
        symbol_info_tick = self.mt5.symbol_info_tick(symbol)
        if symbol_info_tick is None:
            print(f"Erro ao obter dados do símbolo {symbol}")
            #self.mt5.shutdown()
            #exit()

        # Determinar o preço de fechamento
        if order_type == self.mt5.ORDER_TYPE_BUY:
            close_price = symbol_info_tick.bid  # Para fechar uma compra, vendemos no preço bid
            close_type = self.mt5.ORDER_TYPE_SELL
        else:
            close_price = symbol_info_tick.ask  # Para fechar uma venda, compramos no preço ask
            close_type = self.mt5.ORDER_TYPE_BUY

        # Criar a solicitação de fechamento
        close_request = {
            "action": self.mt5.TRADE_ACTION_DEAL,  # Executar ordem a mercado
            "symbol": symbol,
            "volume": volume,
            "type": close_type,  # Fechamento oposto ao tipo da posição original
            "position": ticket,  # Indica qual posição queremos fechar
            "price": close_price,  # Preço atual do mercado
            "deviation": 5,  # Slippage permitido em pontos
            "magic": position.magic,  # Manter o mesmo número mágico da ordem original
            "comment": "Fechamento via Python",
            "type_filling": self.mt5.ORDER_FILLING_IOC,  # Executar imediatamente ou cancelar
            "type_time": self.mt5.ORDER_TIME_GTC,  # Ordem válida até cancelamento
        }

        # Enviar solicitação para fechar a posição
        close_result = self.mt5.order_send(close_request)

        # Verificar resultado da ordem
        #if close_result.retcode == self.mt5.TRADE_RETCODE_DONE:
        #    print(f"Posição {ticket} fechada com sucesso!")
        #else:
        #    print(f"Erro ao fechar posição {ticket}: {close_result.retcode}")
        return close_result

    def get_account_info(self):
        info = self.mt5.account_info()
        print(info)
        info_dict = info._asdict()
        info_dict['_pnl_nao_realizado'] = 0
        return info_dict

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

