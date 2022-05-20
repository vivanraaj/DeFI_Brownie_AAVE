// SPDX-License-Identifier: MIT
pragma solidity 0.6.6;

interface ILendingPoolAddressProvider {
    // get the line below from:
    // https://github.com/aave/protocol-v2/blob/master/contracts/interfaces/ILendingPoolAddressesProvider.sol
    function getLendingPool() external view returns (address);
}
