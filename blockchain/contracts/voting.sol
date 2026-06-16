// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Voting {
    bytes32[] public voteHashes;

    function storeVote(bytes32 _hash) public {
        voteHashes.push(_hash);
    }

    function getCount() public view returns (uint256) {
        return voteHashes.length;
    }

    function getVoteHash(uint256 index) public view returns (bytes32) {
        require(index < voteHashes.length, "Invalid index");
        return voteHashes[index];
    }
}