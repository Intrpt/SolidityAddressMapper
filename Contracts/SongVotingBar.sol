// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./BeerBar.sol";

contract SongVotingBar is BeerBar {
    event DJAdded(address account);
    event DJRemoved(address account);
    event Song(string title);
    event Vote(string title);

    bytes32 public constant DJ = keccak256("DJ");
    bool public votingStarted;

    struct Voting
    {
        string title;
        uint256 votes;
    }

    Voting[] private votes;


    function isDJ(address account) external view returns (bool) {
        return hasRole(DJ, account);
    }

    function addDJ(address account) external {
        require(hasRole(OWNER, msg.sender), "DJs have to be set by owners");
         _grantRole(DJ, account);
         emit DJAdded(account);
    }

    function revokeDJ(address account) external {
        require(hasRole(OWNER, msg.sender), "DJs can be revoked by owners");
        _revokeRole(DJ, account);
        emit DJRemoved(account);
    }

    function renounceDJ() external {
        require(hasRole(DJ, msg.sender), "DJs can renounce themselves");
        _revokeRole(DJ, msg.sender);
        emit DJRemoved(msg.sender);
    }

    function startVoting() external {
        require(hasRole(DJ, msg.sender), "Only DJ start the voting");
        require(_barIsOpen,"Bar is closed");
        votingStarted = true;
    }

    function stopVoting() external {
        require(hasRole(DJ, msg.sender), "Only DJ start the voting");
        votingStarted = false;
    }

    function isVoting() external view returns (bool) {
        return votingStarted;
    }

    function getVotesCount() external view returns (uint) {
        return votes.length;
    }

    function getVoteTitle(uint index) external view returns (string memory) {
        require(index >= 0 && index < votes.length, "Index out of bounds");
        return votes[index].title;
    }

    function getVoteVotes(uint index) external view returns (uint) {
        require(index >= 0 && index < votes.length, "Index out of bounds");
        return votes[index].votes;
    }

    function playSong() external returns (string memory)  {
        require(hasRole(DJ, msg.sender), "Only DJ can play a song");
        uint highestVotes = 0;
        uint pointer;
        for(uint i = 0; i < votes.length; i++) {
            if(votes[i].votes > highestVotes) {
                highestVotes = votes[i].votes;
                pointer = i;
            }
        }
        if(highestVotes > 0) {
            string memory title = votes[pointer].title;
            votes[pointer].votes = 0;
            emit Song(title);
            return title;
        }
        emit Song("");
        return "";
    }

    function vote(string memory title) external payable {
        require(votingStarted,"Voting is closed");
        require(_beerPrice > 0, " Beer price has not been set");
        require(beerTokenContract.transfer(msg.sender, (msg.value-(msg.value % _beerPrice))/_beerPrice),"Failed to transfer");
        bytes32 hash = keccak256(abi.encodePacked(title));
        emit Vote(title);
        for(uint i = 0; i < votes.length; i++) {
            if(keccak256(abi.encodePacked(votes[i].title)) == hash) {
                votes[i].votes += 1;
                return;
            }
        }
        Voting memory voting;
        voting.title = title;
        voting.votes = 1;
        votes.push(voting);

    }



    function closeBar() external override{
        require(hasRole(BARKEEPER, msg.sender), " The bar is opened and closed by barkeepers");
        _barIsOpen = false;
        votingStarted = false;
        emit BarClosed();
    }

}
