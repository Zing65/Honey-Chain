// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title HoneyBatchRegistry
 * @dev On-chain registry for HoneyChain honey batch verification and royalty enforcement.
 * Built for SIH 2026 (Problem Statement 26021, Ministry of MSME / KVIC).
 *
 * Core Concept:
 * 1. Beekeepers anchor cryptographic fingerprints (hashes) of honey harvest batches.
 * 2. Downstream buyers (processors, brands, retailers) must reference the original batch
 *    when recording resale transactions.
 * 3. The contract tracks downstream resale value and calculates the guaranteed royalty
 *    owed back to the original rural beekeeper (producer of record).
 */
contract HoneyBatchRegistry {

    /// @notice Royalty percentage in basis points (1500 = 15.00%)
    uint256 public constant ROYALTY_BPS = 1500;
    uint256 public constant BPS_DENOMINATOR = 10000;

    /// @dev Structure representing a verified harvest batch anchored by a beekeeper
    struct Batch {
        string batchId;           // Human-readable batch identifier (e.g. "BATCH-2026-KVIC-001")
        bytes32 batchHash;        // SHA-256 / Keccak-256 fingerprint of canonical batch metadata
        address anchoredBy;       // Wallet address of the beekeeper (producer of record)
        uint256 anchoredAt;       // Block timestamp when anchored
        uint256 cumulativeSales;  // Total downstream sales value recorded against this batch (in wei/cents)
        uint256 totalQuantitySold;// Total quantity resold downstream (in grams/kg)
        bool exists;              // Existence flag
    }

    /// @dev Structure tracking downstream resale claims (processor -> brand -> retailer)
    struct ResaleClaim {
        address claimant;         // Downstream entity (processor/brand/retailer)
        uint256 quantitySold;     // Quantity sold in this transaction
        uint256 priceSold;        // Total gross revenue for this resale
        uint256 claimedAt;        // Timestamp of claim
    }

    // Mapping from human-readable batchId string to batchHash
    mapping(string => bytes32) private _batchIdToHash;

    // Mapping from cryptographic batchHash to Batch record
    mapping(bytes32 => Batch) private _batches;

    // Mapping from batchHash to array of resale claims
    mapping(bytes32 => ResaleClaim[]) private _resaleClaims;

    // Events
    event BatchAnchored(
        string batchId,
        bytes32 indexed batchHash,
        address indexed anchoredBy,
        uint256 timestamp
    );

    event BatchClaimed(
        string batchId,
        address indexed claimant,
        uint256 quantitySold,
        uint256 priceSold,
        uint256 timestamp
    );

    /**
     * @notice Anchors a new harvest batch on the blockchain.
     * @dev Reverts if the batchId or batchHash has already been registered.
     * Storing only the cryptographic hash ensures data privacy, minimal gas fees,
     * and tamper-proof verification against off-chain batch details.
     *
     * @param batchHash The keccak256 hash of the canonical batch JSON data.
     * @param batchId Human-readable identifier assigned to the harvest.
     */
    function anchorBatch(bytes32 batchHash, string calldata batchId) external {
        require(bytes(batchId).length > 0, "Batch ID cannot be empty");
        require(batchHash != bytes32(0), "Batch hash cannot be zero");
        require(_batchIdToHash[batchId] == bytes32(0), "Batch ID already exists");
        require(!_batches[batchHash].exists, "Batch hash already registered");

        _batchIdToHash[batchId] = batchHash;
        _batches[batchHash] = Batch({
            batchId: batchId,
            batchHash: batchHash,
            anchoredBy: msg.sender,
            anchoredAt: block.timestamp,
            cumulativeSales: 0,
            totalQuantitySold: 0,
            exists: true
        });

        emit BatchAnchored(batchId, batchHash, msg.sender, block.timestamp);
    }

    /**
     * @notice Verifies a batch using its human-readable ID.
     * @dev Public view method used by QR code verification pages and consumers.
     * Free to call (no gas).
     *
     * @param batchId The human-readable batch ID printed on the honey jar's QR code.
     * @return batchHash The cryptographic fingerprint anchored on-chain.
     * @return anchoredBy The wallet address of the original beekeeper.
     * @return anchoredAt The immutable timestamp of when the batch was anchored.
     */
    function verifyBatch(string calldata batchId)
        external
        view
        returns (
            bytes32 batchHash,
            address anchoredBy,
            uint256 anchoredAt
        )
    {
        bytes32 hash = _batchIdToHash[batchId];
        require(hash != bytes32(0), "Batch ID not found");
        Batch storage b = _batches[hash];
        return (b.batchHash, b.anchoredBy, b.anchoredAt);
    }

    /**
     * @notice Records a downstream resale claim against an existing batch.
     * @dev Called by downstream supply chain actors (e.g. honey processing unit, brand, distributor).
     * Links the claimant, original beekeeper, and resale price to establish full traceability.
     *
     * @param batchHash The cryptographic hash identifying the original batch.
     * @param claimant Address of the downstream reseller/brand submitting the claim.
     * @param quantitySold Quantity of honey being resold in this transaction.
     * @param priceSold Total transaction price for this resale.
     */
    function claimBatch(
        bytes32 batchHash,
        address claimant,
        uint256 quantitySold,
        uint256 priceSold
    ) external {
        require(_batches[batchHash].exists, "Batch does not exist");
        require(claimant != address(0), "Invalid claimant address");
        require(priceSold > 0, "Price sold must be greater than zero");

        Batch storage b = _batches[batchHash];
        b.cumulativeSales += priceSold;
        b.totalQuantitySold += quantitySold;

        _resaleClaims[batchHash].push(ResaleClaim({
            claimant: claimant,
            quantitySold: quantitySold,
            priceSold: priceSold,
            claimedAt: block.timestamp
        }));

        emit BatchClaimed(b.batchId, claimant, quantitySold, priceSold, block.timestamp);
    }

    /**
     * @notice Computes the cumulative royalty owed to the original beekeeper.
     * @dev Calculates royalty based on the configurable ROYALTY_BPS (15%) applied to
     * cumulative downstream sales value.
     *
     * @param batchHash The cryptographic hash identifying the batch.
     * @return amountOwed The cumulative royalty amount owed to the beekeeper.
     */
    function getRoyaltyOwed(bytes32 batchHash) external view returns (uint256 amountOwed) {
        require(_batches[batchHash].exists, "Batch does not exist");
        Batch storage b = _batches[batchHash];
        return (b.cumulativeSales * ROYALTY_BPS) / BPS_DENOMINATOR;
    }

    /**
     * @notice Returns batch details including cumulative sales and producer address.
     * @param batchHash The cryptographic hash identifying the batch.
     */
    function getBatchDetails(bytes32 batchHash)
        external
        view
        returns (
            string memory batchId,
            address anchoredBy,
            uint256 anchoredAt,
            uint256 cumulativeSales,
            uint256 totalQuantitySold,
            uint256 claimCount
        )
    {
        require(_batches[batchHash].exists, "Batch does not exist");
        Batch storage b = _batches[batchHash];
        return (
            b.batchId,
            b.anchoredBy,
            b.anchoredAt,
            b.cumulativeSales,
            b.totalQuantitySold,
            _resaleClaims[batchHash].length
        );
    }

    /**
     * @notice Returns the number of downstream claims recorded for a batch.
     */
    function getClaimCount(bytes32 batchHash) external view returns (uint256) {
        require(_batches[batchHash].exists, "Batch does not exist");
        return _resaleClaims[batchHash].length;
    }

    /**
     * @notice Returns specific downstream claim details by index.
     */
    function getClaim(bytes32 batchHash, uint256 index)
        external
        view
        returns (
            address claimant,
            uint256 quantitySold,
            uint256 priceSold,
            uint256 claimedAt
        )
    {
        require(_batches[batchHash].exists, "Batch does not exist");
        require(index < _resaleClaims[batchHash].length, "Index out of bounds");
        ResaleClaim storage c = _resaleClaims[batchHash][index];
        return (c.claimant, c.quantitySold, c.priceSold, c.claimedAt);
    }
}
