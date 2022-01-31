from scripts.helpful_scripts import get_account
from brownie import interface, config, network
from web3 import Web3

value = Web3.toWei(0.1, "ether")


def main():
    get_weth()


def get_weth():
    """
    Minthing WETH by depositing ETH
    """
    account = get_account()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    tx = weth.deposit({"from": account, "value": value})
    tx.wait(1)
    print("Received 0.1 WETH")
    return tx
