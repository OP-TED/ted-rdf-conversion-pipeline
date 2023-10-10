#!/usr/bin/python3

# test_pydantic.py
# Date:  08/02/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class Metadata(BaseModel):
    object_data: bytes


class User(BaseModel):
    id: int
    name: str = 'John Doe'
    signup_ts: Optional[datetime] = None
    friends: List[int] = []


class Foo(BaseModel):
    count: int
    size: float = None


class Bar(BaseModel):
    apple: str = 'x'
    banana: str = 'y'


class Spam(BaseModel):
    foo: Foo
    bars: List[Bar]


def test_pydantic_1():
    external_data = {
        'id': '123',
        'signup_ts': '2019-06-01 12:22',
        'friends': [1, 2, '3'],
    }
    external_data_1 = {

        'signup_ts': '2019-06-01 12:22',
        'friends': [1, 2, '3'],
    }

    User(**external_data)

    User.model_construct(external_data_1)


def test_pydantic_2():
    m = Spam(foo={'count': 4}, bars=[{'apple': 'x1'}, {'apple': 'x2'}])
    assert isinstance(m.foo, Foo)
