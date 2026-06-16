require("@nomicfoundation/hardhat-toolbox");

module.exports = {
  solidity: "0.8.24",
  networks: {
    ganache: {
      url: "http://127.0.0.1:7545",
      accounts: ["0x964dc5d990e61e7c21aa6dcb9bb866a9c3734ad416d29c935cb800c22ef6053a"]
    }
  }
};