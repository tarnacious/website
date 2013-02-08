import redis
import uuid
import json

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)


def start(user):
    session_id = str(uuid.uuid1())
    session = {
        'user_id': user.id,
        'name': user.name,
        'provider': user.provider}
    redis_client.set(session_id, json.dumps(session))
    return session_id


def find(session_id):
    find = redis_client.get(session_id)
    if find:
        return json.loads(find)


def remove(session_id):
    if session_id:
        redis_client.delete(session_id)
