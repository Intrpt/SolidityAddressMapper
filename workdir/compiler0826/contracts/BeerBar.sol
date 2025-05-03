// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./IBeerBar.sol";
import "./BeerToken.sol";
import "./IERC223Recipient.sol";

import "@openzeppelin/contracts/access/AccessControl.sol";


//contract BeerBar is IBeerBar, <Token-Recipient>
contract BeerBar is IBeerBar, AccessControl {
    BeerToken public beerTokenContract;
    bytes32 public constant OWNER = keccak256("OWNER");
    bytes32 public constant BARKEEPER = keccak256("BARKEEPER");
    bool public _barIsOpen;
    uint public _beerPrice;

    mapping(address => uint) orders;


    constructor () {
        _grantRole(OWNER, msg.sender);
        _grantRole(0x0000000000000000000000000000000000000000000000000000000000000000, msg.sender);
    }

    // ROLES
    // * Only owners can add new owners
    // * Owners can only renounce themselves again
    function isOwner(address account) external view returns (bool) {
        return hasRole(OWNER, account);
    }

    function addOwner(address account) external {
        require(hasRole(OWNER, msg.sender), "Only owners can add new owners");
        _grantRole(OWNER, account);
        emit OwnerAdded(account);
    }

    function renounceOwner() external {
        require(hasRole(OWNER, msg.sender), "Owners can only renounce themselves again");
        _revokeRole(OWNER, msg.sender);
        emit OwnerRemoved(msg.sender);
    }

    // * Barkeepers have to be set by owners
    // * Barkeepers can be revoked by owners
    // * Barkeepers can renounce themselves
    function isBarkeeper(address account) external view returns (bool) {
        return hasRole(BARKEEPER, account);
    }

    function addBarkeeper(address account) external {
        require(hasRole(OWNER, msg.sender), "Barkeepers have to be set by owners");
         _grantRole(BARKEEPER, account);
         emit BarkeeperAdded(account);
    }

    function revokeBarkeeper(address account) external {
        require(hasRole(OWNER, msg.sender), "Barkeepers can be revoked by owners");
        _revokeRole(BARKEEPER, msg.sender);
        emit BarkeeperRemoved(account);
    }

    function renounceBarkeeper() external {
        require(hasRole(BARKEEPER, msg.sender), "Barkeepers can renounce themselves");
        _revokeRole(BARKEEPER, msg.sender);
        emit BarkeeperRemoved(msg.sender);
    }

    // * The bar uses its own tokens as local currency.
    //   Connect the bar contract with the token contract.
    // * This can only be done by owners
    function setBeerTokenContractAddress(address addr) external {
        require(hasRole(OWNER, msg.sender), "This can only be done by owners");
        beerTokenContract = BeerToken(addr);
    }
    // * Show which beer is served
    function beerTokenContractAddress() external view returns(address) {
        return address(beerTokenContract);
    }

    // * The bar has opening hours during which beer can be ordered and served
    // * The bar is opened and closed by barkeepers
    function openBar() external {
        require(hasRole(BARKEEPER, msg.sender), " The bar is opened and closed by barkeepers");
        _barIsOpen = true;
        emit BarOpened();
    }

    function closeBar() external virtual {
        require(hasRole(BARKEEPER, msg.sender), " The bar is opened and closed by barkeepers");
        _barIsOpen = false;
        emit BarClosed();
    }

    function barIsOpen() external view returns (bool) {
        return _barIsOpen;
    }



    // Both, supply and order, have to be implemented in a token fallback function
    function tokenReceived(address _from, uint _value, bytes memory _data) public virtual {
        require(msg.sender == address(beerTokenContract),"Wrong token");
        if(keccak256(_data) == hex"b308cfbb7d2d38db3a215f9728501ac69445a6afbee328cdeae4e23db54b850a") {
            require(hasRole(OWNER, tx.origin) ,"Only the token owner can supply");
            emit BeerSupplied(_from, _value);
        } else if(keccak256(_data) == hex"e8e77626586f73b955364c7b4bbf0bb7f7685ebd40e852b164633a4acbd3244c") {
            require(!hasRole(BARKEEPER, msg.sender) && !hasRole(OWNER, msg.sender), "Only customers can order");
            require(_barIsOpen, "Bar is closed");
            orders[_from] += _value;
            emit BeerOrdered(_from, _value);
        }
    }

    // * Beer that has been ordered will be served by barkeepers
    // * Beer can only be served while the bar is open
    // * Served beer has to be burned by the token contract
    function serveBeer(address customer, uint amount) external {
        require(_barIsOpen, " Beer can only be served while the bar is open");
        require(hasRole(BARKEEPER, msg.sender), " Only barkeepers can serve beer");
        require(orders[customer] >= amount, " The customer did not order that much!");
        orders[customer] -= amount;
        beerTokenContract.burn(amount);
    }

    // * Orders that haven't yet been processed may be canceled by the
    //   customer, who will get back the tokens
    // * This triggers the event BeerCanceled
    // * Orders can be canceled at any time
    function cancelOrder(uint amount) external {
        require(orders[msg.sender] >= amount);
        require(beerTokenContract.transfer(msg.sender, amount),"Failed to transfer tokens");
        orders[msg.sender] -= amount;
        emit BeerCanceled(msg.sender, amount);

    }


    // * Get pending orders for a customer
    function pendingBeer(address customer) external view returns (uint256) {
        return orders[customer];
    }

    // * Beer price can only be changed by owners when the bar is closed
    function setBeerPrice(uint256 price) external {
        require(!_barIsOpen, " Beer price can only be changed when the bar is closed");
        require(hasRole(OWNER, msg.sender), " Beer price can only be changed by owners ");
        _beerPrice = price;
    }

    function getBeerPrice() external view returns(uint256) {
        return _beerPrice;
    }

    // * Customers may buy tokens for Ether
    // * If the supplied Ether is not divisible by the beer price
    //   the rest is kept as a tip. The caller (like the web interface)
    //   can check that the value is a multiple of the beer price.
    function buyToken() external payable {
        require(_beerPrice > 0, " Beer price has not been set");
        require(beerTokenContract.transfer(msg.sender, (msg.value-(msg.value % _beerPrice))/_beerPrice),"Failed to transfer");
        //require(beerTokenContract.mint(msg.sender, (msg.value-(msg.value % _beerPrice))/_beerPrice),"Failed to mint");
    }

    // * `amount` (in Wei) of the Ether stored in the contract is transferred to
    //   `receiver`, provided `amount` does not exceed the balance of the contract
    // * Only owners are allowed to do this
    function payout(address payable receiver, uint256 amount) external {
        require(hasRole(OWNER, msg.sender), "  Only owners are allowed to do this");
        (bool success, ) = receiver.call{value: amount}("");
        require(success, "Failed to send Ether");
    }


}
