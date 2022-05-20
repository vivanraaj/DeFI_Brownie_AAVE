from brownie import network, config, interface
from scripts.helpful_scripts import get_account
from scripts.helpful_scripts import get_weth
from web3 import Web3

# 0.1
amount = Web3.toWei(0.1, "ether")


def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in ["mainnet-fork"]:
        get_weth()
    # 2 things when work with contract
    # ABI
    # Address
    # put money into aave
    lending_pool = get_lending_pool()
    # print(lending_pool)
    # APPROVE SENDING OUT ERC20 Function
    approve_erc20(amount, lending_pool.address, erc20_address, account)
    # once approve, can use the lending pool deposit function
    print("Depositing....")
    # https://docs.aave.com/developers/v/1.0/developing-on-aave/the-protocol/lendingpool
    tx = lending_pool.deposit(
        erc20_address, amount, account.address, 0, {"from": account}
    )
    tx.wait(1)
    print("Deposited....")
    borrowable_eth, total_debt = get_borrowable_data(
        lending_pool, account
    )  # get user health
    # 0.1 ETH Deposited
    # 0.08
    print("Let's borrow")
    # now we can borrow DAI
    # need dai in terms of ETH
    dai_eth_price = get_asset_price(
        erc20_address=config["networks"][network.show_active()]["dai_eth_price_feed"]
    )  # get price feed from chainlink
    amount_dai_to_borrow = (1 / dai_eth_price) * (
        borrowable_eth * 0.95
    )  # multiply by 0.95 as buffer
    # borrowable_eth -> borrowable_dai * 95%  #
    print(f"We are going to borrow {amount_dai_to_borrow} DAI")
    # NOW WE WILL BORROW
    # SEE AAVE BORROW FUNCTION
    dai_address = config["networks"][network.show_active()]["dai_token"]
    borrow_tx = lending_pool.borrow(
        dai_address,
        Web3.toWei(amount_dai_to_borrow, "ether"),
        1,
        0,
        account.address,
        {"from": account},
    )
    borrow_tx.wait(1)
    print("We borrowed some DAI!")
    get_borrowable_data(lending_pool, account)
    repay_all(amount, lending_pool, account)
    print("You just deposited borrowed and repayed with AAVE, bronie and cahainlink")


def repay_all(amount, lending_pool, account):
    # first need to approve
    approve_erc20(
        Web3.toWei(amount, "ether"),
        lending_pool,
        config["networks"][network.show_active()]["dai_token"],
        account,
    )
    repay_tx = lending_pool.repay(
        config["networks"][network.show_active()]["dai_token"],
        amount,
        1,
        account.address,
        {"from": account},
    )
    repay_tx.wait(1)
    print("Repaid")


def get_asset_price(price_feed_address):
    # ABI
    # ADDRESS
    dai_eth_price_feed = interface.AggregatorV3Interface(price_feed_address)
    latest_price = dai_eth_price_feed.latestRoundData()[
        1
    ]  # this is 2nd answer which is answer
    converted_latest_price = Web3.fromWei(latest_price, "ether")
    print(f"The DAI/ETH price is {converted_latest_price}")
    return float(converted_latest_price)
    # this has 18 decimals in the price feed


def get_borrowable_data(lending_pool, account):
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrow_eth,
        current_liquidation_threshold,
        ltv,
        health_factor,
    ) = lending_pool.getUserAccountData(
        account.address
    )  # this is a view function
    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    print(f"YOu have {total_collateral_eth} worth of ETH Despoited")
    print(f"YOu have {total_debt_eth} worth of ETH borrowed")
    print(f"YOu can borrow {available_borrow_eth} worth of ETH")
    return (float(available_borrow_eth), float(total_debt_eth))


def approve_erc20(amount, spender, erc20_address, account):
    print("Approving ERC20 token...")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("Approved!")
    return tx
    # ABI
    # Address
    # pass


def get_lending_pool():
    # gets the address of the AAVE market
    # ABI
    # we use interfaces to put all the main functions

    # Address
    # get the address from https://docs.aave.com/developers/v/1.0/deployed-contracts/deployed-contract-instances
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    # returns address of leding pool
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    # ABI
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool
