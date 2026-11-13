// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

interface IOracleRouter {
    function getValidatedPrice(address asset) external view returns (uint256 price);
    function isSequencerActive() external view returns (bool);
}
