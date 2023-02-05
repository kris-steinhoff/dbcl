import pytest

from dbcl.command_line import print_data, print_result, ResourceClosedError


@pytest.mark.parametrize(
    "data,output",
    (
        (
            [["one", "two"], [1, 2], [3, 4]],
            (
                "\x1b(0lqqqqqwqqqqqk\x1b(B\n\x1b(0x\x1b(B one \x1b(0x\x1b(B two "
                "\x1b(0x\x1b(B\n\x1b(0tqqqqqnqqqqqu\x1b(B\n\x1b(0x\x1b(B 1   "
                "\x1b(0x\x1b(B 2   \x1b(0x\x1b(B\n\x1b(0x\x1b(B 3   \x1b(0x"
                "\x1b(B 4   \x1b(0x\x1b(B\n\x1b(0mqqqqqvqqqqqj\x1b(B\n"
            ),
        ),
    ),
)
def test_good_data(data, output, capsys):
    print_data(data)

    out, err = capsys.readouterr()
    assert out == output


def test_closed_resource(mocker, capsys):
    mock_result = mocker.Mock(side_effect=ResourceClosedError)
    mock_result.keys = mocker.Mock(side_effect=ResourceClosedError)

    print_result(mock_result)

    out, err = capsys.readouterr()
    assert out == ""
