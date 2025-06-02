"""
state.py

Module managing the cognitive state of the system.
Holds the current context, environmental data, and internal variables
that define the active cognitive landscape for goal evaluation and arbitration.
"""

from typing import Dict, Any, Callable, List
import copy
import time


class CognitiveState:
    """
    Represents the current cognitive state/context.
    Stores variables and data accessible by other components.
    Supports state snapshots and event listeners.
    """

    def __init__(self):
        # Core storage of state variables
        self._state_data: Dict[str, Any] = {}

        # History snapshots of state for rollback or analysis
        self._history: List[Dict[str, Any]] = []

        # Event listeners to trigger callbacks on state change
        self._listeners: List[Callable[[Dict[str, Any]], None]] = []

        # Timestamp of last update
        self._last_updated: float = time.time()

    def get(self, key: str, default=None):
        """Retrieve a value from the state."""
        return self._state_data.get(key, default)

    def set(self, key: str, value: Any):
        """Set or update a value in the state and notify listeners."""
        self._state_data[key] = value
        self._last_updated = time.time()
        self._notify_listeners()

    def update(self, data: Dict[str, Any]):
        """Bulk update multiple state entries and notify listeners."""
        self._state_data.update(data)
        self._last_updated = time.time()
        self._notify_listeners()

    def snapshot(self):
        """Take a snapshot of the current state and save to history."""
        snap = copy.deepcopy(self._state_data)
        self._history.append(snap)
        return snap

    def rollback(self, index: int = -1):
        """Rollback to a previous snapshot by index (default latest)."""
        if not self._history:
            raise IndexError("No snapshots available for rollback.")
        snap = self._history[index]
        self._state_data = copy.deepcopy(snap)
        self._last_updated = time.time()
        self._notify_listeners()

    def add_listener(self, callback: Callable[[Dict[str, Any]], None]):
        """Register a callback to be called on state change."""
        if callback not in self._listeners:
            self._listeners.append(callback)

    def remove_listener(self, callback: Callable[[Dict[str, Any]], None]):
        """Unregister a previously registered callback."""
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify_listeners(self):
        """Invoke all registered listeners with the current state data."""
        for callback in self._listeners:
            callback(self._state_data)

    def last_updated(self):
        """Return timestamp of the last state update."""
        return self._last_updated

    def __repr__(self):
        return f"CognitiveState(state_data={self._state_data}, last_updated={self._last_updated})"
