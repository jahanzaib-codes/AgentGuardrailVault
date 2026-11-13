// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import "../interfaces/IAgentGuardrail.sol";
import "../interfaces/IOracleRouter.sol";

/**
 * @title AgentGuardrailVault
 * @author Jahanzaib (@jahanzaib-codes)
 * @notice Institutional ERC-4337 smart vault and on-chain policy gate for autonomous AI agents.
 * @dev Enforces multi-tier defense: Session Key validation, 24h spending velocity limits,
 *      calldata selector whitelist, and dynamic Oracle slippage corridors.
 */
contract AgentGuardrailVault is IAgentGuardrail {
    address public immutable protocolOwner;
    IOracleRouter public oracleRouter;

    // Ephemeral AI Agent Session Keys -> Policy Configuration
    mapping(address => SessionPolicy) public sessionPolicies;

    // Whitelisted execution targets (e.g., Aerodrome Router on Base, Camelot on Arbitrum)
    mapping(address => bool) public whitelistedTargets;

    // Whitelisted function selectors (e.g., swapExactTokensForTokens)
    mapping(bytes4 => bool) public authorizedSelectors;

    // Maximum allowable price deviation against oracle benchmark in basis points (100 = 1.00%)
    uint256 public maxSlippageBps = 100;

    // Emergency circuit breaker flag
    bool public isEmergencyHalted;

    // --- CUSTOM ERRORS (Gas-optimized) ---
    error Unauthorized();
    error SystemHalted();
    error SessionKeyInvalidOrExpired();
    error TargetNotPermitted(address target);
    error SelectorForbidden(bytes4 selector);
    error DailyVelocityExceeded(uint256 attempted, uint256 remainingLimit);
    error OracleSlippageBreached(uint256 oraclePrice, uint256 executionPrice);
    error ExecutionDispatchedFailed();
    error InvalidCalldataPayload();

    modifier onlyOwner() {
        if (msg.sender != protocolOwner) revert Unauthorized();
        _;
    }

    modifier whenNotHalted() {
        if (isEmergencyHalted) revert SystemHalted();
        _;
    }

    constructor(address _oracleRouter) {
        require(_oracleRouter != address(0), "Invalid oracle router");
        protocolOwner = msg.sender;
        oracleRouter = IOracleRouter(_oracleRouter);
    }

    // --- ADMINISTRATION ---

    function registerAgentSessionKey(
        address sessionKey,
        uint64 expiresAt,
        uint128 dailySpendLimit
    ) external onlyOwner {
        require(sessionKey != address(0), "Zero address key");
        require(expiresAt > block.timestamp, "Invalid expiration");

        sessionPolicies[sessionKey] = SessionPolicy({
            isActive: true,
            expiresAt: expiresAt,
            dailySpendLimit: dailySpendLimit,
            spentToday: 0,
            lastEpochDay: uint64(block.timestamp / 86400)
        });

        emit SessionKeyRegistered(sessionKey, expiresAt, dailySpendLimit);
    }

    function setWhitelistedTarget(address target, bool status) external onlyOwner {
        whitelistedTargets[target] = status;
        emit TargetWhitelisted(target, status);
    }

    function setAuthorizedSelector(bytes4 selector, bool status) external onlyOwner {
        authorizedSelectors[selector] = status;
        emit SelectorWhitelisted(selector, status);
    }

    function setSlippageTolerance(uint256 newSlippageBps) external onlyOwner {
        require(newSlippageBps <= 500, "Max slippage cap 5%");
        maxSlippageBps = newSlippageBps;
    }

    function tripEmergencyHalt() external {
        // Can be tripped by owner or automated monitoring daemon
        if (msg.sender != protocolOwner) revert Unauthorized();
        isEmergencyHalted = true;
    }

    function resetEmergencyHalt() external onlyOwner {
        isEmergencyHalted = false;
    }

    // --- AGENT ON-CHAIN EXECUTION GATE ---

    /**
     * @notice Primary execution gateway invoked by off-chain Autonomous AI Agents.
     * @param target Whitelisted DEX pool or protocol address.
     * @param value Native currency amount attached.
     * @param payload Encoded call bytes targeting the destination contract.
     * @param assetIn Asset being traded for oracle corridor verification.
     * @param proposedExecutionPrice Unit price at which the agent wants to execute.
     */
    function executeAsAgent(
        address target,
        uint256 value,
        bytes calldata payload,
        address assetIn,
        uint256 proposedExecutionPrice
    ) external whenNotHalted returns (bytes memory returnData) {
        // 1. Verify Session Key
        SessionPolicy storage policy = sessionPolicies[msg.sender];
        if (!policy.isActive || block.timestamp > policy.expiresAt) {
            revert SessionKeyInvalidOrExpired();
        }

        // 2. Validate Whitelisted Target Contract
        if (!whitelistedTargets[target]) {
            emit ExecutionIntercepted(msg.sender, target, bytes4(0), "Target unapproved");
            revert TargetNotPermitted(target);
        }

        // 3. Inspect Calldata Selector
        if (payload.length < 4) revert InvalidCalldataPayload();
        bytes4 selector = bytes4(payload[:4]);
        if (!authorizedSelectors[selector]) {
            emit ExecutionIntercepted(msg.sender, target, selector, "Selector forbidden");
            revert SelectorForbidden(selector);
        }

        // 4. Enforce 24-Hour Velocity Cap
        uint64 currentDay = uint64(block.timestamp / 86400);
        if (currentDay > policy.lastEpochDay) {
            policy.spentToday = 0;
            policy.lastEpochDay = currentDay;
        }

        if (policy.spentToday + value > policy.dailySpendLimit) {
            revert DailyVelocityExceeded(value, policy.dailySpendLimit - policy.spentToday);
        }
        policy.spentToday += uint128(value);

        // 5. Dynamic Oracle Corridor Slippage Verification
        if (assetIn != address(0) && address(oracleRouter) != address(0)) {
            uint256 benchmarkPrice = oracleRouter.getValidatedPrice(assetIn);
            uint256 delta = benchmarkPrice > proposedExecutionPrice 
                ? benchmarkPrice - proposedExecutionPrice 
                : proposedExecutionPrice - benchmarkPrice;

            uint256 calculatedSlippageBps = (delta * 10000) / benchmarkPrice;
            if (calculatedSlippageBps > maxSlippageBps) {
                emit ExecutionIntercepted(msg.sender, target, selector, "Oracle slippage breach");
                revert OracleSlippageBreached(benchmarkPrice, proposedExecutionPrice);
            }
        }

        // 6. Safe Call Dispatch
        bool success;
        (success, returnData) = target.call{value: value}(payload);
        if (!success) revert ExecutionDispatchedFailed();

        emit GuardrailPassed(msg.sender, target, value);
    }

    receive() external payable {}
}
