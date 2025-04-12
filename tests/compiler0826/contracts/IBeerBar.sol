// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IBeerBar {

    // ROLES
    // * Only owners can add new owners
    // * Owners can only renounce themselves again
    function isOwner(address account) external view returns (bool);
    function addOwner(address account) external;
    function renounceOwner() external;
    event OwnerAdded(address account);
    event OwnerRemoved(address account);
    // * Barkeepers have to be set by owners
    // * Barkeepers can be revoked by owners
    // * Barkeepers can renounce themselves
    function isBarkeeper(address account) external view returns (bool);
    function addBarkeeper(address account) external;
    function revokeBarkeeper(address account) external;
    function renounceBarkeeper() external;
    event BarkeeperAdded(address account);
    event BarkeeperRemoved(address account);

    // * The bar uses its own tokens as local currency.
    //   Connect the bar contract with the token contract.
    // * This can only be done by owners
    function setBeerTokenContractAddress(address addr) external;
    // * Show which beer is served
    function beerTokenContractAddress() external view returns(address);

    // * The bar has opening hours during which beer can be ordered and served
    // * The bar is opened and closed by barkeepers
    function openBar() external;
    function closeBar() external;
    function barIsOpen() external view returns (bool);
    event BarOpened();
    event BarClosed();

    // * When new beer is delivered, the token contract owner mints new
    //   tokens and transfers them to the bar contract with the string
    //   "supply" in the data field (since this is not a beer order)
    // * The bar contract emits the event BeerSupplied when receiving
    //   beer tokens marked as "supply" (together with beer)
    event BeerSupplied(address indexed from, uint256 amount);

    // * Beer is ordered by transferring beer tokens to the bar contract
    //   with the data field "hex"00000000" (standard transfer);
    //   1 token = 1 beer
    // * Beer can only be ordered while the bar is open
    // * In addition to the internal bookkeeping, the event
    //   BeerOrdered is triggered to signal that there is work
    event BeerOrdered(address indexed customer, uint256 amount);

    // Both, supply and order, have to be implemented in a token fallback function

    // * Beer that has been ordered will be served by barkeepers
    // * Beer can only be served while the bar is open
    // * Served beer has to be burned by the token contract
    function serveBeer(address customer, uint amount) external;

    // * Orders that haven't yet been processed may be canceled by the
    //   customer, who will get back the tokens
    // * This triggers the event BeerCanceled
    // * Orders can be canceled at any time
    function cancelOrder(uint amount) external;
    event BeerCanceled(address indexed customer, uint256 amount);

    // * Get pending orders for a customer
    function pendingBeer(address customer) external view returns (uint256);

    // * Beer price can only be changed by owners when the bar is closed
    function setBeerPrice(uint256 price) external;
    function getBeerPrice() external view returns(uint256);

    // * Customers may buy tokens for Ether
    // * If the supplied Ether is not divisible by the beer price
    //   the rest is kept as a tip. The caller (like the web interface)
    //   can check that the value is a multiple of the beer price.
    function buyToken() external payable;

    // * `amount` (in Wei) of the Ether stored in the contract is transferred to
    //   `receiver`, provided `amount` does not exceed the balance of the contract
    // * Only owners are allowed to do this
    function payout(address payable receiver, uint256 amount) external;

}
