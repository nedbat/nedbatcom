import pytest

def fill_labeled_input(page, label, value):
    id = input_for_label(page, label)
    return page.fill(f"#{id}", value)

def input_for_label(page, label):
    assert "'" not in label
    labels = page.query_selector_all(f"label:has-text('{label}')")
    assert len(labels) == 1
    return labels[0].get_attribute("for")

def labeled_input_value(page, label):
    id = input_for_label(page, label)
    return page.input_value(f"#{id}")

def errors(page):
    return [elt.inner_text() for elt in page.query_selector_all(".errormsg")]

def nav(meth, *args, **kwargs):
    __tracebackhide__ = True
    with meth.__self__.expect_response("*") as response_info:
        meth(*args, **kwargs)
    response = response_info.value
    assert response.status == 200, f"{response.request.method} {response.url} returned {response.status}"

PREVIEW = "Preview >>"
ADD_IT = "Add it >>"
BLOG_POST = "/blog/200203/my_first_job_ever.html"

@pytest.mark.parametrize("url, title", [
    ("/blog/202108/me_on_bug_hunters_caf.html", "Me on Bug Hunters Café"),
    ("/blog/200203/my_first_job_ever.html", "My first job ever"),
])
def test_blog_post(page, url, title):
    nav(page.goto, url)
    assert page.inner_text("h1") == title
    assert page.title() == f"{title} | Ned Batchelder"
    # No errors on the page.
    assert errors(page) == []
    # No previewed comment.
    assert page.query_selector_all(".comment.preview") == []
    # There is a preview button, but no Add It button.
    assert len(page.query_selector_all(f"input:has-text('{PREVIEW}')")) == 1
    assert len(page.query_selector_all(f"input:has-text('{ADD_IT}')")) == 0

def test_previewing(page):
    # Load the page and fill in the comment form.
    nav(page.goto, BLOG_POST)
    assert len(page.query_selector_all(".comment.preview")) == 0
    fill_labeled_input(page, "Name:", "Thomas Edison")
    fill_labeled_input(page, "Email:", "tom@edison.org")
    fill_labeled_input(page, "Comment:", "This is a great blog post!")

    # Click "preview", the page has a preview, and filled in fields.
    nav(page.click, f"input:has-text('{PREVIEW}')")
    assert errors(page) == []
    assert len(page.query_selector_all(".comment.preview")) == 1
    assert page.query_selector(".comment.preview .who").inner_text() == "Thomas Edison"
    assert page.query_selector(".comment.preview .commenttext").inner_text() == "This is a great blog post!"
    assert labeled_input_value(page, "Name:") == "Thomas Edison"
    assert labeled_input_value(page, "Email:") == "tom@edison.org"
    assert labeled_input_value(page, "Comment:") == "This is a great blog post!"
    assert len(page.query_selector_all(f"input:has-text('{PREVIEW}')")) == 1
    assert len(page.query_selector_all(f"input:has-text('{ADD_IT}')")) == 1

    # Reload the page, it has no preview, but the simple fields are filled in.
    nav(page.goto, BLOG_POST)
    assert len(page.query_selector_all(".comment.preview")) == 0
    assert labeled_input_value(page, "Name:") == "Thomas Edison"
    assert labeled_input_value(page, "Email:") == "tom@edison.org"
    assert labeled_input_value(page, "Comment:") == ""

NAME_MSG = "You must provide a name."
EMWB_MSG = "You must provide either an email or a website."
COMM_MSG = "You didn't write a comment!"

@pytest.mark.parametrize("name, email, website, comment, msgs", [
    (False, False, False, True, [NAME_MSG, EMWB_MSG]),
    (True, False, False, True, [EMWB_MSG]),
    (False, True, False, True, [NAME_MSG]),
    (True, True, False, False, [COMM_MSG]),
    (True, False, True, False, [COMM_MSG]),
    (True, False, False, False, [EMWB_MSG, COMM_MSG]),
])
def test_missing_info(page, name, email, website, comment, msgs):
    # Load the page and fill in the comment form.
    nav(page.goto, BLOG_POST)
    if name:
        fill_labeled_input(page, "Name:", " Thomas Edison")
    if email:
        fill_labeled_input(page, "Email:", "tom@edison.org ")
    if website:
        fill_labeled_input(page, "Web site:", " https://edison.org    ")
    if comment:
        fill_labeled_input(page, "Comment:", "This is a great blog post!")

    # Click "preview", the page has errors and no preview.
    nav(page.click, f"input:has-text('{PREVIEW}')")
    assert errors(page) == msgs
    assert len(page.query_selector_all(".comment.preview")) == 0
    assert labeled_input_value(page, "Comment:") == ("This is a great blog post!" if comment else "")
    assert labeled_input_value(page, "Name:") == ("Thomas Edison" if name else "")
    assert labeled_input_value(page, "Email:") == ("tom@edison.org" if email else "")
    assert labeled_input_value(page, "Web site:") == ("https://edison.org" if website else "")
    assert len(page.query_selector_all(f"input:has-text('{PREVIEW}')")) == 1
    assert len(page.query_selector_all(f"input:has-text('{ADD_IT}')")) == 0
