# Differences from the original code
- Mostly re-written from scratch
- Better error correction.
- Autologin fixed.
- Faster.
- All heroes are sent to work regardless of their stamina.

# I will not provide support on Windows.
# Install on archlinux
```
sudo pacman -Syu python-pip tk
git clone https://github.com/lobomfz/bombcrypto-bot
cd bombcrypto-bot
sudo pip install -r requirements.txt
python bcryptobot.py
```
## To run with logging:
```
python bcryptobot.py 2>&1 | tee log
```

# Config
Thresholds and refresh intervals are on the top of the script itself. Modify it as you need.

## My wallet for donations: 0xFDf479c7723Eda2945cb5F3EE9bf8181821D12a5
### Original fork:
#### Wallet: 0xbd06182D8360FB7AC1B05e871e56c76372510dDf
#### Paypal: [Donate](https://www.paypal.com/donate?hosted_button_id=JVYSC6ZYCNQQQ)
