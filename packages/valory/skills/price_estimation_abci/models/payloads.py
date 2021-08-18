# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2021 Valory AG
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

"""This module contains the transaction payloads for the price_estimation app."""
from abc import ABC
from enum import Enum
from typing import Dict

from packages.valory.skills.abstract_round_abci.base_models import BaseTxPayload


class TransactionType(Enum):
    """Enumeration of transaction types."""

    REGISTRATION = "registration"
    OBSERVATION = "observation"
    ESTIMATE = "estimate"

    def __str__(self) -> str:
        """Get the string value of the transaction type."""
        return self.value


class BasePriceEstimationPayload(BaseTxPayload, ABC):
    """Base class for the price estimation demo."""


class RegistrationPayload(BasePriceEstimationPayload):
    """Represent a transaction payload of type 'registration'."""

    transaction_type = TransactionType.REGISTRATION


class ObservationPayload(BasePriceEstimationPayload):
    """Represent a transaction payload of type 'observation'."""

    transaction_type = TransactionType.OBSERVATION

    def __init__(self, sender: str, observation: float) -> None:
        """Initialize an 'observation' transaction payload.

        :param sender: the sender (Ethereum) address
        :param observation: the observation
        """
        super().__init__(sender)
        self._observation = observation

    @property
    def observation(self) -> float:
        """Get the observation."""
        return self._observation

    @property
    def data(self) -> Dict:
        """Get the data."""
        return dict(observation=self.observation)


class EstimatePayload(BasePriceEstimationPayload):
    """Represent a transaction payload of type 'estimate'."""

    transaction_type = TransactionType.ESTIMATE

    def __init__(self, sender: str, estimate: float) -> None:
        """Initialize an 'estimate' transaction payload.

        :param sender: the sender (Ethereum) address
        :param estimate: the estimate
        """
        super().__init__(sender)
        self._estimate = estimate

    @property
    def estimate(self) -> float:
        """Get the estimate."""
        return self._estimate

    @property
    def data(self) -> Dict:
        """Get the data."""
        return dict(estimate=self.estimate)