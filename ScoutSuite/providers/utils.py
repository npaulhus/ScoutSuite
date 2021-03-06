import asyncio

from hashlib import sha1


def get_non_provider_id(name):
    """
    Not all resources have an ID and some services allow the use of "." in names, which breaks Scout's
    recursion scheme if name is used as an ID. Use SHA1(name) instead.

    :param name:                    Name of the resource to
    :return:                        SHA1(name)
    """
    name_hash = sha1()
    name_hash.update(name.encode('utf-8'))
    return name_hash.hexdigest()


def run_concurrently(func):
    """
    Schedules the execution of function `func` in the default thread pool (referred as 'executor') that has been
    associated with the global event loop.

    :param func: function to be executed concurrently, in a dedicated thread.
    :return: an asyncio.Future to be awaited.
    """

    return asyncio.get_event_loop().run_in_executor(executor=None, func=func)


async def get_and_set_concurrently(get_and_set_funcs: [], entities: [], **kwargs):
    """
    Given a list of get_and_set_* functions (ex: get_and_set_description, get_and_set_attributes,
    get_and_set_policy, etc.) and a list of entities (ex: stacks, keys, load balancers, vpcs, etc.),
    get_and_set_concurrently will call each of these functions concurrently on each entity.

    :param get_and_set_funcs: list of functions that takes a region and an entity (they must have the following
    signature: region: str, entity: {}) and then fetch and set some kind of attributes to this entity.
    :param entities: list of a same kind of entities
    :param region: a region

    :return:
    """

    if len(entities) == 0:
        return

    tasks = {
        asyncio.ensure_future(
            get_and_set_func(entity, **kwargs)
        ) for entity in entities for get_and_set_func in get_and_set_funcs
    }
    await asyncio.wait(tasks)


async def map_concurrently(coro, entities, **kwargs):
    """
    Given a list of entities, executes coroutine `coro` concurrently on each entity and returns a list of the obtained
    results ([await coro(entity_x), await coro(entity_a), ..., await coro(entity_z)]).

    :param coro: coroutine to be executed concurrently. Takes an entity as parameter and returns a new entity.
    :param entities: a list of the same type of entity (ex: cluster ids)

    :return: a list of new entities (ex: clusters)
    """

    if len(entities) == 0:
        return []

    results = []
    tasks = {
        asyncio.ensure_future(
            coro(entity, **kwargs)
        ) for entity in entities
    }
    for task in asyncio.as_completed(tasks):
        result = await task
        results.append(result)

    return results
