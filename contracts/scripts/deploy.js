const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  console.log("----------------------------------------------------");
  console.log("Deploying HoneyBatchRegistry to network:", hre.network.name);
  console.log("----------------------------------------------------");

  const [deployer] = await hre.ethers.getSigners();
  console.log("Deployer address:", deployer.address);
  const balance = await hre.ethers.provider.getBalance(deployer.address);
  console.log("Deployer balance:", hre.ethers.formatEther(balance), "ETH/MATIC");

  const HoneyBatchRegistry = await hre.ethers.getContractFactory("HoneyBatchRegistry");
  const registry = await HoneyBatchRegistry.deploy();
  await registry.waitForDeployment();

  const contractAddress = await registry.getAddress();
  console.log("\n>>> HoneyBatchRegistry deployed successfully!");
  console.log(">>> Contract Address:", contractAddress);

  if (hre.network.name === "amoy") {
    console.log(`>>> Polygonscan Amoy Explorer: https://amoy.polygonscan.com/address/${contractAddress}`);
  }

  // Save deployment artifact for backend and scripts
  const deploymentInfo = {
    network: hre.network.name,
    chainId: hre.network.config.chainId,
    contractAddress: contractAddress,
    deployer: deployer.address,
    deployedAt: new Date().toISOString(),
    abi: JSON.parse(registry.interface.formatJson()),
  };

  const artifactPath = path.join(__dirname, "..", "deployed_contract.json");
  fs.writeFileSync(artifactPath, JSON.stringify(deploymentInfo, null, 2));
  console.log(`>>> Deployment metadata saved to: ${artifactPath}`);

  // Also write address to .env file in contracts and backend
  const envContractSnippet = `\nHONEY_BATCH_REGISTRY_ADDRESS=${contractAddress}\n`;
  const contractsEnv = path.join(__dirname, "..", ".env");
  fs.appendFileSync(contractsEnv, envContractSnippet);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("Deployment failed:", error);
    process.exit(1);
  });
