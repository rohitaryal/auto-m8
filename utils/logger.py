import sys
import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)

class Logger:
    @staticmethod
    def log(message: str):
        print(f"{Fore.CYAN}{Style.BRIGHT}[ + ]{Style.RESET_ALL} {message}")

    @staticmethod
    def print(message: str):
        print(f"{Fore.WHITE}{Style.BRIGHT}[ + ]{Style.RESET_ALL} {message}")

    @staticmethod
    def info(message: str):
        print(f"{Fore.BLUE}{Style.BRIGHT}[ i ]{Style.RESET_ALL} {message}")

    @staticmethod
    def error(message: str):
        print(f"{Fore.RED}{Style.BRIGHT}[ ! ]{Style.RESET_ALL} {message}")

    @staticmethod
    def warning(message: str):
        print(f"{Fore.YELLOW}{Style.BRIGHT}[ w ]{Style.RESET_ALL} {message}")

    @staticmethod
    def exit(message: str, code: int = 1):
        print(f"{Fore.MAGENTA}{Style.BRIGHT}[ x ]{Style.RESET_ALL} {message}")
        sys.exit(code)

    @staticmethod
    def indexed(message: str, index: int = 1):
        print(f"{Fore.MAGENTA}[ {index} ] {Fore.RESET} {message}")

    @staticmethod
    def input(message: str) -> str:
        return input(f"{Fore.GREEN}{Style.BRIGHT}[ ? ]{Style.RESET_ALL} {message}: ").strip()

# Example usage
if __name__ == "__main__":
    Logger.log("This is a log message")
    Logger.print("This is a normal print message")
    Logger.info("This is an info message")
    Logger.error("This is an error message")
    Logger.warning("This is a warning message")
    Logger.exit("Exiting the program")

