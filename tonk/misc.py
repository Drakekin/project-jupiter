from enum import StrEnum
from typing import TypeVar, Generic

T = TypeVar("T")


class Arc(StrEnum):
    front = "Front"
    side = "Side"
    rear = "Rear"


class Direction(StrEnum):
    front = "Front"
    left = "Left"
    right = "Right"
    rear = "Rear"


class Arcs(Generic[T]):
    front: T
    side: T
    rear: T

    def __init__(self, front: T, side: T, rear: T):
        self.front = front
        self.side = side
        self.rear = rear

    def __getitem__(self, item: Arc):
        if item == Arc.front:
            return self.front
        elif item == Arc.side:
            return self.side
        elif item == Arc.rear:
            return self.rear


class D6Table(Generic[T]):
    one: T
    two: T
    three: T
    four: T
    five: T
    six: T

    def __init__(self, *args):
        self.one, self.two, self.three, self.four, self.five, self.six = args

    def __getitem__(self, item: int):
        return (self.one, self.two, self.three, self.four, self.five, self.six)[item - 1]
