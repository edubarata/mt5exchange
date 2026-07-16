# mt5_connection.py
import sys
import platform


class MT5ConnectionFactory:
    """Fábrica de conexões com o mercado (MT5).

    Dois eixos independentes:
    - fonte de dados: sempre conecta ao MT5 real (histórico, ticks, candles)
    - execução de ordens: simulada (RL/backtest) ou real (trading ao vivo)
    """

    @staticmethod
    def create_data_source(broker, platform_mode="auto"):
        """Sempre conecta ao MT5 real para leitura de dados/histórico."""
        print(150*'1')
        print(150*'1')
        print(150*'1')
        print(f"platform_mode: {platform_mode}")
        print(150*'1')
        print(150*'1')
        print(150*'1')
        if platform_mode == "auto":
            platform_mode = "windows" if platform.system() == "Windows" else "linux"
        print(150*'0')
        print(150*'0')
        print(150*'0')
        print(f"platform_mode: {platform_mode}")
        print(150*'0')
        print(150*'0')
        print(150*'0')

        if platform_mode == "windows":
            from mt5exchange.mt5exchange import MTrader
            from passwords import mt5_clear_password
            server, login, password = mt5_clear_password()
            print(150*'-')
            print(150*'-')
            print(150*'-')

            print(150*'-')
            print(150*'-')
            print(150*'-')
            server_novo   = broker['server']
            login_novo    = broker['login']
            password_novo = broker['password']
            print(f"Broker: server_novo: {server_novo}, login_novo: {login_novo}, password_novo: {password_novo}")
            conn = MTrader(server, login, password)
            print("Conectado na API MT5Exchange (Windows)")
        else:
            from mt5exchange.mt5api import MT5api
            conn = MT5api()
            print("Conectado na API MT5API (Linux)")
        return conn

    @staticmethod
    def create_executor(broker, mode="simulated"):
        """Execução de ordens: simulada (RL) ou real (trading ao vivo)."""
        if mode == "simulated":
            from app.rl.simulator import MT5Simulator
            print("Conectado na API Simulador (execução simulada)")
            return MT5Simulator()
        else:
            return MT5ConnectionFactory.create_data_source(broker)