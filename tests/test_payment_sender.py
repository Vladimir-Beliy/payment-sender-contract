import pytest
from brownie import accounts, exceptions, TestToken
from eth_account import Account
from scripts.deploy import deploy_sender_with_token

from scripts.test_helpers import create_voucher


def test_payee_can_release_payment():
    payee = accounts[1]
    voucher_signer = Account.create()
    payment_amount = 100

    payment_sender, token = deploy_sender_with_token(voucher_signer)

    payee_nonce = payment_sender.nonce(payee)

    voucher = create_voucher(
        voucher_signer,
        payment_sender.address,
        payee.address,
        payee_nonce,
        payment_amount,
    )

    assert token.balanceOf(payee) == 0

    payment_sender.release(payment_amount, voucher, {"from": payee})

    assert token.balanceOf(payee) == payment_amount


def test_payee_cant_use_voucher_twice():
    payee = accounts[1]
    voucher_signer = Account.create()
    payment_amount = 100

    payment_sender, _ = deploy_sender_with_token(voucher_signer)

    payee_nonce = payment_sender.nonce(payee)

    voucher = create_voucher(
        voucher_signer,
        payment_sender.address,
        payee.address,
        payee_nonce,
        payment_amount,
    )

    payment_sender.release(payment_amount, voucher, {"from": payee})

    with pytest.raises(exceptions.VirtualMachineError, match="voucher is invalid"):
        payment_sender.release(payment_amount, voucher, {"from": payee})


def test_payee_cant_use_invalid_voucher():
    payee = accounts[1]
    voucher_signer = Account.create()
    invalid_voucher_signer = Account.create()
    payment_amount = 100

    payment_sender, _ = deploy_sender_with_token(voucher_signer)

    payee_nonce = payment_sender.nonce(payee)

    invalid_voucher = create_voucher(
        invalid_voucher_signer,
        payment_sender.address,
        payee.address,
        payee_nonce,
        payment_amount,
    )

    with pytest.raises(exceptions.VirtualMachineError, match="voucher is invalid"):
        payment_sender.release(payment_amount, invalid_voucher, {"from": payee})


def test_payee_cant_release_payment_when_pause():
    owner = accounts[0]
    payee = accounts[1]
    voucher_signer = Account.create()
    payment_amount = 100

    payment_sender, _ = deploy_sender_with_token(voucher_signer)

    payee_nonce = payment_sender.nonce(payee)

    voucher = create_voucher(
        voucher_signer,
        payment_sender.address,
        payee.address,
        payee_nonce,
        payment_amount,
    )

    payment_sender.pause({"from": owner})

    assert payment_sender.paused() == True

    with pytest.raises(exceptions.VirtualMachineError, match="paused"):
        payment_sender.release(payment_amount, voucher, {"from": payee})


def test_release_emits_event():
    payee = accounts[1]
    voucher_signer = Account.create()
    payment_amount = 100

    payment_sender, _ = deploy_sender_with_token(voucher_signer)

    payee_nonce = payment_sender.nonce(payee)

    voucher = create_voucher(
        voucher_signer,
        payment_sender.address,
        payee.address,
        payee_nonce,
        payment_amount,
    )

    tx = payment_sender.release(payment_amount, voucher, {"from": payee})

    assert tx.events["PaymentReleased"]["payee"] == payee
    assert tx.events["PaymentReleased"]["nonce"] == payee_nonce
    assert tx.events["PaymentReleased"]["amount"] == payment_amount


def test_only_owner_can_pause():
    owner = accounts[0]
    random_account = accounts[1]

    payment_sender, _ = deploy_sender_with_token()

    assert payment_sender.paused() == False

    with pytest.raises(exceptions.VirtualMachineError, match="caller is not the owner"):
        payment_sender.pause({"from": random_account})

    payment_sender.pause({"from": owner})

    assert payment_sender.paused() == True


def test_only_owner_can_unpause():
    owner = accounts[0]
    random_account = accounts[1]

    payment_sender, _ = deploy_sender_with_token()

    payment_sender.pause({"from": owner})

    assert payment_sender.paused() == True

    with pytest.raises(exceptions.VirtualMachineError, match="caller is not the owner"):
        payment_sender.unpause({"from": random_account})

    payment_sender.unpause({"from": owner})

    assert payment_sender.paused() == False


def test_only_owner_can_change_voucher_signer():
    owner = accounts[0]
    voucher_signer = accounts[1]
    new_voucher_signer = accounts[2]
    random_account = accounts[3]

    payment_sender, _ = deploy_sender_with_token(voucher_signer)

    assert payment_sender.voucherSigner() == voucher_signer

    with pytest.raises(exceptions.VirtualMachineError, match="caller is not the owner"):
        payment_sender.voucherSigner(new_voucher_signer, {"from": random_account})

    payment_sender.voucherSigner(new_voucher_signer, {"from": owner})

    assert payment_sender.voucherSigner() == new_voucher_signer


def test_only_owner_can_change_payment_token():
    owner = accounts[0]
    random_account = accounts[1]

    payment_sender, token = deploy_sender_with_token()
    new_token = TestToken.deploy({"from": owner})

    assert payment_sender.paymentToken() == token.address

    with pytest.raises(exceptions.VirtualMachineError, match="caller is not the owner"):
        payment_sender.paymentToken(new_token, {"from": random_account})

    payment_sender.paymentToken(new_token, {"from": owner})

    assert payment_sender.paymentToken() == new_token.address
