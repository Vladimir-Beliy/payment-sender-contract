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

    constructor(address voucherSigner_, address paymentToken_)
        EIP712("Payment Sender", "1")
    {
        voucherSigner(voucherSigner_);
        paymentToken(paymentToken_);
    }

    function release(uint256 amount, bytes calldata voucher)
        external
        whenNotPaused
    {
        uint256 nonce_ = _nonce[msg.sender];

        require(
            _verifyVoucher(nonce_, amount, voucher),
            "PaymentSender: voucher is invalid"
        );

        _nonce[msg.sender] = nonce_ + 1;

        emit PaymentReleased(msg.sender, nonce_, amount);

        _paymentToken.safeTransfer(msg.sender, amount);
    }

    function pause() external onlyOwner {
        _pause();
    }

    function unpause() external onlyOwner {
        _unpause();
    }

    function voucherSigner(address voucherSigner_) public onlyOwner {
        require(
            voucherSigner_ != address(0),
            "PaymentSender: voucher signer is zero address"
        );
        require(
            voucherSigner_.code.length == 0,
            "PaymentSender: voucher signer is contract address"
        );

        _voucherSigner = voucherSigner_;
    }

    function paymentToken(address paymentToken_) public onlyOwner {
        require(
            paymentToken_ != address(0),
            "PaymentSender: payment token is zero address"
        );
        require(
            paymentToken_.code.length > 0,
            "PaymentSender: payment token isn't contract address"
        );

        _paymentToken = IERC20(paymentToken_);
    }

    function voucherSigner() external view returns (address) {
        return _voucherSigner;
    }

    function paymentToken() external view returns (IERC20) {
        return _paymentToken;
    }

    function nonce(address account) external view returns (uint256) {
        return _nonce[account];
    }

    function _verifyVoucher(
        uint256 nonce_,
        uint256 amount,
        bytes calldata voucher
    ) private view returns (bool) {
        bytes32 digest = _hashTypedDataV4(
            keccak256(
                abi.encode(
                    keccak256("PaymentVoucher(address payee,uint256 nonce,uint256 amount)"),
                    msg.sender,
                    nonce_,
                    amount
                )
            )
        );

        address signer = ECDSA.recover(digest, voucher);

        return signer == _voucherSigner;
    }
}
