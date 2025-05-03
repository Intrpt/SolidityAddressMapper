// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./IBeerToken.sol";
import "./Address.sol";
import "./IERC223Recipient.sol";

contract BeerToken is IBeerToken {

    address private owner;
    uint public total;
    mapping(address => uint) public tokens;

    constructor() {
      owner = msg.sender;
    }

    // * Default attributes of your token
    function name() external view returns (string memory) {
      return "Corns";
    }

    function symbol() external view returns (string memory) {
      return "Corns";
    }

    // * Our BeerToken is not divisible
    function decimals() external view returns (uint8) {
      return 0;
    }

    // * Show the total supply of tokens
    function totalSupply() external view returns (uint256) {
      return total;
    }

    // * Show the token balance of the address
    function balanceOf(address who) external view returns (uint256) {
      return tokens[who];
    }

    // * Basic functionality for transferring tokens to user.
    //   The token contract keeps track of the token balances.
    // * Token must not be lost! Make sure they can only be transferred to addresses,
    //   who also support the receiving of tokens.
    function transfer(address to, uint256 value) external returns (bool success) {
      require(tokens[msg.sender] >= value);
      bytes memory _empty = hex"00000000";
      tokens[msg.sender] = tokens[msg.sender] - value;
      tokens[to] = tokens[to] + value;
      if(Address.isContract(to)) {
         IERC223Recipient(to).tokenReceived(msg.sender, value, _empty);
      }
      emit Transfer(msg.sender, to, value);
      //emit TransferData(_empty);
      return true;
    }

    function transfer(address to, uint256 value, bytes calldata data) external returns (bool success) {
      require(tokens[msg.sender] >= value);
      tokens[msg.sender] = tokens[msg.sender] - value;
      tokens[to] = tokens[to] + value;
      if(Address.isContract(to)) {
         IERC223Recipient(to).tokenReceived(msg.sender, value, data);
      }
      emit Transfer(msg.sender, to, value);
      //emit TransferData(_data);
      return true;
    }

    // * Tokens can be minted by the owner of the token contract
    function mint(address account, uint256 value) external returns (bool success) {
      require(owner == msg.sender,"Only owner can mint");
      tokens[account] += value;
      total += value;
      emit Transfer(msg.sender, account, value);
      return true;
    }

    // * Tokens can be burned and therefore "destroyed"
    function burn(uint256 value) external {
      require(tokens[msg.sender] >= value);
      tokens[msg.sender] -= value;
      total -= value;
    }

}
