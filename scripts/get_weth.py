from scripts.helpful_scripts import get_account
from brownie import interface, config, network


def main():
    get_weth()


def get_weth():
    """
    Mints WETH by depositing ETH.
    """
    # ABI
    # now that interface, can compile down to abi

    # Address
    account = get_account()
    weth = interface.Iweth(config["networks"][network.show_active()]["weth_token"])
    # now deposit ETH and get WETH
    tx = weth.deposit(
        {"from": account, "value": 0.1 * 10 ** 18}
    )  # so deposit 1 eth and get 0.1Weth in return?
    tx.wait(1)
    print("Received 0.1 WETH")
    return tx
