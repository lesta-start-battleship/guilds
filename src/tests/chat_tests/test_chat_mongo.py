import pytest
from bson import ObjectId
from datetime import datetime

from db.mongo.chat import MongoChatMessage


def test_create_model_from_valid_dict():
    message_dict = {
        "_id": str(ObjectId()),
        "guild_id": 1,
        "user_id": 42,
        "user_name": "Alice",
        "content": "Hello Mongo",
    }

    msg = MongoChatMessage(**message_dict)

    assert isinstance(msg.id, ObjectId)
    assert msg.guild_id == 1
    assert msg.user_id == 42
    assert msg.user_name == "Alice"
    assert msg.content == "Hello Mongo"
    assert isinstance(msg.timestamp, datetime)


def test_create_model_from_objectid_directly():
    message_dict = {
        "_id": ObjectId(),
        "guild_id": 2,
        "user_id": 99,
        "user_name": "Bob",
        "content": "Hi!"
    }

    msg = MongoChatMessage(**message_dict)
    assert isinstance(msg.id, ObjectId)
    assert msg.id == message_dict["_id"]


def test_serialization_of_id():
    obj_id = ObjectId()
    msg = MongoChatMessage(
        id=obj_id,
        guild_id=3,
        user_id=1,
        user_name="Test",
        content="Serialized"
    )

    dumped = msg.model_dump(by_alias=True)
    assert "_id" in dumped
    assert dumped["_id"] == str(obj_id)


def test_invalid_objectid_string():
    with pytest.raises(ValueError):
        MongoChatMessage(
            id="invalid_object_id",
            guild_id=1,
            user_id=1,
            user_name="Fail",
            content="Oops"
        )


def test_invalid_objectid_type():
    with pytest.raises(TypeError):
        MongoChatMessage(
            id=12345,
            guild_id=1,
            user_id=1,
            user_name="Fail",
            content="Oops"
        )


# def test_missing_optional_id():
#     msg = MongoChatMessage(
#         guild_id=10,
#         user_id=5,
#         user_name="NoID",
#         content="Still works"
#     )
#     assert msg.id is None
#     assert isinstance(msg.timestamp, datetime)
