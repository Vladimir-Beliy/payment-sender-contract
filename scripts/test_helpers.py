from brownie import chain, TestToken, PaymentSender, accounts
from eth_account import Account
from eip712.messages import EIP712Message

NAME = "Payment Sender"
VERSION = "1"


def create_voucher(signer: Account, verifying_contract, payee, nonce, amount):
    class PaymentVoucher(EIP712Message):
        _name_: "string" = NAME
        _version_: "string" = VERSION
        _chainId_: "uint256" = chain.id
        _verifyingContract_: "address" = verifying_contract

        payee: "address"
        nonce: "uint256"
        amount: "uint256"

    msg = PaymentVoucher(payee, nonce, amount)
    signedMsg = Account.sign_message(msg.signable_message, signer.key)

    return signedMsg.signature
