import re
import pathlib


def sanitize(s):
    return re.sub(r"[\n\t\s]*", "", s)


def test_tpl_generator(tpl):
    path_to_test_tpl = pathlib.Path(__file__).parent.parent.parent / "test_data" / "notice_packager" / tpl
    return path_to_test_tpl.read_text()


def test(tpl_generator, data, test_tpl):
    tpl_render = tpl_generator.generate_tpl(data)
    test_tpl_render = test_tpl_generator(test_tpl)

    assert sanitize(tpl_render) == sanitize(test_tpl_render)

