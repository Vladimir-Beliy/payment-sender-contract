// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/utils/cryptography/draft-EIP712.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract PaymentSender is Ownable, Pausable, EIP712 {
    using SafeERC20 for IERC20;

    event PaymentReleased(address indexed payee, uint256 nonce, uint256 amount);

    address private _voucherSigner;
    IERC20 private _paymentToken;

    mapping(address => uint256) private _nonce;

    constructor(address voucherSigner_, IERC20 paymentToken_) EIP712("Payment Sender", "1") {
        _voucherSigner = voucherSigner_;
        _paymentToken = paymentToken_;
    }

    function release(uint256 amount, bytes calldata voucher) external whenNotPaused {
        uint256 nonce = _nonce[msg.sender];

        _verifyVoucher(nonce, amount, voucher);

        _nonce[msg.sender] = nonce + 1;

        emit PaymentReleased(msg.sender, nonce, amount);

        _paymentToken.safeTransfer(msg.sender, amount);
    }

    function voucherSigner(address voucherSigner_) external onlyOwner {
        _voucherSigner = voucherSigner_;
    }

    function paymentToken(IERC20 paymentToken_) external onlyOwner {
        _paymentToken = paymentToken_;
    }

    function pause() external onlyOwner {
        _pause();
    }

    function unpause() external onlyOwner {
        _unpause();
    }

    function voucherSigner() external view returns(address) {
        return _voucherSigner;
    }

    function paymentToken() external view returns(IERC20) {
        return _paymentToken;
    }

    function nonce(address account) external view returns(uint256) {
        return _nonce[account];
    }

    function _verifyVoucher(uint256 nonce, uint256 amount, bytes calldata voucher) private {
        bytes32 digest = _hashTypedDataV4(keccak256(abi.encode(
            keccak256("PaymentVoucher(address payee,uint256 nonce,uint256 amount)"),
            msg.sender,
            nonce,
            amount
        )));

        address signer = ECDSA.recover(digest, voucher);

        require(signer == _voucherSigner, "PaymentSender: voucher is invalid");
    }
}
