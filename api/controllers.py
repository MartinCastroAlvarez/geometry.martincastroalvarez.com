"""
Controllers: base Controller, ControllerRequest, ControllerResponse, PrivateControllerMixin.

Title
-----
Controllers Module

Context
-------
Controller is the abstract base for all API operations. validate(body)
returns ControllerRequest; execute(validated_input: ControllerRequest)
returns ControllerResponse; handler(body) runs validate then execute.
ControllerRequest and ControllerResponse are base TypedDicts extended by
mutations, queries, validations, and tasks. PrivateControllerMixin
enforces authentication and sets self.user. Used by api.api handler to
dispatch and by api.api (ROUTES) for typing.

Examples:
>>> from controllers import Controller, ControllerRequest, ControllerResponse, PrivateControllerMixin
>>> class MyMutation(PrivateControllerMixin, Mutation): ...
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import TypedDict

from exceptions import UnauthorizedError
from models import User


class ControllerRequest(TypedDict, total=False):
    """Base TypedDict for controller request (validated input). Extended by mutations, queries, validations, tasks."""

    pass


class ControllerResponse(TypedDict, total=False):
    """Base TypedDict for controller response. Extended by mutations, queries, validations, tasks."""

    pass


class Controller(ABC):
    """
    Base controller: validate, execute, handler.
    Subclasses implement validate() and execute(); handler() is unified here.

    For example, to run a mutation:
    >>> handler = JobMutation(user=request.user)
    >>> result = handler.handler(body)
    """

    @abstractmethod
    def validate(self, body: dict[str, Any]) -> ControllerRequest:
        """Validate raw body into typed request. Raises on invalid input."""
        pass

    @abstractmethod
    def execute(self, validated_input: ControllerRequest) -> ControllerResponse:
        """Run the operation on validated input and return response."""
        pass

    def handler(self, body: dict[str, Any]) -> ControllerResponse:
        """
        Validate then execute. Single entry point for API dispatch.

        For example, to handle a POST body:
        >>> response = controller.handler(request_body)
        >>> "id" in response
        True
        """
        validated_input = self.validate(body)
        return self.execute(validated_input)


class PrivateControllerMixin:
    """
    Mixin that requires an authenticated user. Add as first base with
    Mutation, Query, Validation, or Task; pass user= to __init__.

    For example, to create an authenticated mutation:
    >>> class MyMutation(PrivateControllerMixin, Mutation):
    ...     pass
    >>> handler = MyMutation(user=request.user)
    >>> handler.handler(body)
    """

    user: User

    def __init__(self, *, user: User, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.user = user

    def validate(self, body: dict[str, Any]) -> ControllerRequest:
        """Require user to be authenticated before delegating to super validate."""
        if self.user is None or not self.user.is_authenticated():
            raise UnauthorizedError("User must be authenticated")
        return super().validate(body)
