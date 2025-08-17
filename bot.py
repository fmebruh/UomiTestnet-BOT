import asyncio
import json
import os
import random
import re
import time
from datetime import datetime

import pytz
from aiohttp import BasicAuth, ClientSession, ClientTimeout
from aiohttp.client_exceptions import ClientResponseError
from aiohttp_socks import ProxyConnector
from colorama import Fore, Style, init
from eth_account import Account
from eth_abi.abi import encode
from eth_utils import to_bytes
from web3 import Web3
from web3.exceptions import TransactionNotFound

# --- 1. Initial Setup ---
init(autoreset=True)
wib = pytz.timezone('Asia/Jakarta')

class ChainScriptersUOMIBot:
    def __init__(self):
        # --- Constants ---
        self.RPC_URL = "https://finney.uomi.ai/"
        self.WUOMI_CONTRACT_ADDRESS = "0x5FCa78E132dF589c1c799F906dC867124a2567b2"
        self.USDC_CONTRACT_ADDRESS = "0xAA9C4829415BCe70c434b7349b628017C59EC2b1"
        self.SYN_CONTRACT_ADDRESS = "0x2922B2Ca5EB6b02fc5E1EBE57Fc1972eBB99F7e0"
        self.SIM_CONTRACT_ADDRESS = "0x04B03e3859A25040E373cC9E8806d79596D70686"
        self.EXECUTE_ROUTER_ADDRESS = "0x197EEAd5Fe3DB82c4Cd55C5752Bc87AEdE11f230"
        self.POSITION_ROUTER_ADDRESS = "0x906515Dc7c32ab887C8B8Dce6463ac3a7816Af38"
        self.QUOTER_ROUTER_ADDRESS = "0xCcB2B2F8395e4462d28703469F84c95293845332"
        self.ERC20_ABI = json.loads('[{"type":"function","name":"balanceOf","stateMutability":"view","inputs":[{"name":"address","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},{"type":"function","name":"decimals","stateMutability":"view","inputs":[],"outputs":[{"name":"","type":"uint8"}]},{"type":"function","name":"allowance","stateMutability":"view","inputs":[{"name":"owner","type":"address"},{"name":"spender","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},{"type":"function","name":"approve","stateMutability":"nonpayable","inputs":[{"name":"spender","type":"address"},{"name":"amount","type":"uint256"}],"outputs":[{"name":"","type":"bool"}]},{"type":"function","name":"deposit","stateMutability":"payable","inputs":[],"outputs":[]},{"type":"function","name":"withdraw","stateMutability":"nonpayable","inputs":[{"name":"wad","type":"uint256"}],"outputs":[]}]')
        self.UOMI_ABI = json.loads('[{"type":"function","name":"quoteExactInput","stateMutability":"nonpayable","inputs":[{"internalType":"bytes","name":"path","type":"bytes"},{"internalType":"uint256","name":"amountIn","type":"uint256"}],"outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}]},{"type":"function","name":"execute","stateMutability":"payable","inputs":[{"internalType":"bytes","name":"commands","type":"bytes"},{"internalType":"bytes[]","name":"inputs","type":"bytes[]"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"outputs":[]},{"type":"function","name":"multicall","stateMutability":"payable","inputs":[{"internalType":"bytes[]","name":"data","type":"bytes[]"}],"outputs":[{"internalType":"bytes[]","name":"results","type":"bytes[]"}]},{"type":"function","name":"mint","stateMutability":"nonpayable","inputs":[{"type":"tuple","name":"params","internalType":"struct INonfungiblePositionManager.MintParams","components":[{"internalType":"address","name":"token0","type":"address"},{"internalType":"address","name":"token1","type":"address"},{"internalType":"uint24","name":"fee","type":"uint24"},{"internalType":"int24","name":"tickLower","type":"int24"},{"internalType":"int24","name":"tickUpper","type":"int24"},{"internalType":"uint256","name":"amount0Desired","type":"uint256"},{"internalType":"uint256","name":"amount1Desired","type":"uint256"},{"internalType":"uint256","name":"amount0Min","type":"uint256"},{"internalType":"uint256","name":"amount1Min","type":"uint256"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}]}],"outputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"uint128","name":"liquidity","type":"uint128"},{"internalType":"uint256","name":"amount0","type":"uint256"},{"internalType":"uint256","name":"amount1","type":"uint256"}]}]')
        
        # --- State ---
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.used_nonce = {}
        self.user_choices = {}

    # --- UI & Logging ---
    def log(self, message, level="INFO"):
        now = datetime.now(wib).strftime('%H:%M:%S')
        color_map = {"INFO": Fore.CYAN, "SUCCESS": Fore.GREEN, "WARNING": Fore.YELLOW, "ERROR": Fore.RED}
        print(f"{Fore.MAGENTA}[{now}]{Style.RESET_ALL} {color_map.get(level, Fore.WHITE)}{message}{Style.RESET_ALL}", flush=True)

    def display_header(self):
        art = """
██████╗██╗  ██╗ █████╗ ██╗███╗   ██╗                               
██╔════╝██║  ██║██╔══██╗██║████╗  ██║                               
██║     ███████║███████║██║██╔██╗ ██║                               
██║     ██╔══██║██╔══██║██║██║╚██╗██║                               
╚██████╗██║  ██║██║  ██║██║██║ ╚████║                               
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝                               
                                                                    
███████╗ ██████╗██████╗ ██╗██████╗ ████████╗███████╗██████╗ ███████╗
██╔════╝██╔════╝██╔══██╗██║██╔══██╗╚══██╔══╝██╔════╝██╔══██╗██╔════╝
███████╗██║     ██████╔╝██║██████╔╝   ██║   █████╗  ██████╔╝███████╗
╚════██║██║     ██╔══██╗██║██╔═══╝    ██║   ██╔══╝  ██╔══██╗╚════██║
███████║╚██████╗██║  ██║██║██║        ██║   ███████╗██║  ██║███████║
╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝╚═╝        ╚═╝   ╚══════╝╚═╝  ╚═╝╚══════╝
        """
        print(Fore.CYAN + Style.BRIGHT + art)
        print(Fore.YELLOW + Style.BRIGHT + "--- UOMI Testnet Bot by CHAIN SCRIPTERS ---\n")

    def get_user_choices(self):
        """Interactive prompts to configure the bot run."""
        # Run Mode
        print(Fore.YELLOW + "Select Run Mode:")
        print("1. Run once for all accounts and then exit.")
        print("2. Run on a continuous 24-26 hour schedule.")
        while True:
            try:
                self.user_choices['run_mode'] = int(input(Fore.CYAN + "Choose [1/2] -> " + Style.RESET_ALL))
                if self.user_choices['run_mode'] in [1, 2]: break
                else: self.log("Invalid choice. Please enter 1 or 2.", "ERROR")
            except ValueError: self.log("Invalid input. Please enter a number.", "ERROR")

        # Proxy Mode
        print(Fore.YELLOW + "\nSelect Proxy Mode:")
        print("1. Use free proxies from Proxyscrape.")
        print("2. Use private proxies from proxy.txt.")
        print("3. Run without proxies.")
        while True:
            try:
                self.user_choices['proxy_mode'] = int(input(Fore.CYAN + "Choose [1/2/3] -> " + Style.RESET_ALL))
                if self.user_choices['proxy_mode'] in [1, 2, 3]: break
                else: self.log("Invalid choice. Please enter 1, 2, or 3.", "ERROR")
            except ValueError: self.log("Invalid input. Please enter a number.", "ERROR")
        
        # Other questions (wrap, swap, etc.) can be added here in the same pattern.
        # For now, we will run all features by default.
        self.user_choices['wrap_amount'] = 0.01 # Example default
        self.user_choices['swap_count'] = 2 # Example default
        self.user_choices['min_swap_amount'] = 0.001 # Example default
        self.user_choices['max_swap_amount'] = 0.005 # Example default
        self.user_choices['liquidity_count'] = 1 # Example default
        self.user_choices['min_delay'] = 10 # Example default
        self.user_choices['max_delay'] = 20 # Example default
        
    # --- Proxy & Network ---
    async def load_proxies(self):
        choice = self.user_choices.get('proxy_mode')
        if choice == 3:
            self.log("Running without proxies.", "INFO")
            return
        
        filename = "proxy.txt"
        if choice == 1:
            try:
                self.log("Fetching free proxies from Proxyscrape...", "INFO")
                async with ClientSession() as session:
                    async with session.get("https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all") as response:
                        response.raise_for_status()
                        content = await response.text()
                        self.proxies = [line.strip() for line in content.splitlines() if line.strip()]
                        self.log(f"Loaded {len(self.proxies)} free proxies.", "SUCCESS")
            except Exception as e:
                self.log(f"Failed to fetch free proxies: {e}. Continuing without proxies.", "ERROR")
        
        elif choice == 2:
            if not os.path.exists(filename):
                self.log("proxy.txt not found. Continuing without proxies.", "ERROR")
                return
            with open(filename, 'r') as f:
                self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
            self.log(f"Loaded {len(self.proxies)} private proxies.", "SUCCESS")

    def get_proxy_for_account(self, address):
        if not self.proxies:
            return None
        if address not in self.account_proxies:
            self.account_proxies[address] = self.proxies[self.proxy_index % len(self.proxies)]
            self.proxy_index += 1
        return self.account_proxies[address]

    async def get_web3_instance(self, proxy=None):
        """Creates a Web3 instance, with proxy if provided."""
        request_kwargs = {"timeout": 60}
        if proxy:
            proxy_url = f"http://{proxy}" if "://" not in proxy else proxy
            request_kwargs["proxies"] = {"http": proxy_url, "https": proxy_url}
        
        for attempt in range(3): # Retry connection
            try:
                web3 = Web3(Web3.HTTPProvider(self.RPC_URL, request_kwargs=request_kwargs))
                if await asyncio.to_thread(web3.eth.get_block_number):
                    return web3
            except Exception as e:
                self.log(f"Failed to connect to RPC (Attempt {attempt + 1}): {e}", "WARNING")
                await asyncio.sleep(5)
        return None

    # --- On-Chain Actions ---
    # ... [All the on-chain functions like perform_wrapped, perform_swap, etc. go here]
    # ... [They would be refactored to use the new `get_web3_instance` and logging]

    async def process_account(self, private_key, proxy):
        """Main processing logic for a single account."""
        try:
            account = Account.from_key(private_key)
            address = account.address
            self.log(f"Processing account: {address[:6]}...{address[-4:]}", "INFO")
        except Exception as e:
            self.log(f"Invalid private key: {private_key[:6]}... - {e}", "ERROR")
            return

        web3 = await self.get_web3_instance(proxy)
        if not web3:
            self.log(f"Could not establish RPC connection for {address}. Skipping.", "ERROR")
            return
            
        self.used_nonce[address] = await asyncio.to_thread(web3.eth.get_transaction_count, address)

        # Example of running all features
        self.log(f"Starting all tasks for {address}", "INFO")
        # await self.process_option_1(account, address, web3) # Wrap
        # await asyncio.sleep(random.uniform(self.user_choices['min_delay'], self.user_choices['max_delay']))
        # await self.process_option_3(account, address, web3) # Swap
        # await asyncio.sleep(random.uniform(self.user_choices['min_delay'], self.user_choices['max_delay']))
        # await self.process_option_4(account, address, web3) # Liquidity
        self.log(f"Dummy run for {address}. Implement actual calls here.", "SUCCESS")


    async def main(self):
        """Main execution loop."""
        self.display_header()
        self.get_user_choices()
        await self.load_proxies()

        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            self.log("'accounts.txt' not found. Please create it.", "ERROR")
            return
        
        self.log(f"Loaded {len(accounts)} accounts.", "INFO")

        while True:
            for i, account_pk in enumerate(accounts):
                proxy = self.get_proxy_for_account(account_pk) if self.proxies else None
                await self.process_account(account_pk, proxy)
                self.log(f"Finished processing account {i+1}/{len(accounts)}.", "SUCCESS")
                if i < len(accounts) - 1:
                    delay_seconds = random.uniform(20, 40)
                    self.log(f"Waiting for {delay_seconds:.0f} seconds before next account...", "INFO")
                    await asyncio.sleep(delay_seconds)

            if self.user_choices['run_mode'] == 1:
                self.log("Run once complete. Exiting.", "SUCCESS")
                break
            
            sleep_duration = random.uniform(24 * 3600, 26 * 3600)
            sleep_hours = sleep_duration / 3600
            self.log(f"All accounts processed. Sleeping for {sleep_hours:.1f} hours...", "INFO")
            await asyncio.sleep(sleep_duration)

if __name__ == "__main__":
    try:
        bot = ChainScriptersUOMIBot()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print("\n" + Fore.RED + "Exiting bot...")
