# Running agents and tests against different networks

Sometimes agents and tests need to be run on specific networks. In the case of Ethereum,
you might want to use developer environments like Hardhat or Ganache as your testbed,
but at some point you will also require running on top of a public testnet like Ropsten or,
ultimately, the main chain.

To switch chains, you will first need to edit your chain configuration, as well as verify that
the relevant addresses that come into play are funded. After that, the `valory/ledger` connection's
configuration must be modified, and the process is slightly different for agents than for tests.

## Ledger configuration for Agents
Look at you agent's `aea-config.yaml` last section. It should look like this:
```
public_id: valory/ledger:0.1.0
type: connection
config:
  ledger_apis:
    ethereum:
      address: ${LEDGER_ADDRESS:str:http://hardhat:8545}
      chain_id: ${LEDGER_CHAIN_ID:int:31337}
```
There, edit the `address` and `chain_id` fields to match your requirements. In this case, we've set
a local Hardhat node as our target chain, with its default id.

## Ledger configuration for contract integration tests
Tests that make calls to a chain usually inherit from `BaseContractTest`, located at
`/tests/test_contracts/base.py`. That class defines the `_setup_class` method that overrides
the `valory/ledger` connection's configuration:
```
new_config = {
    "address": url,
    "chain_id": DEFAULT_CHAIN_ID,
    "denom": DEFAULT_CURRENCY_DENOM,
    "default_gas_price_strategy": "eip1559",
    "gas_price_strategies": {
        "gas_station": DEFAULT_GAS_STATION_STRATEGY,
        "eip1559": DEFAULT_EIP1559_STRATEGY,
    },
}

cls.ledger_api = ledger_apis_registry.make(
    cls.identifier,
    **new_config,
)
```

As before, edit here the `address` and `chain_id` fields. That should suffice for your
test to use the desired network.

## Configuration for end to end tests
End to end agent tests inherit from the `BaseTestEnd2End` in `tests/test_agents.py`. That
class defines an `extra_configs` attribute that is used to set the agent's configuration overrides.
If your tests override that attribute, parameters defined there will be used by the agent.
This does not only apply to `valory/ledger` connection, but to any agent configuration:
```
from tests.test_agents.base import BaseTestEnd2End

class MySuperHelpfulEndToEndTestBase(BaseTestEnd2End):
    """Base class for my super helpful e2e tests."""

    extra_configs = [
        {
            "dotted_path": "vendor.valory.skills.my_super_skill_abci.models.params.args.ipfs_domain_name",
            "value": "/dns/localhost/tcp/5001/http",
        }
    ]
```

All tests that inherit from this test base class will use the new configuration.