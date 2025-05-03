pragma solidity ^0.8.0;
contract ArtithmeticTestContract {
    function arithmeticOps(uint256 a, uint256 b) public pure returns (uint256, uint256, uint256, uint256) {
        uint256 add = a + b;
        uint256 sub = a - b;
        uint256 mul = a * b;
        uint256 div = b != 0 ? a / b : 0;
        return (add, sub, mul, div);
    }
}