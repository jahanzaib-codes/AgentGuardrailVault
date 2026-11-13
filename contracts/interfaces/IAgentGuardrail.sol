// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

interface IAgentGuardrail {
    struct SessionPolicy {
        bool isActive;
        uint64 expiresAt;
        uint128 dailySpendLimit;
        uint128 spentToday;
        uint64 lastEpochDay;
    }

    event SessionKeyRegistered(address indexed sessionKey, uint64 expiresAt, uint128 dailyLimit);
    event TargetWhitelisted(address indexed target, bool status);
    event SelectorWhitelisted(bytes4 indexed selector, bool status);
    event ExecutionIntercepted(address indexed agent, address indexed target, bytes4 selector, string reason);
    event GuardrailPassed(address indexed agent, address indexed target, uint256 value);
}
