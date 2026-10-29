import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from djstell.pages.templatetags.tags import combined_more_blog, top_areas


@pytest.fixture
def warm_caches(db):
    # These are computed once per process, so don't count them against
    # whichever page happens to render first.
    combined_more_blog()
    top_areas()


@pytest.mark.parametrize("url", [
    "/",
    "/blog/all",
    "/blog/2024",
    "/blog/date/0101",
    "/blog/drafts",
    "/blog/classics/tech",
    "/blog/tag/python",
    "/blog/tag/none",
    "/blog/tags",
])
def test_entry_lists_prefetch_tags(client, warm_caches, django_assert_max_num_queries, url):
    with django_assert_max_num_queries(5):
        resp = client.get(url)
    assert resp.status_code == 200


@pytest.mark.django_db(databases=["default", "reactor"])
@pytest.mark.parametrize("url", [
    "/blog",
    "/blog/200903/its_all_greek_to_me",
    "/blog/201101/the_aporetics_living_history",
])
def test_entry_footers_prefetch(client, warm_caches, url):
    # These pages also resolve links in the entry text, so the total varies
    # with the content. Just check the footer's tables are read once.
    with CaptureQueriesContext(connection) as ctx:
        resp = client.get(url)
    assert resp.status_code == 200
    for table in ["pages_tag", "pages_via", "pages_link"]:
        froms = [q for q in ctx.captured_queries if f'FROM "{table}"' in q["sql"]]
        assert len(froms) <= 1, f"{table} read {len(froms)} times"
