import unittest
import time
from core.state import CognitiveState



class TestCognitiveState(unittest.TestCase):
    def setUp(self):
        self.state = CognitiveState()

    def test_initial_empty_state(self):
        self.assertEqual(self.state._state_data, {})
        self.assertEqual(self.state._history, [])
        self.assertEqual(self.state._listeners, [])

    def test_get_set_value(self):
        self.state.set('foo', 42)
        self.assertEqual(self.state.get('foo'), 42)
        self.assertIsNone(self.state.get('bar'))
        self.assertEqual(self.state.get('bar', 'default'), 'default')

    def test_update_bulk(self):
        self.state.update({'a': 1, 'b': 2})
        self.assertEqual(self.state.get('a'), 1)
        self.assertEqual(self.state.get('b'), 2)

    def test_snapshot_and_rollback(self):
        self.state.set('x', 10)
        snap1 = self.state.snapshot()
        self.assertEqual(snap1, {'x': 10})

        self.state.set('x', 20)
        self.assertEqual(self.state.get('x'), 20)

        self.state.rollback()
        self.assertEqual(self.state.get('x'), 10)

    def test_rollback_no_snapshot_raises(self):
        with self.assertRaises(IndexError):
            self.state.rollback()

    def test_listeners_called_on_set(self):
        called = []

        def listener(state_data):
            called.append(state_data.copy())

        self.state.add_listener(listener)
        self.state.set('key', 'value')
        self.assertTrue(called)
        self.assertEqual(called[-1]['key'], 'value')

    def test_listeners_called_on_update(self):
        called = []

        def listener(state_data):
            called.append(state_data.copy())

        self.state.add_listener(listener)
        self.state.update({'foo': 123, 'bar': 456})
        self.assertTrue(called)
        self.assertEqual(called[-1]['foo'], 123)
        self.assertEqual(called[-1]['bar'], 456)

    def test_add_and_remove_listener(self):
        called = []

        def listener(state_data):
            called.append(state_data.copy())

        self.state.add_listener(listener)
        self.state.set('test', 1)
        self.state.remove_listener(listener)
        self.state.set('test', 2)
        self.assertEqual(len(called), 1)  # listener called only once before removal

    def test_last_updated_changes(self):
        before = self.state.last_updated()
        time.sleep(0.01)
        self.state.set('new', 'val')
        after = self.state.last_updated()
        self.assertGreater(after, before)

    def test_repr_includes_state(self):
        self.state.set('a', 1)
        r = repr(self.state)
        self.assertIn('a', r)
        self.assertIn('1', r)


if __name__ == '__main__':
    unittest.main()
