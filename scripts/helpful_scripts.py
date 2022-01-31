from brownie import (
    config,
    network,
    accounts,
    Contract,
)

FORKED_LOCAL_DEVELOPMENT = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_DEVELOPMENT = ["development", "ganache-local"]


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_DEVELOPMENT
        or network.show_active() in FORKED_LOCAL_DEVELOPMENT
    ):
        return accounts[0]

    return accounts.add(config["wallets"]["from_key"])
