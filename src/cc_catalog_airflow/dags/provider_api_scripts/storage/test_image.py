import pytest
import logging

from storage import image

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.DEBUG)


def test_init_includes_provider_in_output_files_string():
    image_store = image.ImageStore('test_provider')
    assert type(image_store._OUTPUT_FILE) == str
    assert 'test_provider' in image_store._OUTPUT_FILE


def test_ImageStore_get_image_correctly_places_given_args(monkeypatch):
    image_store = image.ImageStore(provider='testing_provider')
    args_dict = {
        'foreign_landing_url': 'https://landing_page.com',
        'image_url': 'http://imageurl.com',
        'license_': 'testlicense',
        'license_version': '1.0',
        'license_url': None,
        'foreign_identifier': 'foreign_id',
        'thumbnail_url': 'http://thumbnail.com',
        'width': 200,
        'height': 500,
        'filesize': None,
        'creator': 'tyler',
        'creator_url': 'https://creatorurl.com',
        'title': 'agreatpicture',
        'meta_data': {'description': 'cat picture'},
        'raw_tags': [{'name': 'tag1', 'provider': 'testing'}],
        'watermarked': 'f',
        'source': 'testing_source'
    }

    def mock_license_chooser(license_url, license_, license_version):
        return license_, license_version
    monkeypatch.setattr(
        image.util,
        'choose_license_and_version',
        mock_license_chooser
    )

    def mock_get_source(source, provider):
        return source
    monkeypatch.setattr(
        image.util,
        'get_source',
        mock_get_source
    )

    def mock_get_enriched_tags(tags):
        return tags
    monkeypatch.setattr(
        image_store,
        '_get_enriched_tags',
        mock_get_enriched_tags
    )

    actual_image = image_store._get_image(**args_dict)
    args_dict['tags'] = args_dict.pop('raw_tags')
    args_dict.pop('license_url')
    args_dict['provider'] = 'testing_provider'
    assert actual_image == image._Image(**args_dict)


def test_ImageStore_get_image_calls_license_chooser(
        monkeypatch,
):
    image_store = image.ImageStore()

    def mock_license_chooser(license_url, license_, license_version):
        return 'diff_license', None
    monkeypatch.setattr(
        image.util,
        'choose_license_and_version',
        mock_license_chooser
    )

    actual_image = image_store._get_image(
        license_url='https://license/url',
        license_='license',
        license_version='1.5',
        foreign_landing_url=None,
        image_url=None,
        thumbnail_url=None,
        foreign_identifier=None,
        width=None,
        height=None,
        filesize=None,
        creator=None,
        creator_url=None,
        title=None,
        meta_data=None,
        raw_tags=None,
        watermarked=None,
        source=None,
    )
    assert actual_image.license_ == 'diff_license'


def test_ImageStore_get_image_gets_source(monkeypatch):
    image_store = image.ImageStore()

    def mock_get_source(source, provider):
        return 'diff_source'
    monkeypatch.setattr(image.util, 'get_source', mock_get_source)

    actual_image = image_store._get_image(
        license_url='https://license/url',
        license_='license',
        license_version='1.5',
        foreign_landing_url=None,
        image_url=None,
        thumbnail_url=None,
        foreign_identifier=None,
        width=None,
        height=None,
        filesize=None,
        creator=None,
        creator_url=None,
        title=None,
        meta_data=None,
        raw_tags=None,
        watermarked=None,
        source=None,
    )
    assert actual_image.source == 'diff_source'


def test_ImageStore_get_image_nones_non_dict_meta_data():
    image_store = image.ImageStore()

    actual_image = image_store._get_image(
        license_url='https://license/url',
        license_='license',
        license_version='1.5',
        foreign_landing_url=None,
        image_url=None,
        thumbnail_url=None,
        foreign_identifier=None,
        width=None,
        height=None,
        filesize=None,
        creator=None,
        creator_url=None,
        title=None,
        meta_data='notadict',
        raw_tags=None,
        watermarked=None,
        source=None,
    )
    assert actual_image.meta_data is None


def test_ImageStore_get_image_leaves_dict_meta_data():
    image_store = image.ImageStore()

    actual_image = image_store._get_image(
        license_url='https://license/url',
        license_='license',
        license_version='1.5',
        foreign_landing_url=None,
        image_url=None,
        thumbnail_url=None,
        foreign_identifier=None,
        width=None,
        height=None,
        filesize=None,
        creator=None,
        creator_url=None,
        title=None,
        meta_data={'key1': 'val1'},
        raw_tags=None,
        watermarked=None,
        source=None,
    )
    assert actual_image.meta_data == {'key1': 'val1'}


def test_ImageStore_get_image_enriches_singleton_tags():
    image_store = image.ImageStore('test_provider')

    actual_image = image_store._get_image(
        license_url='https://license/url',
        license_='license',
        license_version='1.5',
        foreign_landing_url=None,
        image_url=None,
        thumbnail_url=None,
        foreign_identifier=None,
        width=None,
        height=None,
        filesize=None,
        creator=None,
        creator_url=None,
        title=None,
        meta_data=None,
        raw_tags=['lone'],
        watermarked=None,
        source=None,
    )

    assert actual_image.tags == [{'name': 'lone', 'provider': 'test_provider'}]


def test_ImageStore_get_image_enriches_multiple_tags():
    image_store = image.ImageStore('test_provider')
    actual_image = image_store._get_image(
        license_url='https://license/url',
        license_='license',
        license_version='1.5',
        foreign_landing_url=None,
        image_url=None,
        thumbnail_url=None,
        foreign_identifier=None,
        width=None,
        height=None,
        filesize=None,
        creator=None,
        creator_url=None,
        title=None,
        meta_data=None,
        raw_tags=['tagone', 'tag2', 'tag3'],
        watermarked=None,
        source=None,
    )

    assert actual_image.tags == [
        {'name': 'tagone', 'provider': 'test_provider'},
        {'name': 'tag2', 'provider': 'test_provider'},
        {'name': 'tag3', 'provider': 'test_provider'},
    ]


def test_ImageStore_get_image_leaves_preenriched_tags():
    image_store = image.ImageStore('test_provider')
    tags = [
        {'name': 'tagone', 'provider': 'test_provider'},
        {'name': 'tag2', 'provider': 'test_provider'},
        {'name': 'tag3', 'provider': 'test_provider'},
    ]

    actual_image = image_store._get_image(
        license_url='https://license/url',
        license_='license',
        license_version='1.5',
        foreign_landing_url=None,
        image_url=None,
        thumbnail_url=None,
        foreign_identifier=None,
        width=None,
        height=None,
        filesize=None,
        creator=None,
        creator_url=None,
        title=None,
        meta_data=None,
        raw_tags=['tagone', 'tag2', 'tag3'],
        watermarked=None,
        source=None,
    )

    assert actual_image.tags == tags


def test_ImageStore_get_image_nones_nonlist_tags():
    image_store = image.ImageStore('test_provider')
    tags = 'notalist'

    actual_image = image_store._get_image(
        license_url='https://license/url',
        license_='license',
        license_version='1.5',
        foreign_landing_url=None,
        image_url=None,
        thumbnail_url=None,
        foreign_identifier=None,
        width=None,
        height=None,
        filesize=None,
        creator=None,
        creator_url=None,
        title=None,
        meta_data=None,
        raw_tags=tags,
        watermarked=None,
        source=None,
    )

    assert actual_image.tags is None


@pytest.fixture
def default_image_args():
    return dict(
        foreign_identifier=None,
        foreign_landing_url='https://image.org',
        image_url='https://image.org',
        thumbnail_url=None,
        width=None,
        height=None,
        filesize=None,
        license_='cc0',
        license_version='1.0',
        creator=None,
        creator_url=None,
        title=None,
        meta_data=None,
        tags=None,
        watermarked=None,
        provider=None,
        source=None,
    )


def test_create_tsv_row_non_none_if_required_fields(default_image_args):
    image_store = image.ImageStore()
    test_image = image._Image(**default_image_args)
    actual_row = image_store._create_tsv_row(test_image)
    assert actual_row is not None


def test_create_tsv_row_none_if_no_foreign_landing_url(default_image_args):
    image_store = image.ImageStore()
    image_args = default_image_args
    image_args['foreign_landing_url'] = None
    test_image = image._Image(**image_args)
    expect_row = None
    actual_row = image_store._create_tsv_row(test_image)
    assert expect_row == actual_row


def test_create_tsv_row_none_if_no_license(default_image_args):
    image_store = image.ImageStore()
    image_args = default_image_args
    image_args['license_'] = None
    test_image = image._Image(**image_args)
    expect_row = None
    actual_row = image_store._create_tsv_row(test_image)
    assert expect_row == actual_row


def test_create_tsv_row_none_if_no_license_version(default_image_args):
    image_store = image.ImageStore()
    image_args = default_image_args
    image_args['license_version'] = None
    test_image = image._Image(**image_args)
    expect_row = None
    actual_row = image_store._create_tsv_row(test_image)
    assert expect_row == actual_row


def test_create_tsv_row_returns_none_if_missing_image_url(default_image_args):
    image_store = image.ImageStore()
    image_args = default_image_args
    image_args['image_url'] = None
    test_image = image._Image(**image_args)
    expect_row = None
    actual_row = image_store._create_tsv_row(test_image)
    assert expect_row == actual_row


def test_create_tsv_row_handles_empty_dict_and_tags(default_image_args):
    image_store = image.ImageStore()
    meta_data = {}
    tags = []
    image_args = default_image_args
    image_args['meta_data'] = meta_data
    image_args['tags'] = tags
    test_image = image._Image(**image_args)

    actual_row = image_store._create_tsv_row(test_image).split('\t')
    actual_meta_data, actual_tags = actual_row[12], actual_row[13]
    expect_meta_data, expect_tags = '\\N', '\\N'
    assert expect_meta_data == actual_meta_data
    assert expect_tags == actual_tags


def test_create_tsv_row_turns_empty_into_nullchar(default_image_args):
    image_store = image.ImageStore()
    image_args = default_image_args
    test_image = image._Image(**image_args)

    actual_row = image_store._create_tsv_row(test_image).split('\t')
    assert all(
        [
            actual_row[i] == '\\N'
            for i in [0, 3, 4, 5, 6, 9, 10, 11, 12, 13, 14, 15]
        ]
    ) is True
    assert actual_row[-1] == '\\N\n'


def test_create_tsv_row_properly_places_entries():
    image_store = image.ImageStore()
    req_args_dict = {
        'foreign_landing_url': 'https://landing_page.com',
        'image_url': 'http://imageurl.com',
        'license_': 'testlicense',
        'license_version': '1.0',
    }
    args_dict = {
        'foreign_identifier': 'foreign_id',
        'thumbnail_url': 'http://thumbnail.com',
        'width': 200,
        'height': 500,
        'filesize': None,
        'creator': 'tyler',
        'creator_url': 'https://creatorurl.com',
        'title': 'agreatpicture',
        'meta_data': {'description': 'cat picture'},
        'tags': [{'name': 'tag1', 'provider': 'testing'}],
        'watermarked': 'f',
        'provider': 'testing_provider',
        'source': 'testing_source'
    }
    args_dict.update(req_args_dict)

    test_image = image._Image(**args_dict)
    actual_row = image_store._create_tsv_row(
        test_image
    )
    expect_row = '\t'.join([
        'foreign_id',
        'https://landing_page.com',
        'http://imageurl.com',
        'http://thumbnail.com',
        '200',
        '500',
        '\\N',
        'testlicense',
        '1.0',
        'tyler',
        'https://creatorurl.com',
        'agreatpicture',
        '{"description": "cat picture"}',
        '[{"name": "tag1", "provider": "testing"}]',
        'f',
        'testing_provider',
        'testing_source'
    ]) + '\n'
    assert expect_row == actual_row
