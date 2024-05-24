from datetime import datetime, timedelta

from django.contrib.auth.models import Group, Permission

import pytest
from freezegun import freeze_time
from redis import Redis

from api.utils.moderation_lock import LockManager


pytestmark = pytest.mark.django_db


@pytest.fixture
def mod_group():
    perms_to_add = ["view", "add", "change"]
    models_to_affect = [
        "audio report",
        "image report",
        "sensitive audio",
        "sensitive image",
    ]

    mod_group, created = Group.objects.get_or_create(name="Content Moderators")
    if created:
        for model in models_to_affect:
            for perm in perms_to_add:
                name = f"Can {perm} {model}"
                model_add_perm = Permission.objects.get(name=name)
                mod_group.permissions.add(model_add_perm)
    mod_group.save()
    return mod_group


@pytest.fixture(autouse=True)
def moderators(django_user_model, mod_group):
    for username in ["one", "two"]:
        user = django_user_model.objects.create(username=username, password=username)
        mod_group.user_set.add(user)


@pytest.mark.parametrize(
    "is_cache_reachable, cache_name",
    [(True, "redis"), (False, "unreachable_redis")],
)
def test_lock_manager_handles_missing_redis(is_cache_reachable, cache_name, request):
    request.getfixturevalue(cache_name)

    lm = LockManager("media_type")
    lm.add_locks("one", 10)

    if is_cache_reachable:
        assert isinstance(lm.redis, Redis)
        assert lm.moderator_set(10) == {"one"}
    else:
        assert lm.redis is None
        assert lm.moderator_set(10) == set()


def test_lock_manager_adds_and_removes_locks():
    lm = LockManager("media_type")

    lm.add_locks("one", 10)
    assert lm.moderator_set(10) == {"one"}
    lm.add_locks("two", 10)
    assert lm.moderator_set(10) == {"one", "two"}
    lm.remove_locks("two", 10)
    assert lm.moderator_set(10) == {"one"}


def test_relocking_updates_score(redis):
    lm = LockManager("media_type")
    now = datetime.now()

    with freeze_time(now):
        lm.add_locks("one", 10)
        init_score = lm.score("one", 10)

    with freeze_time(now + timedelta(minutes=2)):
        lm.add_locks("one", 10)
        updated_score = lm.score("one", 10)

    assert updated_score == init_score + 120


def test_lock_manager_prunes_after_timeout():
    lm = LockManager("media_type")
    now = datetime.now()

    with freeze_time(now):
        lm.add_locks("one", 10)

    with freeze_time(now + timedelta(minutes=2)):
        lm.prune()
        assert lm.moderator_set(10) == {"one"}

    with freeze_time(now + timedelta(minutes=6)):
        lm.prune()
        assert lm.moderator_set(10) == set()
