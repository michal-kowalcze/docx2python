"""Test docx2python.table_object

:author: Shay Hill
:created: 6/26/2019

"""

# pyright: reportPrivateUsage=false

import pytest

from docx2python.depth_collector import CaretDepthError, DepthCollector


class TestDepthCollector:
    """Test tables_object.DepthCollector"""

    def test_init(self) -> None:
        """Init containers"""
        inst = DepthCollector()
        assert inst._par_depth == 4
        assert inst._rightmost_branches == [[]]

    def test_last_caret(self) -> None:
        """Add empty list to caret[-1]. Append pointer to new list to caret."""
        inst = DepthCollector()
        inst._drop_caret()
        assert inst._rightmost_branches == [[[]], []]
        assert inst._rightmost_branches[-1] is inst._rightmost_branches[-2][-1]

    def test_caret_will_not_drop_past_par_depth(self) -> None:
        """Raise error before dropping caret past item_depth"""
        inst = DepthCollector()  # at depth 1
        inst._drop_caret()  # at depth 2
        inst._drop_caret()  # at depth 3
        inst._drop_caret()  # at depth 4 (_par_depth)
        with pytest.raises(CaretDepthError):
            inst._drop_caret()

    def test_raise_caret(self) -> None:
        """Reduce caret list by one."""
        inst = DepthCollector()  # caret = [[]]
        inst._drop_caret()
        assert inst._rightmost_branches == [[[]], []]
        inst._raise_caret()
        assert inst._rightmost_branches == [[[]]]

    def test_caret_will_not_raise_past_root(self) -> None:
        """Raise error before raising caret to depth 0."""
        inst = DepthCollector()  # caret = [[]]
        with pytest.raises(CaretDepthError):
            inst._raise_caret()

    def test_set_caret(self) -> None:
        """Open or close branches to prepare for next branch or item."""
        inst = DepthCollector()
        inst.set_caret(3)
        assert inst._rightmost_branches == [[[[]]], [[]], []]
        inst.set_caret(2)
        assert inst._rightmost_branches == [[[[]]], [[]]]
        inst.set_caret(1)
        assert inst._rightmost_branches == [[[[]]]]
