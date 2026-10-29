import pytest

from djstell.pages.templatetags.tags import combined_more_blog, top_areas


@pytest.fixture
def warm_caches(db):
    # These are computed once per process, so don't count them against
    # whichever page happens to render first.
    combined_more_blog()
    top_areas()


@pytest.mark.parametrize("url", [
    "/blog/all",
    "/blog/2024",
    "/blog/date/0101",
    "/blog/drafts",
    "/blog/classics/tech",
    "/blog/tag/python",
    "/blog/tag/none",
])
def test_entry_lists_prefetch_tags(client, warm_caches, django_assert_max_num_queries, url):
    with django_assert_max_num_queries(5):
        resp = client.get(url)
    assert resp.status_code == 200
