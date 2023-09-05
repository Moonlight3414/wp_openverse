import pytest

from common.utils import setup_kwargs_for_media_type


TEST_VALS_BY_MEDIA_TYPE = {"audio": "foo", "image": "bar"}
p = pytest.param


@pytest.mark.parametrize(
    "media_type, my_param, expected_param",
    (
        ("audio", None, "foo"),
        ("image", None, "bar"),
        # Pass in an explicit value for my_param; this should be returned
        p(
            "audio",
            "hello world",
            "hello world",
            id="explicitly passed value should be returned",
        ),
        p(
            "foo",
            "hello world",
            "hello world",
            id="explicitly passed value is returned, even if the values dict does not have a key for the media type",
        ),
        # No media type
        p(
            None,
            None,
            None,
            marks=pytest.mark.raises(exception=ValueError),
            id="raises error when no media type passed",
        ),
        p(
            "foo",
            None,
            None,
            marks=pytest.mark.raises(exception=ValueError),
            id="raises error when no matching key in values dict",
        ),
    ),
)
def test_setup_kwargs_for_media_type(media_type, my_param, expected_param):
    @setup_kwargs_for_media_type(TEST_VALS_BY_MEDIA_TYPE, "my_param")
    def test_fn(media_type: str, my_param: str = None):
        assert my_param == expected_param

    test_fn(media_type=media_type, my_param=my_param)


def test_setup_kwargs_for_media_type_creates_new_decorator():
    # Create a new decorator using the factory
    new_decorator = setup_kwargs_for_media_type(TEST_VALS_BY_MEDIA_TYPE, "new_param")

    # New function decorated with this decorator
    @new_decorator
    def test_fn(media_type: str, new_param: str = None):
        return new_param

    assert test_fn(media_type="audio") == "foo"


def test_setup_kwargs_for_media_type_fails_without_media_type_kwarg():
    # Decorated function does not have a media_type kwarg
    @setup_kwargs_for_media_type(TEST_VALS_BY_MEDIA_TYPE, "my_param")
    def test_fn(my_param: str = None):
        return my_param

    with pytest.raises(ValueError, match="Missing `media_type` kwarg."):
        test_fn()


def test_setup_kwargs_for_media_type_fails_with_media_type_arg():
    # Decorated function sets up media_type as an *arg*
    @setup_kwargs_for_media_type(TEST_VALS_BY_MEDIA_TYPE, "my_param")
    def test_fn(media_type, my_param: str = None):
        return my_param

    with pytest.raises(ValueError, match="Missing `media_type` kwarg."):
        # Pass media_type as arg rather than kwarg
        test_fn("audio")


def test_setup_kwargs_for_media_type_fails_without_kwarg():
    # Decorated function does not have the kwarg we want populated
    @setup_kwargs_for_media_type(TEST_VALS_BY_MEDIA_TYPE, "my_param")
    def test_fn(media_type: str):
        pass

    with pytest.raises(
        TypeError,
        match="got an unexpected keyword argument 'my_param'",
    ):
        test_fn(media_type="audio")
