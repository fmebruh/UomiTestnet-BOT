# UomiTestnet-BOT
# CHAIN SCRIPTERS - UOMI Testnet Bot

A professional, high-performance automation bot for the UOMI Testnet, revamped and customized by **CHAIN SCRIPTERS**. This tool is designed for advanced users who need to automate on-chain interactions across multiple accounts with enhanced reliability and Sybil resistance.

---

### **Community & Support**

Join our community for updates, support, and discussions about our tools.

- **Telegram:** [t.me/ChainScripters](https://t.me/ChainScripters)

---

### **Key Features**

This bot has been re-architected to be a robust and intelligent automation tool for the UOMI ecosystem.

- **Multi-Account Support:** Run an unlimited number of accounts by simply adding their private keys to `accounts.txt`.
- **Flexible Proxy Options:** Choose to run with a free public proxy list, your own private proxies from `proxy.txt`, or no proxy at all.
- **Interactive Task Menu:** A full in-terminal menu allows you to choose which actions to perform for your accounts:
  - Wrap UOMI to WUOMI
  - Unwrap WUOMI to UOMI
  - Perform random swaps between assets
  - Add liquidity to various pools
  - Run all features sequentially
- **Graceful Error Handling:** A failure on one account (e.g., invalid private key, insufficient funds) will not crash the bot. It logs the error and automatically moves on to the next account.
- **Modern & Reliable:** Built with modern, industry-standard Python libraries (`aiohttp`, `web3`) for stable, asynchronous performance.

---

### **Setup Instructions**

Follow these steps to get the bot up and running.

**1. Prerequisites:**
   - Make sure you have [Python](https://www.python.org/downloads/) (version 3.9 or higher) installed.

**2. Clone the Repository:**
   ```bash
   git clone https://github.com/fmebruh/UomiTestnet-BOT
   cd UomiTestnet-BOT
```
**3. Install Dependencies:
Run the following command in your terminal to install the necessary libraries from the requirements.txt file:

Bash
```
pip install -r requirements.txt 
```
4. Create Configuration Files:
You need to create two configuration files in the main folder:

accounts.txt: Add one private key per line.


```
0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
```
proxies.txt: Add one proxy per line. If you don't plan to use private proxies, you can leave this file empty.Format: ip:port or user:pass@ip:port

```
user1:pass1@192.168.1.1:8080
192.168.1.2:8888
```
Usage
To run the bot, simply execute the following command in your terminal:

Bash
```
python bot.py
```
The bot will start, display the CHAIN SCRIPTERS banner, and then guide you through an interactive menu to configure and start your desired tasks.

Disclaimer
This bot is intended for educational and testing purposes only. Automating interactions with blockchain networks carries inherent risks. The creators (CHAIN SCRIPTERS) are not responsible for any financial losses. Always
