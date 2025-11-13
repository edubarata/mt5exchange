import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime,timedelta

class MTrader():
    def __init__(self,servidor,user_login,senha,verbose=True):
        if verbose:
            print("Estabelecendo Conexão com Metatrader 5:")
            print("  Server: "+servidor)
            print("  Login:  "+str(user_login))
        self.client = mt5.initialize(login=user_login,server=servidor,password=senha)
        if not self.client:
            print("Initialize() failed, error code =",mt5.last_error())
            self.error = True
            quit()
        else:
            self.error = False

    def symbol_select(self, symbol):
        resposta = mt5.symbol_select(symbol, True)
        return resposta

    def read_price_day(self,papel):
        rates = mt5.copy_rates_from_pos(papel, mt5.TIMEFRAME_D1, 0, 2)
        fechamento_anterior = rates[0][4]
        valor_atual = rates[1][4]
        abertura_atual = rates[1][1]
        return fechamento_anterior,abertura_atual,valor_atual

    def read_info(self,papel):
        symbol_info=mt5.symbol_info(papel)

        if symbol_info!=None:
            return symbol_info.last,symbol_info.bid,symbol_info.ask
        else:
            return 0,0,0

    def read_positions(self,ativo):
        position = Position()
        aux = mt5.positions_get(symbol=ativo)
        for i in range(len(aux)):
            position.ticket          = aux[0][0]
            position.time            = str(pd.to_datetime(aux[0][1],unit='s'))[11:]
            position.time_msc        = pd.to_datetime(aux[0][2],unit='ms')
            position.time_update     = pd.to_datetime(aux[0][3],unit='ms')
            position.time_update_msc = pd.to_datetime(aux[0][4],unit='ms')
            position.type            = aux[0][5]
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

    def read_position(self,ativo):
        #print('ativo:',ativo)
        info_posicoes = mt5.positions_get(symbol=ativo)
        try:
            if len(info_posicoes) == 0:
                df = pd.DataFrame()
                return df
        except:
            print('Programa Terminado por erro')
            df = pd.DataFrame()
            return df
        #print('info_posicoes-123 - len=',len(info_posicoes))
        #print(info_posicoes)
        
        
        df = pd.DataFrame(list(info_posicoes),columns=info_posicoes[0]._asdict().keys())
        df ['time'] = pd.to_datetime (df ['time'], unit='s')
        return df

        aux = mt5.positions_get(symbol=ativo)
        #print('aux')
        #print(aux)
        position = pd.DataFrame(aux)
        #print('position')
        #print(position)
        return position

    def verify_position(self,ativo,position_verify):
        position = Position()
        aux = mt5.positions_get(symbol=ativo)
        #print('ddd-1')
        #print(pd.DataFrame(aux))
        #print('ddd-2')
        if len(aux) >= 1:
            return True,aux[0].price_open,aux[0].sl,aux[0].tp
        return False,0,0,0

    def read_order(self,ativo):
        order = Order()
        aux = mt5.orders_get(symbol=ativo)
        print(aux)
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
        aux = mt5.orders_get(symbol=ativo)
        for i in range(len(aux)):
            if order_verify == aux[i].ticket:
                return True,aux[i].price_open,aux[i].sl,aux[i].tp
        return False,0,0,0

    def read_candles(self,symbol,tf,n=1,time_index=False):
        # symbol = 'PETR4'
        # tf = '1m' / '5m' / '1h' / '1d' / ...
        # n = 0 (opened candle)
        # n = 1 (last closed candle)
        # n = 2.. (las 2.. closed candles)
        tamanho_bloco = 99998
        n_blocos = n//tamanho_bloco
        residual = n % tamanho_bloco
        dictionary = {
            '1m':  mt5.TIMEFRAME_M1,
            '2m':  mt5.TIMEFRAME_M2,
            '5m':  mt5.TIMEFRAME_M5,
            '15m': mt5.TIMEFRAME_M15,
            '30m': mt5.TIMEFRAME_M30,
            '1h':  mt5.TIMEFRAME_H1,
            '1d':  mt5.TIMEFRAME_D1
        }
        n = n + 1
        timef = dictionary[tf]
        if n_blocos>0:
            df = pd.DataFrame(mt5.copy_rates_from_pos(symbol, timef, (n_blocos-1)*tamanho_bloco+residual, tamanho_bloco))
            for i in range(n_blocos-1):
                df_aux = pd.DataFrame(mt5.copy_rates_from_pos(symbol, timef, (n_blocos-2-i)*tamanho_bloco+residual, tamanho_bloco))
                df = pd.concat([df,df_aux])
            if residual>0:
                df_aux = pd.DataFrame(mt5.copy_rates_from_pos(symbol, timef, 0, residual))
                df = pd.concat([df,df_aux])
        else:
            df = pd.DataFrame(mt5.copy_rates_from_pos(symbol, timef, 0, residual))
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

    def read_candles_(self,symbol,tf,n=0,verbose=False):
        # Faz a leitura de "n" candles de "symbol" no timeframe "tf"
        # Se n == 0 devolve o candle atual ainda nao fechado

        candles = mt5.get_klines(symbol=symbol, interval=tf, limit=1)
        if n==0:
            df = pd.DataFrame(candles)
            df.columns = ['time','open','high','low','close','volume','a','b','c','d','e','f']
            df.drop(['a','b','c','d','e','f'],axis=1,inplace=True)
            df['time'] = pd.to_datetime(df['time'], unit='ms')
            df.set_index('time',inplace=True)
            return df
        if   tf == '1m':  delta =    60000
        elif tf == '5m':  delta =   300000
        elif tf == '15m': delta =   900000
        elif tf == '1h':  delta =  3600000
        elif tf == '1d':  delta = 86400000
        else:
            print('tf error')
            quit()
        t_atual = candles[0][0]
        df = pd.DataFrame()
        while n > 0:
            if verbose:
                print('Lendo histórico. n = {}   '.format(n),end='\r')
            if n > 500:
                tini = t_atual - n * delta
                n_candles = 500
                n = n - 500
            else:
                tini = t_atual - n * delta
                n_candles = n
                n = 0
            candles = self.client.get_klines(symbol=symbol, interval=tf, limit=n_candles, startTime=tini)
            c = pd.DataFrame(candles)
            c.columns = ['time','open','high','low','close','volume','a','b','c','d','e','f']
            c.drop(['a','b','c','d','e','f'],axis=1,inplace=True)
            c['time'] = pd.to_datetime(c['time'], unit='ms')
            df = pd.concat([df, c])
        if verbose:
            print(50*' ')
        df = df.astype({"open": float, "high": float, "low": float, "close": float, "volume": float})
        df.reset_index(drop=True,inplace=True)
        return(df)

    def read_OHLC(self,symbol,tf,n=1,time_index=False):
        # symbol = 'PETR4'
        # tf = '1m' / '5m' / '1h' / '1d' / ...
        # n = 0 (last open candle)
        # n = 1 (last closed candle)
        # n = 2.. (las 2.. closed candles)
        dictionary = {
            '1m':mt5.TIMEFRAME_M1,
            '5m':mt5.TIMEFRAME_M5,
            '1h':mt5.TIMEFRAME_H1,
            '1d':mt5.TIMEFRAME_D1
        }
        n = n + 1
        timef = dictionary[tf]
        df = pd.DataFrame(mt5.copy_rates_from_pos(symbol, timef, 0, n))
        df = df.rename({'real_volume': 'volume'}, axis=1)
        df['volume'] = df['volume'].astype(float)
        df['time'] = pd.to_datetime(df['time'],unit='s')
        df.drop(["tick_volume"], axis=1,inplace=True)
        df.drop(["spread"], axis=1,inplace=True)
        return df

    def get_book_não_funciona(aelf, symbol):
        if mt5.market_book_add(symbol):
            print(f"Assinatura bem-sucedida do book de ofertas para {symbol}")
            book = mt5.market_book_get(symbol)
            print(f'symbol: {symbol}')
            print('book:')
            print(book)
            if book is None:
                print("Erro ao obter o book:", mt5.last_error())
            for level in book:
                print(level._asdict())
            print("-" * 40)

            mt5.market_book_release(symbol)
        else:
            print("Erro ao assinar o book de ofertas:", mt5.last_error())
        return book

    def get_book_(self,ativo,data_inicio,n=1000):
        '''
        TICK_FLAG define possíveis sinalizadores para ticks. Esses sinalizadores são usados para descrever os ticks recebidos pelas funções copy_ticks_from() e copy_ticks_range().

        Identificador         Descrição

        TICK_FLAG_BID         preço Bid alterado
        TICK_FLAG_ASK         preço Ask alterado
        TICK_FLAG_LAST        preço Last alterado
        TICK_FLAG_VOLUME      volume alterado (Volume)
        TICK_FLAG_BUY         preço da última compra alterado (Buy)
        TICK_FLAG_SELL        preço da última venda alterado (Sell)
        '''
        print(mt5.TICK_FLAG_BID,'preço Bid alterado')
        print(mt5.TICK_FLAG_ASK,'preço Ask alterado')
        print(mt5.TICK_FLAG_LAST,'preço Last alterado')
        print(mt5.TICK_FLAG_VOLUME,'volume alterado (Volume)')
        print(mt5.TICK_FLAG_BUY,'preço da última compra alterado (Buy)')
        print(mt5.TICK_FLAG_SELL,'preço da última venda alterado (Sell)')

        ativo = mt5.copy_ticks_from(ativo,data_inicio,n,mt5.COPY_TICKS_ALL)
        ativo = pd.DataFrame(ativo)
        print('ativo111')
        print(ativo)
        ativo['time']=pd.to_datetime(ativo['time'],unit='s')
        return ativo

    def order(self,buy_sell, symbol, volume):
        slippage = 5  # Slippage permitido em pontos
        magic_number = 434343  # Número mágico para identificar a ordem

        # Obter preço atual de mercado
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            print(f"Símbolo {symbol} não encontrado")
            mt5.shutdown()
            exit()

        #price = mt5.symbol_info_tick(symbol).ask  # Preço de compra (ask)

        # Criar a solicitação de compra
        order_request = {
            "action": mt5.TRADE_ACTION_DEAL,  # Ordem a mercado
            "symbol": symbol,
            "volume": volume,
            "type": mt5.ORDER_TYPE_BUY if buy_sell == 'buy' else mt5.ORDER_TYPE_SELL,  # Compra
            #"price": price,
            "price": symbol_info.ask,
            "slippage": slippage,
            "magic": magic_number,
            "comment": "Ordem de compra via mt5ai",
            "type_filling": mt5.ORDER_FILLING_IOC,  # Imediato ou cancelar
            "type_time": mt5.ORDER_TIME_GTC,  # Válida até cancelamento
        }

        # Enviar a ordem
        order_result = mt5.order_send(order_request)

        # Verificar resultado da ordem
        #if order_result.retcode == mt5.TRADE_RETCODE_DONE:
        #    print(f"Ordem de compra executada com sucesso! Ticket: {order_result.order}")
        #else:
        #    print(f"Falha ao enviar ordem: {order_result.retcode}")
        
        return order_result

    def close_orders(self, verbose=False):
        positions = mt5.positions_get()

        if positions is None or len(positions) == 0:
            if verbose:
                print("Nenhuma posição aberta encontrada.")
            #mt5.shutdown()
            #exit()
            return False

        # Escolher a posição que deseja fechar (exemplo: a primeira posição)
        position = positions[0]
        ticket = position.ticket
        symbol = position.symbol
        volume = position.volume
        order_type = position.type

        # Obter preço atual de mercado para fechamento
        symbol_info_tick = mt5.symbol_info_tick(symbol)
        if symbol_info_tick is None:
            print(f"Erro ao obter dados do símbolo {symbol}")
            #mt5.shutdown()
            #exit()

        # Determinar o preço de fechamento
        if order_type == mt5.ORDER_TYPE_BUY:
            close_price = symbol_info_tick.bid  # Para fechar uma compra, vendemos no preço bid
            close_type = mt5.ORDER_TYPE_SELL
        else:
            close_price = symbol_info_tick.ask  # Para fechar uma venda, compramos no preço ask
            close_type = mt5.ORDER_TYPE_BUY

        # Criar a solicitação de fechamento
        close_request = {
            "action": mt5.TRADE_ACTION_DEAL,  # Executar ordem a mercado
            "symbol": symbol,
            "volume": volume,
            "type": close_type,  # Fechamento oposto ao tipo da posição original
            "position": ticket,  # Indica qual posição queremos fechar
            "price": close_price,  # Preço atual do mercado
            "deviation": 5,  # Slippage permitido em pontos
            "magic": position.magic,  # Manter o mesmo número mágico da ordem original
            "comment": "Fechamento via Python",
            "type_filling": mt5.ORDER_FILLING_IOC,  # Executar imediatamente ou cancelar
            "type_time": mt5.ORDER_TIME_GTC,  # Ordem válida até cancelamento
        }

        # Enviar solicitação para fechar a posição
        close_result = mt5.order_send(close_request)

        # Verificar resultado da ordem
        #if close_result.retcode == mt5.TRADE_RETCODE_DONE:
        #    print(f"Posição {ticket} fechada com sucesso!")
        #else:
        #    print(f"Erro ao fechar posição {ticket}: {close_result.retcode}")
        return close_result

class Tick:
    def __init__(self):
        self.time        = ''
        self.bid         = 0.0
        self.bidqty      = 0.0
        self.ask         = 0.0
        self.askqty      = 0.0
        self.last        = 0.0
        self.volume      = 0.0
        self.time_msc    = ''
        self.flags       = 0
        self.volume_real = 0.0

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

