from brownie import TestToken, PaymentSender, accounts, config, network
from eth_account import Account


def deploy_sender_with_token(_voucher_signer=Account.create()):
    if network.show_active() == "development":
        owner = accounts[0]
        voucher_signer = _voucher_signer.address
        publish_source = None
    elif network.show_active() == "ganache-local":
        owner = accounts[0]
        voucher_signer = config["wallets"]["voucher_signer_pub_key"]
        publish_source = None
    else:
        owner = accounts.add(config["wallets"]["deployer_privet_key"])
        voucher_signer = config["wallets"]["voucher_signer_pub_key"]
        publish_source = True

    test_token = TestToken.deploy({"from": owner})

    payment_sender = PaymentSender.deploy(
        voucher_signer,
        test_token.address,
        {"from": owner},
        publish_source=publish_source,
    )

    tx = test_token.transfer(
        payment_sender.address,
        test_token.balanceOf(owner),
        {"from": owner},
    )

    tx.wait(1)

    return payment_sender, test_token


def main():
    deploy_sender_with_token()
