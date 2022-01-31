from brownie import network, config, interface
from scripts.get_weth import get_weth
from scripts.helpful_scripts import FORKED_LOCAL_DEVELOPMENT, get_account

from web3 import Web3

VALUE = Web3.toWei(0.1, "ether")


def main():
    account = get_account()
    erc20_token = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in FORKED_LOCAL_DEVELOPMENT:
        get_weth()
    # Depositing WETH into AAVE protocol
    lending_pool = get_lending_pool()
    # Approve sending out ERC20 token
    approve_erc20(VALUE, lending_pool.address, erc20_token, account)
    print("Depositing..")
    tx = lending_pool.deposit(erc20_token, VALUE, account.address, 0, {"from": account})
    tx.wait(1)
    print("Deposited!")
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
    print("Lets borrow!")

    dai_eth_price = get_asset_price(
        config["networks"][network.show_active()]["dai_eth_price_feed"]
    )
    # converting borrowable_eth into borrowable_dai * 95% to keep a positive health factor
    borrowable_dai = (1 / dai_eth_price) * (borrowable_eth * 0.95)
    print(f"We are about to borrow {borrowable_dai} DAI")
    dai_token = config["networks"][network.show_active()]["dai_token"]
    borrow_tx = lending_pool.borrow(
        dai_token,
        Web3.toWei(borrowable_dai, "ether"),
        1,
        0,
        account.address,
        {"from": account},
    )
    borrow_tx.wait(1)
    print("We borrowed some DAI!")
    get_borrowable_data(lending_pool, account)
    repay_all(Web3.toWei(borrowable_dai, "ether"), lending_pool, account)
    print("You just deposited, borrowed and repayed with AAVE, Brownie and Chainlink!")


def repay_all(amount, lending_pool, account):
    approve_erc20(
        amount,
        lending_pool.address,
        config["networks"][network.show_active()]["dai_token"],
        account.address,
    )
    repay_tx = lending_pool.repay(
        config["networks"][network.show_active()]["dai_token"],
        amount,
        1,
        account.address,
        {"from": account},
    )
    repay_tx.wait(1)
    print("Repaid DAI!")


def get_asset_price(asset_price_feed):
    dai_eth_price_feed = interface.AggregatorV3Interface(asset_price_feed)
    latest_price = dai_eth_price_feed.latestRoundData()[1]
    converted_dai_price = Web3.fromWei(latest_price, "ether")
    print(f"The DAI/ETH price feed is {converted_dai_price}")
    return float(converted_dai_price)


def get_borrowable_data(lending_pool, account):
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrows_eth,
        current_liquidation_threshold,
        ltv,
        health_factor,
    ) = lending_pool.getUserAccountData(account.address)
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    available_borrows_eth = Web3.fromWei(available_borrows_eth, "ether")
    print(f"You have {total_collateral_eth} worth of ETH deposited")
    print(f"You have {total_debt_eth} worth of ETH borrowed")
    print(f"You have {available_borrows_eth} ETH left to borrow")
    return (float(available_borrows_eth), float(total_debt_eth))


def approve_erc20(amount, spender, erc20token, account):
    print("Approving ERC20 token...")
    # ABI
    # Address
    erc20_address = interface.IERC20(erc20token)
    tx = erc20_address.approve(spender, amount, {"from": account})
    print("Approved!")
    return tx


def get_lending_pool():
    lending_pool_address_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )

    # Address
    lending_pool_address = lending_pool_address_provider.getLendingPool()
    # ABI
    lending_pool = interface.ILendingPool(lending_pool_address)
    print(lending_pool)
    return lending_pool
