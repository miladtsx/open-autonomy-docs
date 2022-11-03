# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2022 Valory AG
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

"""Tests for abstract_round_abci/test_tools/base.py"""

from enum import Enum
from pathlib import Path
from typing import Any, Dict, Type, cast

import pytest
from aea.helpers.base import cd
from aea.mail.base import Envelope
from aea.test_tools.utils import copy_class

from packages.valory.connections.ledger.connection import (
    PUBLIC_ID as LEDGER_CONNECTION_PUBLIC_ID,
)
from packages.valory.protocols.contract_api.message import ContractApiMessage
from packages.valory.protocols.ledger_api.message import LedgerApiMessage
from packages.valory.skills.abstract_round_abci.base import AbciAppDB, _MetaPayload
from packages.valory.skills.abstract_round_abci.behaviours import BaseBehaviour
from packages.valory.skills.abstract_round_abci.test_tools.base import (
    FSMBehaviourBaseCase,
)
from packages.valory.skills.abstract_round_abci.tests.data.dummy_abci import (
    PATH_TO_SKILL,
    PUBLIC_ID,
)
from packages.valory.skills.abstract_round_abci.tests.data.dummy_abci.behaviours import (
    DummyRoundBehaviour,
)
from packages.valory.skills.abstract_round_abci.tests.data.dummy_abci.rounds import (
    Event,
    SynchronizedData,
)


participants = frozenset("abcd")


class TestFSMBehaviourBaseCaseSetup:
    """test TestFSMBehaviourBaseCaseSetup setup"""

    test_cls = Type[FSMBehaviourBaseCase]

    @classmethod
    def setup_class(cls) -> None:
        """Setup class"""
        cls.old_value = _MetaPayload.transaction_type_to_payload_cls.copy()  # type: ignore
        _MetaPayload.transaction_type_to_payload_cls.clear()

    @classmethod
    def teardown_class(cls) -> None:
        """Teardown class"""
        _MetaPayload.transaction_type_to_payload_cls = cls.old_value  # type: ignore

    def setup(self) -> None:
        """Setup test"""

        # must `copy` the class to avoid test interference
        self.test_cls = cast(
            Type[FSMBehaviourBaseCase], copy_class(FSMBehaviourBaseCase)
        )

    def setup_test_cls(self, **kwargs) -> FSMBehaviourBaseCase:
        """Helper method to setup test to be tested"""

        with cd(self.test_cls.path_to_skill):
            self.test_cls.setup_class(**kwargs)

        test_instance = self.test_cls()  # type: ignore
        test_instance.setup()
        return test_instance

    def set_path_to_skill(self, path_to_skill: Path = PATH_TO_SKILL) -> None:
        """Set path_to_skill"""
        self.test_cls.path_to_skill = path_to_skill

    @pytest.mark.parametrize("kwargs", [{}, {"param_overrides": {"new_p": None}}])
    def test_setup(self, kwargs: Dict[str, Dict[str, Any]]) -> None:
        """Test setup"""

        self.set_path_to_skill()
        test_instance = self.setup_test_cls(**kwargs)
        assert test_instance
        assert hasattr(test_instance.behaviour.context.params, "new_p") == bool(kwargs)

    @pytest.mark.parametrize("behaviour", DummyRoundBehaviour.behaviours)
    def test_fast_forward_to_behaviour(self, behaviour: BaseBehaviour) -> None:
        """Test fast_forward_to_behaviour"""
        self.set_path_to_skill()
        test_instance = self.setup_test_cls()

        round_behaviour = test_instance._skill.skill_context.behaviours.main
        behaviour_id = behaviour.behaviour_id
        synchronized_data = SynchronizedData(
            AbciAppDB(setup_data=dict(participants=[participants]))
        )

        test_instance.fast_forward_to_behaviour(
            behaviour=round_behaviour,
            behaviour_id=behaviour_id,
            synchronized_data=synchronized_data,
        )

    @pytest.mark.parametrize("event", Event)
    @pytest.mark.parametrize("set_none", [False, True])
    def test_end_round(self, event: Type[Enum], set_none: bool) -> None:
        """Test end_round"""

        self.set_path_to_skill()
        test_instance = self.setup_test_cls()
        current_behaviour = test_instance.behaviour.current_behaviour
        abci_app = current_behaviour.context.state.round_sequence.abci_app
        if set_none:
            test_instance.behaviour.current_behaviour = None
        assert abci_app.current_round_height == 0
        test_instance.end_round(event)
        assert abci_app.current_round_height == 1 - int(set_none)

    def test_mock_ledger_api_request(self) -> None:
        """Test mock_ledger_api_request"""

        self.set_path_to_skill()
        test_instance = self.setup_test_cls()

        request_kwargs = dict(performative=LedgerApiMessage.Performative.GET_BALANCE)
        response_kwargs = dict(performative=LedgerApiMessage.Performative.BALANCE)
        with pytest.raises(
            AssertionError,
            match="Invalid number of messages in outbox. Expected 1. Found 0.",
        ):
            test_instance.mock_ledger_api_request(request_kwargs, response_kwargs)

        message = LedgerApiMessage(**request_kwargs, dialogue_reference=("a", "b"))
        envelope = Envelope(
            to=str(LEDGER_CONNECTION_PUBLIC_ID),
            sender=str(PUBLIC_ID),
            protocol_specification_id=LedgerApiMessage.protocol_specification_id,
            message=message,
        )
        test_instance._multiplexer.out_queue.put_nowait(envelope)
        test_instance.mock_ledger_api_request(request_kwargs, response_kwargs)

    def test_mock_contract_api_request(self) -> None:
        """Test mock_contract_api_request"""

        self.set_path_to_skill()
        test_instance = self.setup_test_cls()

        contract_id = "dummy_contract"
        request_kwargs = dict(performative=ContractApiMessage.Performative.GET_STATE)
        response_kwargs = dict(performative=ContractApiMessage.Performative.STATE)
        with pytest.raises(
            AssertionError,
            match="Invalid number of messages in outbox. Expected 1. Found 0.",
        ):
            test_instance.mock_contract_api_request(
                contract_id, request_kwargs, response_kwargs
            )

        message = ContractApiMessage(
            **request_kwargs,
            dialogue_reference=("a", "b"),
            ledger_id="ethereum",
            contract_id=contract_id
        )
        envelope = Envelope(
            to=str(LEDGER_CONNECTION_PUBLIC_ID),
            sender=str(PUBLIC_ID),
            protocol_specification_id=ContractApiMessage.protocol_specification_id,
            message=message,
        )
        test_instance._multiplexer.out_queue.put_nowait(envelope)
        test_instance.mock_contract_api_request(
            contract_id, request_kwargs, response_kwargs
        )
