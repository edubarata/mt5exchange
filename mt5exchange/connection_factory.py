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
    def create_data_source(platform_mode="auto"):
        """Sempre conecta ao MT5 real para leitura de dados/histórico."""
        if platform_mode == "auto":
            platform_mode = "windows" if platform.system() == "Windows" else "linux"

        if platform_mode == "windows":
            from mt5exchange.mt5exchange import MTrader
            from passwords import mt5_clear_password
            server, login, password = mt5_clear_password()
            conn = MTrader(server, login, password)
            print("Conectado na API MT5Exchange (Windows)")
        else:
            from mt5exchange.mt5api import MT5api
            conn = MT5api()
            print("Conectado na API MT5API (Linux)")
        return conn

    @staticmethod
    def create_executor(mode="simulated"):
        """Execução de ordens: simulada (RL) ou real (trading ao vivo)."""
        if mode == "simulated":
            from app.rl.simulator import MT5Simulator
            print("Conectado na API Simulador (execução simulada)")
            return MT5Simulator()
        else:
            return MT5ConnectionFactory.create_data_source()