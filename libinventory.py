"""Lib inventory

This module just as its name; implements Inventory system.
However, you might see somewhat different implementations.
This module adapts typical staticallt allocated file system.

For extending the size of an Inventory, you can use inv.extend() function.

Note: Inventory class is careful to its size; It'll scream at you when you are trying to append a new data on fully allocated Inventory."""

from __future__ import annotations

__all__ = ['SameIdentifierException',
           'FixedSizeArray', 'LinkedFSA', 'Inventory', 'null', 'fsa_null']

from typing import Any, List, Literal, Union
import warnings
from libshared import ConstCreator, PUID

null = ConstCreator.define('null', None)
fsa_null = ConstCreator.define('<block not-found>', null)


class SameIdentifierException(Exception):
    """The given argument is the same object as saved/operated object."""


class FixedSizeArray:
    """Fixed-size array (not so)"""

    def __init_subclass__(cls, **kwargs) -> None:
        raise Exception("Cannot subclass FSA.")

    def __init__(self, size: int, noallocate=False):
        self._size = size
        self.__array: List[Union[ConstCreator, Any]] = [null]*size
        self.__sizeof__ = lambda self: size
        self.__fake_address_UUID = PUID.make_random()
        self.__fake_address = self.__fake_address_UUID.body.upper()
        self.__noalloc = noallocate
        self._name = None
        self._owner = None

    def insert(self, index: int, data: Any):
        """Insert an object before index"""
        self._yell_at_externally_extended_size()
        if index > self._size-1:
            raise IndexError(
                "Array index out of range; you can do self.allocate(<length>)")
        self.__array.insert(index, data)
        self.__array.pop(index+1)

    def pop(self, index: int):
        """Remove and return an item at index."""
        self._yell_at_externally_extended_size()
        self.__array.insert(index, null)
        return self.__array.pop(index+1)

    def remove(self, value):
        """Remove an item based on value"""
        self._yell_at_externally_extended_size()
        i = self.__array.index(value)
        self.pop(i)

    def __len__(self):
        """Implement len(self)"""
        return self._size

    def __iter__(self):
        """Implement iter(self)"""
        yield self.__array.__iter__()

    def clear(self):
        """Clear all item from array."""
        self.__array.clear()
        self.__array.extend([null]*self._size)

    def copy(self, noalloc: bool = True) -> 'FixedSizeArray':
        """Copy an item from an array"""
        ret = FixedSizeArray(self._size, noalloc)
        for i, x in enumerate(self):
            if x is null:
                continue
            ret.insert(i, x)

    @classmethod
    def new(cls, *instances) -> 'FixedSizeArray':
        """Create a new FixedSizeArray"""
        if len(instances) == 1:
            if hasattr(instances[0], '__iter__'):
                instances = instances[0]
        self = cls(len(instances))
        for i, x in enumerate(instances):
            self.insert(i, x)

    def __setitem__(self, index: int, value: int):
        """Implement self[index] = value"""
        if index > self._size-1:
            raise IndexError('Array out of range')
        self.insert(index, value)

    def __getitem__(self, index: int):
        """Implement self[index]"""
        if index > self._size-1:
            raise IndexError("Array out of range")
        return self.__array[index]

    reset = clear

    # Breaking the name rule

    def allocate(self, size: int):
        """Allocate new size for the array"""
        if self.__noalloc is True:
            raise Exception("This array can't be allocated.")
        self.__array.extend([null]*size)
        self._size = len(self.__array)

    def free(self, size: int):
        """Release/take away size from the array."""
        if self.__noalloc is True:
            self.reset()
            return
        size = abs(size)
        if size > len(self.__array):
            raise Exception(
                "Failed to freeing larger amount of allocated data.")
        if size == 0:
            self.__array.clear()
            self._size = 0
        else:
            self.__array = self.__array[:len(self.__array)-size]
            self._size = len(self.__array)

    # end of rule breaker

    @property
    def address(self):
        """Return pseudo address of this array."""
        return self.__fake_address

    @property
    def allocated(self):
        """Return how much allocated data in this array."""
        return len([data for data in self.__array if data is not null])

    @property
    def size(self):
        """"Return the size of this array."""
        return self._size

    # We can finally calculate used space or whatever

    @property
    def allow_alloc(self):
        """Return true if this array allocable"""
        return not self.__noalloc

    @property
    def linked_name(self):
        """Return link name of this array. None if unbind."""
        return self._name

    def _yell_at_externally_extended_size(self):
        """Raise if the array is externally changed."""
        if len(self.__array) > self._size:
            raise Exception(
                "The array is externally edited. Size of array is unmatched with current size. No 'auto' alloc.")

    def __repr__(self):
        """Return repr(self)"""
        return repr(self.__array)

    def _set_name(self, owner: LinkedFSA, name: str):
        """Set link name of this array. Owner must be instance of LinksedFSA"""
        if not isinstance(owner, LinkedFSA):
            raise Exception("Is not LinkedFSA object")
        if self._name is not None:
            if owner != self._owner:
                raise Exception(
                    f"This FSA seems locked by a LinkedFSA object. (pre-owner ref: {owner.name} | owner ref: {self._owner.name}")
        self._name = name
        self._owner = owner

    def _reset_name(self, owner: LinkedFSA):
        """Reset link name of this array. Or, unbind this array."""
        if not isinstance(owner, LinkedFSA):
            raise Exception("Invalid owner type")
        if not owner == self._owner:
            raise Exception("Invalid owner object")
        self._name = None
        self._owner = None

    @property
    def name(self):
        """Return linked name of this array"""
        return self._name

    def __contains__(self, other):
        """Return true if something is in this array."""
        return other in self.__array if other is not null else False


class LinkedFSA:
    """Linked FixedSizeArray"""

    def __init_subclass__(cls, **kwargs) -> None:
        raise Exception("LinkedFSA must not be subclassed.")

    def __init__(self, *array: FixedSizeArray):
        self._links: List[FixedSizeArray] = []
        self._linkID = PUID.make_random()
        for x in array:
            self._watcher(x)
            self.append(x)

    def _watcher(self, array: FixedSizeArray):
        """Watcher method of incoming array"""
        if not isinstance(array, FixedSizeArray):
            raise TypeError("The type of array is not FixedSizeArray.")

    def detach(self, block_index: int):
        """Detaching and unlock a FixedSizeArray"""
        fsa = self._links.pop(block_index)
        self._links.insert(block_index, fsa_null)
        fsa._reset_name(self)

    def __len__(self):
        """Implement len(self)"""
        return len(self._links)

    # Report methods

    def _get_report(self):
        """Get link report"""
        print(f"=== Report for {self._linkID.body.upper()} ===")
        for i, link in enumerate(self._links):
            if link is fsa_null:
                print(f"NULL on link-block({i}) size=0 avail=0% alloc=0")
                continue
            print(f"{link.address} on {link.name} size={link.size} avail={(link.size-link.allocated)/link.size*100}% alloc={link.allocated}")
        print(f"==============={'='*len(self._linkID.body.upper())}====")

    # end of Report methods definitions

    @property
    def available(self):
        """Value indicating how much data is available in all blocks"""
        x = 0
        for link in self._links:
            if link is fsa_null:
                continue  # skip on NULL
            x += link.size - link.allocated
        return x

    @property
    def lsa(self):
        """Link size-available"""
        x = []
        for link in self._links:
            if link is fsa_null:
                x.append(0)
                continue
            x.append(link.size - link.allocated)
        return tuple(x)

    @property
    def linksize(self):
        """Link size"""
        x = []
        for link in self._links:
            if link is fsa_null:
                x.append(0)
                continue
            x.append(link.size)
        return tuple(x)

    @property
    def size(self):
        """Size of all link"""
        x = 0
        for link in self._links:
            if link is fsa_null:
                continue  # skip on NULL
            x += link.size
        return x

    @property
    def name(self):
        """Name or UID of this instance."""
        return self._linkID.body.upper()

    def __getitem__(self, index: int):
        """Implement self[index]"""
        return self._links[index]

    def __setitem__(self, index: int, value: Any):
        """Implement self[index] = value"""
        self.insert(index, value)

    def append(self, *value: FixedSizeArray):
        """Append a FixedSizeArray into this instance"""
        for x in value:
            self._watcher(x)
            addresses = [link.address for link in self._links]
            if x.address in addresses:
                raise ValueError(
                    "The value is somewhat exists in this LinkedFSA")
            lid = len(self._links)
            x._set_name(self, f'link-block({lid})')
            self._links.append(x)

    def insert(self, index: int, value: FixedSizeArray):
        """Insert a new link into given index"""
        self._watcher(value)
        value._set_name(self, f'link-block({index})')
        links = self._links[index:]
        [link._set_name(
            self, f'link-block({self._links.index(link)+1})') for link in links]
        self._links.insert(index, value)

    def pop(self, index: int) -> FixedSizeArray:
        """Get a FSA and removes it."""
        v = self[index]
        self.detach(index)
        return v

    def remove(self, value: FixedSizeArray):
        """Remove a FSA from this instance"""
        self._watcher(value)
        i = self._links.index(value)
        self.detach(i)

    def replace(self, index: int, value: FixedSizeArray):
        """Replace a FSA/NULL from this instance in given index"""
        self._watcher(value)
        if self[index] is not fsa_null:
            self.detach(index)
        name = f'link-block({index})'
        value._set_name(self, name)
        self._links.insert(index, value)
        self._links.pop(index+1)

    def __contains__(self, other):
        """Return true if other in this instance."""
        for link in self._links:
            if link is fsa_null:
                continue
            if other in link:
                return True
        return False

    def __repr__(self):
        """Implement repr(self)"""
        return '['+', '.join((link.address if hasattr(link, 'address') else str(link)) for link in self._links)+']'

    def _smart_index(self, link_index: int):
        # Say, index is 80 while our links is 2 50-sized array. 80-50 = 30
        # This may can't use negative index. but, let's see...
        # Return: Link index, link's index
        if link_index > self.size:
            raise IndexError(
                f"Linked Index out of range ({link_index} > {self.size}; perhaps you forgot to append?)")
        if link_index < 0:
            while link_index < 0:
                link_index += self.size
        clsa = self.linksize
        tli = link_index
        for i, a in enumerate(clsa):
            if tli > a:
                tli -= a
                continue
            if self[i] is fsa_null:
                if len(self) == i:
                    raise IndexError("Index out or range")
                i += 1
            if tli == len(self[i]):
                if len(self) == i:
                    raise IndexError("Index out or range")
                if self[i+1] == fsa_null:
                    if len(self) == i+1:
                        raise IndexError("Index out or range")
                    return i+2, 0
                return i+1, 0
            return i, tli
        raise Exception("Smart index can't return!")

    def smart_insert(self, link_index: int, value: Any):
        """Insert a value into a link from a given index (The index should be less than self.size)"""
        i, li = self._smart_index(link_index)
        self[i][li] = value

    def smart_get(self, link_index: int) -> Any:
        """Get a value from a link in a given index (The index should be less than self.size)"""
        i, li = self._smart_index(link_index)
        return self[i][li]

    def smart_pop(self, link_index: int) -> Any:
        """Get and remove a value from a link in a given index (The index should be less than self.size)"""
        i, li = self._smart_index(link_index)
        return self[i].pop(li)

    def smart_remove(self, data: Any):
        """Remove a value from a link. The first matching item on a link is removed. This, doesn't really remove all matching items."""
        for link in self._links:
            if link is fsa_null:
                continue
            if data in link:
                link.remove(data)
                return

    def __eq__(self, other):
        """Implement self==other"""
        if isinstance(other, LinkedFSA):
            return self._linkID == other._linkID


class Inventory:
    """Inventory class"""

    def __init__(self, iname: str, size: int, *args):
        """Init function"""
        self._name = iname
        self._array_list = LinkedFSA(FixedSizeArray(size, True))

    def extend_inventory(self, array: FixedSizeArray):
        """Adding an Inventory array"""
        if array is self._array or array.address == self._array.address:
            raise SameIdentifierException(
                "array is the same as this instance array.")

        if array.allow_alloc is True:
            warnings.warn("array is allocate-able.")
            array = array.new()
        self._array_list.append(array)

    def __setitem__(self, index: int, value: Any):
        """Implement self[index] = value."""
        return self.insert(index, value)

    def __getitem__(self, index: int):
        """Implement self[index]."""
        return self._array_list.smart_get(index)

    def insert(self, index: int, data: Any):
        """Insert an item from inventory"""
        self._array_list.smart_insert(index, data)

    def pop(self, index: int):
        """Pop an item from inventory"""
        self._array_list.smart_pop(index)

    def remove(self, data: Any):
        """Remove an item from inventory"""
        self._array_list.smart_remove(data)

    def detach_inventory(self, array_id):
        """Release a inventory"""
        self._array_list.detach(array_id)

    def __repr__(self):
        return f"Inventory({self._name})"
