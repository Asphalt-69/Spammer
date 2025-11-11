import discord
import asyncio
import random
import time
import sys
from colorama import init, Fore, Style

#
init(autoreset=True)


try:
    from secrets import TOKENS
except ImportError:
    print(f"{Fore.RED}❌ Error: Please create secrets.py with your TOKENS list")
    sys.exit(1)


try:
    from spam import SPAM_MESSAGES
except ImportError:
    print(f"{Fore.RED}❌ Error: Please create spam.py with SPAM_MESSAGES list")
    sys.exit(1)


BLUE = Fore.BLUE
PINK = Fore.MAGENTA
GREEN = Fore.GREEN
RED = Fore.RED
RESET = Style.RESET_ALL


def print_banner():
    print(f"{BLUE}{Style.BRIGHT}")
    print("   ███████╗██████╗  █████╗ ███╗   ███╗███╗   ███╗███████╗██████╗ ")
    print("   ██╔════╝██╔══██╗██╔══██╗████╗ ████║████╗ ████║██╔════╝██╔══██╗")
    print("   ███████╗██████╔╝███████║██╔████╔██║██╔████╔██║█████╗  ██████╔╝")
    print("   ╚════██║██╔═══╝ ██╔══██║██║╚██╔╝██║██║╚██╔╝██║██╔══╝  ██╔══██╗")
    print("   ███████║██║     ██║  ██║██║ ╚═╝ ██║██║ ╚═╝ ██║███████╗██║  ██║")
    print("   ╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝     ╚═╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝")
    print(f"{PINK}╔══════════════════════════════════════════════════════════════╗")
    print(f"{PINK}║{BLUE}           U L T R A - F A S T  S E L F B O T           {PINK}║")
    print(f"{PINK}║{BLUE}            Created with ❤ by asphalt._.6              {PINK}║")
    print(f"{PINK}╚══════════════════════════════════════════════════════════════╝")
    print(RESET)


MAX_SPEED_DELAY = 0.001
RATE_LIMITED_DELAY = 0.1
RATE_LIMIT_BACKOFF = 5
START_COMMAND = "!start spam"
STOP_COMMAND = "!stop spam"
SPAM_WORD_COMMAND = "!spam"

class SelfBotClient(discord.Client):
    def __init__(self, token: str):
       
        super().__init__()
        self.token = token
        self.spam_tasks = {}
        self.rate_limited = False
        self.rate_limit_count = 0
        self.current_delay = MAX_SPEED_DELAY
        self.is_spamming = False
        self.custom_word_spam = False
        self.spam_word = ""

    async def on_ready(self):
        print(f"{GREEN}{self.user} ready and waiting for commands!{RESET}")

    async def on_message(self, message):
        
        if message.author != self.user:
            return
        
        
        is_dm = isinstance(message.channel, discord.DMChannel)
        channel_name = f"DM with {message.channel.recipient}" if is_dm else message.channel.name
        
        
        if message.content.lower() == START_COMMAND.lower():
            if not self.is_spamming:
                self.is_spamming = True
                self.custom_word_spam = False
                print(f"{GREEN}Starting spam in {channel_name}...{RESET}")
                
                asyncio.create_task(self.spam_messages(message.channel))
            else:
                await message.channel.send("Spam is already running!")
                
        
        elif message.content.lower() == STOP_COMMAND.lower():
            if self.is_spamming:
                self.is_spamming = False
                self.custom_word_spam = False
                print(f"{RED}Stopping spam...{RESET}")
                await message.channel.send("Spam stopped!")
            else:
                await message.channel.send("Spam isn't running!")
                
        
        elif message.content.lower().startswith(SPAM_WORD_COMMAND.lower()):
            
            parts = message.content.split(' ', 1)
            if len(parts) > 1:
                self.spam_word = parts[1]
                if not self.is_spamming:
                    self.is_spamming = True
                    self.custom_word_spam = True
                    print(f"{GREEN}Starting custom word spam ('{self.spam_word}') in {channel_name}...{RESET}")
                    
                    asyncio.create_task(self.spam_custom_word(message.channel))
                else:
                    await message.channel.send("Spam is already running! Use !stop spam first.")
            else:
                await message.channel.send("Please specify a word to spam. Usage: !spam [word]")

    async def spam_messages(self, channel):
        while self.is_spamming and not self.custom_word_spam:
            try:
                message = random.choice(SPAM_MESSAGES)
                await channel.send(message)
                print(f"{PINK}Sent: {message}{RESET}")
                await asyncio.sleep(self.current_delay)
            except discord.HTTPException as e:
                if e.status == 429:  # Rate limited
                    print(f"{RED}Rate limited! Waiting {RATE_LIMIT_BACKOFF} seconds...{RESET}")
                    self.rate_limited = True
                    self.rate_limit_count += 1
                    self.current_delay = RATE_LIMITED_DELAY
                    await asyncio.sleep(RATE_LIMIT_BACKOFF)
                else:
                    print(f"{RED}Error sending message: {e}{RESET}")
            except Exception as e:
                print(f"{RED}Unexpected error: {e}{RESET}")
                await asyncio.sleep(1)
                
    async def spam_custom_word(self, channel):
        while self.is_spamming and self.custom_word_spam:
            try:
                await channel.send(self.spam_word)
                print(f"{PINK}Sent: {self.spam_word}{RESET}")
                await asyncio.sleep(self.current_delay)
            except discord.HTTPException as e:
                if e.status == 429:  # Rate limited
                    print(f"{RED}Rate limited! Waiting {RATE_LIMIT_BACKOFF} seconds...{RESET}")
                    self.rate_limited = True
                    self.rate_limit_count += 1
                    self.current_delay = RATE_LIMITED_DELAY
                    await asyncio.sleep(RATE_LIMIT_BACKOFF)
                else:
                    print(f"{RED}Error sending message: {e}{RESET}")
            except Exception as e:
                print(f"{RED}Unexpected error: {e}{RESET}")
                await asyncio.sleep(1)

async def main():
    clients = []
    for i, token in enumerate(TOKENS):
        client = SelfBotClient(token)
        clients.append(client)
        print(f"{BLUE}Initializing client {i+1}...{RESET}")
        
        asyncio.create_task(client.start(token))
        await asyncio.sleep(1)  

    
    await asyncio.Future()  

if __name__ == "__main__":
    print_banner()
    print(f"{RED}⚠️  WARNING: Selfbots violate Discord's Terms of Service")
    print(f"{RED}⚠️  Use at your own risk - accounts may be banned")
    print(f"{PINK}────────────────────────────────────────────")
    
    print(f"{BLUE}Initializing {len(TOKENS)} ultra-fast selfbot clients...{RESET}")
    
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{RED}Shutting down selfbots...{RESET}")
    except Exception as e:
        print(f"{RED}Unexpected error: {e}{RESET}")
