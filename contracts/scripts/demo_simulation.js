const hre = require("hardhat");
const { ethers } = require("hardhat");

async function main() {
  console.log("\n============================================================");
  console.log(" HONEYCHAIN (SIH 2026 PS 26021) — SMART CONTRACT SIMULATION");
  console.log("============================================================\n");

  // 1. Prepare sample batch JSON data
  const sampleBatch = {
    batchId: "BATCH-2026-KVIC-001",
    beekeeper: {
      id: "BK-IN-BR-0842",
      name: "Rameshwar Patel",
      cooperative: "Muzaffarpur Honey Producers Sahakari Samiti",
      phone: "+91 98765 43210",
      walletAddress: "0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
    },
    harvest: {
      hiveId: "HIVE-MZP-04",
      harvestDate: "2026-03-15T09:30:00Z",
      location: {
        latitude: 26.1209,
        longitude: 85.3647,
        district: "Muzaffarpur",
        state: "Bihar",
        country: "India",
      },
      floralSource: "Litchi Blossom (Unifloral)",
      quantityKg: 50.0,
      farmGatePricePerKgINR: 320, // Initial farm-gate procurement price
    },
    labTest: {
      laboratory: "KVIC Central Honey Testing Laboratory, Pune",
      certificateNumber: "KVIC-CHTL-2026-8812",
      testedAt: "2026-03-18T14:15:00Z",
      moisturePercentage: 17.4,   // FSSAI limit < 20%
      purityScore: 99.4,
      hmfMgPerKg: 14.2,           // Freshness indicator
      c4SugarAdulteration: "Negative (0.0%)",
      status: "VERIFIED_AUTHENTIC",
    },
  };

  console.log("[1] Sample Harvest Batch JSON Prepared:");
  console.log(`    - Batch ID: ${sampleBatch.batchId}`);
  console.log(`    - Beekeeper: ${sampleBatch.beekeeper.name} (${sampleBatch.beekeeper.cooperative})`);
  console.log(`    - Floral Origin: ${sampleBatch.harvest.floralSource}`);
  console.log(`    - Harvest Quantity: ${sampleBatch.harvest.quantityKg} kg @ INR ${sampleBatch.harvest.farmGatePricePerKgINR}/kg`);
  console.log(`    - Lab Purity: ${sampleBatch.labTest.purityScore}% (Moisture: ${sampleBatch.labTest.moisturePercentage}%, C4 Adulteration: ${sampleBatch.labTest.c4SugarAdulteration})`);

  // 2. Compute deterministic keccak256 hash of canonical JSON string
  const canonicalString = JSON.stringify(sampleBatch, Object.keys(sampleBatch).sort());
  const batchHash = ethers.keccak256(ethers.toUtf8Bytes(canonicalString));
  console.log(`\n[2] Computed Deterministic Keccak-256 Hash:`);
  console.log(`    ${batchHash}`);

  // 3. Deploy or connect to HoneyBatchRegistry contract
  const [deployer, beekeeper, resellerBrand] = await ethers.getSigners();
  console.log(`\n[3] Interacting Wallets:`);
  console.log(`    - Beekeeper Wallet: ${beekeeper ? beekeeper.address : deployer.address}`);
  console.log(`    - Downstream Reseller Wallet: ${resellerBrand ? resellerBrand.address : deployer.address}`);

  const HoneyBatchRegistry = await ethers.getContractFactory("HoneyBatchRegistry");
  const registry = await HoneyBatchRegistry.deploy();
  await registry.waitForDeployment();
  const contractAddress = await registry.getAddress();
  console.log(`    - Contract Deployed at: ${contractAddress}`);

  // 4. Anchor batch on-chain as Beekeeper
  console.log(`\n[4] Anchoring Batch on Blockchain (anchorBatch)...`);
  const beekeeperSigner = beekeeper || deployer;
  const anchorTx = await registry.connect(beekeeperSigner).anchorBatch(batchHash, sampleBatch.batchId);
  const anchorReceipt = await anchorTx.wait();
  console.log(`    >>> Transaction Hash: ${anchorTx.hash}`);
  console.log(`    >>> Gas Used: ${anchorReceipt.gasUsed.toString()}`);
  console.log(`    >>> Polygonscan Amoy Explorer: https://amoy.polygonscan.com/tx/${anchorTx.hash}`);

  // 5. Verify batch on-chain (free public view call)
  console.log(`\n[5] Calling verifyBatch("${sampleBatch.batchId}")...`);
  const verification = await registry.verifyBatch(sampleBatch.batchId);
  console.log(`    >>> Verified Hash:     ${verification[0]}`);
  console.log(`    >>> Anchored By:       ${verification[1]}`);
  console.log(`    >>> Timestamp:         ${new Date(Number(verification[2]) * 1000).toUTCString()}`);
  console.log(`    >>> Matches Local:     ${verification[0] === batchHash ? "YES (100% Cryptographic Match)" : "MISMATCH"}`);

  // 6. Downstream Brand Claims Batch at Markup Price
  // Retail Shelf Price: ₹950/kg for 50 kg = ₹47,500
  const retailQuantity = 50; // kg
  const retailPriceINR = 47500; // total retail resale value
  console.log(`\n[6] Simulating Downstream Resale Claim (claimBatch)...`);
  console.log(`    - Reseller: "Dabur / Organic India Premium Honey Ltd."`);
  console.log(`    - Resale Volume: ${retailQuantity} kg`);
  console.log(`    - Retail Shelf Price: INR 950/kg (Total: INR ${retailPriceINR})`);
  console.log(`    - Farm-Gate Value Gap: INR 950 vs INR 320 (+196% downstream markup)`);

  const resellerSigner = resellerBrand || deployer;
  const claimTx = await registry.connect(resellerSigner).claimBatch(
    batchHash,
    resellerSigner.address,
    retailQuantity,
    retailPriceINR
  );
  await claimTx.wait();
  console.log(`    >>> Claim Transaction Hash: ${claimTx.hash}`);
  console.log(`    >>> Polygonscan Amoy Explorer: https://amoy.polygonscan.com/tx/${claimTx.hash}`);

  // 7. Calculate and Query On-Chain Royalty Owed to Beekeeper
  console.log(`\n[7] Querying getRoyaltyOwed(batchHash)...`);
  const royaltyOwed = await registry.getRoyaltyOwed(batchHash);
  const royaltyBps = await registry.ROYALTY_BPS();
  console.log(`    >>> Fixed Royalty Rate: ${Number(royaltyBps) / 100}% of gross resale`);
  console.log(`    >>> Cumulative Downstream Resale: INR ${retailPriceINR}`);
  console.log(`    >>> TOTAL ROYALTY OWED TO BEEKEEPER: INR ${royaltyOwed.toString()} (15% of INR 47,500)`);
  console.log(`    >>> Direct Farm-Gate Procurement:  INR ${sampleBatch.harvest.quantityKg * sampleBatch.harvest.farmGatePricePerKgINR}`);
  console.log(`    >>> Combined Beekeeper Earnings:   INR ${sampleBatch.harvest.quantityKg * sampleBatch.harvest.farmGatePricePerKgINR + Number(royaltyOwed)} (+44.5% direct income boost!)`);

  console.log("\n============================================================");
  console.log(" SIMULATION COMPLETE — BLOCKCHAIN ROYALTY LOOP PROVEN");
  console.log("============================================================\n");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("Simulation failed:", error);
    process.exit(1);
  });
