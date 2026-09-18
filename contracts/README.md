# HoneyChain — Smart Contract Layer (`/contracts`)

## Overview

The `HoneyBatchRegistry.sol` smart contract provides the immutable backbone for the **HoneyChain** platform (SIH 2026 Problem Statement 26021, Ministry of MSME / KVIC).

It addresses the fundamental exploitation of rural beekeepers: while farm-gate procurement rates hover around **₹150–₹320/kg**, retail honey shelves command **₹800–₹1,500/kg**. HoneyChain establishes a permanent on-chain **Producer of Record** and enforces an auditable **15% downstream royalty mechanism**.

---

## Why Only Hashes Are Stored On-Chain (Not Raw Data)

1. **Privacy & Data Protection**: Storing beekeeper PII (phone numbers, Aadhaar/KVIC IDs, home coordinates) directly on a public blockchain violates data privacy regulations and exposes vulnerable rural farmers.
2. **Gas Optimization & Scalability**: Storing high-resolution harvest photos, laboratory spectrometer PDFs, and sensor time-series data on-chain is prohibitively expensive in gas fees. A 32-byte cryptographic hash (`bytes32`) costs less than **0.002 MATIC** to anchor.
3. **Tamper-Proof Integrity**: A deterministic cryptographic hash (Keccak-256) of the canonical batch JSON creates an unforgeable digital fingerprint. If even a single digit in the moisture percentage or beekeeper name is altered off-chain, the computed hash will not match the on-chain hash, immediately failing verification.

---

## Core Smart Contract Functions

| Function | Type | Description |
|---|---|---|
| `anchorBatch(bytes32 batchHash, string batchId)` | Write | Anchors a new harvest batch, binding the beekeeper's wallet as the permanent Producer of Record. Reverts on duplicates. |
| `verifyBatch(string batchId)` | Free View | Publicly accessible lookup returning the anchored cryptographic hash, beekeeper address, and timestamp. Used by consumer QR scans. |
| `claimBatch(bytes32 batchHash, address claimant, uint256 quantitySold, uint256 priceSold)` | Write | Downstream processors/brands record resale quantities and shelf prices, linking directly to the original batch hash. |
| `getRoyaltyOwed(bytes32 batchHash)` | Free View | Computes the cumulative royalty (15% constant) owed back to the beekeeper based on downstream resale gross volume. |

---

## Quick Start & Testing

### 1. Install Dependencies
```bash
npm install
```

### 2. Run Unit Tests
```bash
npx hardhat test
```

### 3. Run Live Simulation Script
Simulates sample batch generation, hashing, anchoring, downstream brand markup, and royalty calculation:
```bash
node scripts/demo_simulation.js
```

### 4. Deploy to Polygon Amoy Testnet
```bash
npx hardhat run scripts/deploy.js --network amoy
```
*(Requires `POLYGON_AMOY_RPC_URL` and `PRIVATE_KEY` in `.env`)*
