const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("HoneyBatchRegistry", function () {
  let registry;
  let deployer, beekeeper, brand, retailer;
  const sampleBatchId = "BATCH-2026-KVIC-001";
  const sampleHash = ethers.keccak256(ethers.toUtf8Bytes("Sample Canonical Batch Data 2026"));

  beforeEach(async function () {
    [deployer, beekeeper, brand, retailer] = await ethers.getSigners();
    const HoneyBatchRegistry = await ethers.getContractFactory("HoneyBatchRegistry");
    registry = await HoneyBatchRegistry.deploy();
    await registry.waitForDeployment();
  });

  describe("anchorBatch", function () {
    it("should allow a beekeeper to anchor a new batch and emit BatchAnchored", async function () {
      await expect(registry.connect(beekeeper).anchorBatch(sampleHash, sampleBatchId))
        .to.emit(registry, "BatchAnchored")
        .withArgs(sampleBatchId, sampleHash, beekeeper.address, (val) => val > 0);

      const verification = await registry.verifyBatch(sampleBatchId);
      expect(verification[0]).to.equal(sampleHash);
      expect(verification[1]).to.equal(beekeeper.address);
      expect(verification[2]).to.be.gt(0);
    });

    it("should reject anchoring an empty batchId", async function () {
      await expect(
        registry.connect(beekeeper).anchorBatch(sampleHash, "")
      ).to.be.revertedWith("Batch ID cannot be empty");
    });

    it("should reject anchoring a zero batchHash", async function () {
      await expect(
        registry.connect(beekeeper).anchorBatch(ethers.ZeroHash, "BATCH-ZERO")
      ).to.be.revertedWith("Batch hash cannot be zero");
    });

    it("should reject duplicate batchId", async function () {
      await registry.connect(beekeeper).anchorBatch(sampleHash, sampleBatchId);
      const anotherHash = ethers.keccak256(ethers.toUtf8Bytes("Different data"));
      await expect(
        registry.connect(beekeeper).anchorBatch(anotherHash, sampleBatchId)
      ).to.be.revertedWith("Batch ID already exists");
    });

    it("should reject duplicate batchHash with different batchId", async function () {
      await registry.connect(beekeeper).anchorBatch(sampleHash, sampleBatchId);
      await expect(
        registry.connect(beekeeper).anchorBatch(sampleHash, "BATCH-2026-KVIC-002")
      ).to.be.revertedWith("Batch hash already registered");
    });
  });

  describe("verifyBatch", function () {
    it("should revert if querying non-existent batchId", async function () {
      await expect(registry.verifyBatch("NON-EXISTENT")).to.be.revertedWith(
        "Batch ID not found"
      );
    });
  });

  describe("claimBatch and getRoyaltyOwed", function () {
    beforeEach(async function () {
      await registry.connect(beekeeper).anchorBatch(sampleHash, sampleBatchId);
    });

    it("should allow downstream brands to record claims and emit BatchClaimed", async function () {
      const quantity = 50; // kg
      const priceSold = 47500; // INR

      await expect(
        registry.connect(brand).claimBatch(sampleHash, brand.address, quantity, priceSold)
      )
        .to.emit(registry, "BatchClaimed")
        .withArgs(sampleBatchId, brand.address, quantity, priceSold, (val) => val > 0);

      const claimCount = await registry.getClaimCount(sampleHash);
      expect(claimCount).to.equal(1);

      const claim = await registry.getClaim(sampleHash, 0);
      expect(claim[0]).to.equal(brand.address);
      expect(claim[1]).to.equal(quantity);
      expect(claim[2]).to.equal(priceSold);
    });

    it("should compute exact 15% royalty owed across multiple resale stages", async function () {
      // First resale: Processor -> Brand (50kg @ ₹30,000)
      await registry.connect(brand).claimBatch(sampleHash, brand.address, 50, 30000);
      let royalty = await registry.getRoyaltyOwed(sampleHash);
      // 15% of 30,000 = 4,500
      expect(royalty).to.equal(4500);

      // Second resale: Brand -> Premium Retailer (50kg @ ₹47,500)
      await registry.connect(retailer).claimBatch(sampleHash, retailer.address, 50, 47500);
      royalty = await registry.getRoyaltyOwed(sampleHash);
      // Cumulative sales: 30,000 + 47,500 = 77,500
      // 15% of 77,500 = 11,625
      expect(royalty).to.equal(11625);
    });

    it("should reject claim for unanchored batch hash", async function () {
      const fakeHash = ethers.keccak256(ethers.toUtf8Bytes("Fake Hash"));
      await expect(
        registry.connect(brand).claimBatch(fakeHash, brand.address, 10, 5000)
      ).to.be.revertedWith("Batch does not exist");
    });

    it("should reject claim with zero priceSold", async function () {
      await expect(
        registry.connect(brand).claimBatch(sampleHash, brand.address, 10, 0)
      ).to.be.revertedWith("Price sold must be greater than zero");
    });
  });
});
