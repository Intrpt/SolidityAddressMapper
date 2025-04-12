pragma solidity ^0.8.0;

contract InstructionsTest {
    // State variables
    uint256 public counter = 0;
    uint256[8] public myArray;
    mapping(address => uint256) public balances;
    bool public flag = false;

    // Constructor
    constructor() {
        myArray[0] = 10;
        balances[msg.sender] = 100;
    }

    // 1. Arithmetic Operations
    function arithmeticOps(uint256 a, uint256 b) public pure returns (uint256, uint256, uint256, uint256) {
        uint256 add = a + b;
        uint256 sub = a - b;
        uint256 mul = a * b;
        uint256 div = b != 0 ? a / b : 0;
        return (add, sub, mul, div);
    }

    // 2. Bitwise Operations
    function bitwiseOps(uint256 a, uint256 b) public pure returns (uint256, uint256, uint256, uint256, uint256, uint256) {
        uint256 andOp = a & b;
        uint256 orOp = a | b;
        uint256 xorOp = a ^ b;
        uint256 notOp = ~a;
        uint256 shlOp = a << 2;
        uint256 shrOp = a >> 2;
        return (andOp, orOp, xorOp, notOp, shlOp, shrOp);
    }

    // 3. Comparison Operations
    function comparisonOps(uint256 a, uint256 b) public pure returns (bool, bool, bool, bool, bool, bool) {
        bool eq = a == b;
        bool neq = a != b;
        bool gt = a > b;
        bool lt = a < b;
        bool gte = a >= b;
        bool lte = a <= b;
        return (eq, neq, gt, lt, gte, lte);
    }

    // 4. Logical Operations
    function logicalOps(bool a, bool b) public pure returns (bool, bool, bool) {
        bool andOp = a && b;
        bool orOp = a || b;
        bool notOp = !a;
        return (andOp, orOp, notOp);
    }

    // 5. Assignment Operations
    function assignmentOps(uint256 a) public returns (uint256, uint256, uint256, uint256, uint256) {
        uint256 addAssign = counter;
        addAssign += a;
        uint256 subAssign = counter;
        subAssign -= a;
        uint256 mulAssign = counter;
        mulAssign *= a;
        uint256 divAssign = counter;
        divAssign /= (a != 0 ? a : 1);
        uint256 modAssign = counter;
        modAssign %= (a != 0 ? a : 1);
        return (addAssign, subAssign, mulAssign, divAssign, modAssign);
    }

    // 6. Control Structures (if, else, for, while, do-while)
    function controlStructures(uint256 n) public returns (uint256) {
        uint256 sum = 0;
        if (n > 10) {
            sum += 1;
        } else {
            sum -= 1;
        }

        for (uint256 i = 0; i < n; i++) {
            sum += i;
            if (i > 5) break;
        }

        uint256 j = 0;
        while (j < n) {
            sum += j;
            j++;
            if (j > 5) break;
        }

        uint256 k = 0;
        do {
            sum += k;
            k++;
        } while (k < n && k <= 5);

        return sum;
    }

    // 7. Function Calls (internal, external)
    function internalCall(uint256 a) internal pure returns (uint256) {
        return a * a;
    }

    function externalCall(uint256 a) public pure returns (uint256) {
        return internalCall(a);
    }

    // 8. Array Operations
    function arrayOps(uint256 index) public view returns (uint256) {
        require(index < myArray.length);
        return myArray[index];
    }

    function arrayUpdate(uint256 index, uint256 value) public {
        require(index < myArray.length);
        myArray[index] = value;
    }

    // 9. Mapping Operations
    function mappingOps(address addr) public view returns (uint256) {
        return balances[addr];
    }

    function mappingUpdate(address addr, uint256 value) public {
        balances[addr] = value;
    }

    // 10. Assert, Require, Revert
    function assertTest(uint256 a) public view {
        assert(a > 0);
    }

    function requireTest(uint256 a) public pure {
        require(a > 0, "Value must be greater than 0");
    }

    function revertTest(uint256 a) public pure {
        if (a <= 0) {
            revert("Value must be greater than 0");
        }
    }

    // 11. Try-Catch
    function tryCatchTest(uint256 a) public view returns (bool) {
        try this.assertTest(a) {
            return true;
        } catch Error(string memory reason) {
            return false;
        }
    }

    // 12. Modifiers
    modifier onlyNonZero(uint256 a) {
        require(a != 0, "Value cannot be zero");
        _;
    }

    function modifierTest(uint256 a) public onlyNonZero(a) pure returns (uint256) {
        return a * a;
    }

    // 13. Events
    event ValueUpdated(uint256 value);

    function eventTest(uint256 a) public {
        emit ValueUpdated(a);
        counter = a;
    }

    // 14. Fallback and Receive Functions
    fallback() external payable {}

    receive() external payable {}

    // 15. Gas Stipend (2300 gas)
    function gasStipendTest() public returns (bool) {
        (bool sent, ) = msg.sender.call{gas: 2300}("");
        return sent;
    }

    // 16. Type Conversions
    function typeConversionTest(uint256 a) public pure returns (uint128, int256) {
        uint128 uint128Value = uint128(a);
        int256 intValue = int256(a);
        return (uint128Value, intValue);
    }

    // 17. Enums
    enum State { Active, Inactive }
    State public state = State.Active;

    function enumTest() public {
        state = State.Inactive;
    }

    // 18. Structs
    struct User {
        uint256 id;
        string name;
    }

    User public user;

    function structTest() public {
        user = User(1, "John Doe");
    }

    // 19. Delete
    function deleteTest() public {
        delete user;
    }
}