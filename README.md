# payment-sender-contract

The repo base on eth-brownie [framework](https://eth-brownie.readthedocs.io/en/stable/toctree.html) 🍪

PaymentSender releases payments with PaymentVoucher helps. PaymentVoucher is a [signed typed data](https://eips.ethereum.org/EIPS/eip-712). The Release method can be paused by an owner.

[Contract on Testnet](https://testnet.bscscan.com/address/0xf3eae947ba80f4213304dc5bf0554a4c92a3fe73)

#
### Requirements 🛠️
  - python 3.9.5
  - virtualenv 20.13.2
  - pip 21.3
  - eth-brownie 1.19.2
#
### Run environment 🚀
1.
```
python -m venv venv
```
or
```
python3.9 -m venv venv
```
2.
```
source ./venv/bin/activate
```
3.
```
pip install -r requirements.txt
```
#
### Testing 🤖
```
brownie test
```
#
### Run scripts 🦾
```
brownie run scripts/[script_name].py
```
#
### Deploy 🐎
```
brownie run scripts/deploy.py --network [bsc-test/bsc-main]
```
#
### Console 💻
```
brownie console
```
