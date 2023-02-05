import pytest

from dbcl.command_line import command_loop


@pytest.fixture()
def mock_get_args(mocker):
    return mocker.patch("dbcl.command_line.get_args")


@pytest.fixture()
def mock_get_engine(mocker):
    return mocker.patch("dbcl.command_line.get_engine")


@pytest.fixture()
def mock_in_memory_history(mocker):
    return mocker.patch("dbcl.command_line.FileHistory")


def test_bad_connection(mock_get_args, mocker, capsys):
    mock_create_engine = mocker.patch("dbcl.command_line.create_engine")
    mock_create_engine.return_value.connect = mocker.MagicMock(
        side_effect=Exception("connection error")
    )

    with pytest.raises(SystemExit) as excinfo:
        command_loop()

    assert excinfo.value.code == 1

    out, err = capsys.readouterr()
    assert out == "connection error\n"


def test_normal_exit(mock_get_args, mock_get_engine, mock_in_memory_history, mocker):
    mock_prompt = mocker.patch("dbcl.command_line.prompt", side_effect=EOFError)
    with pytest.raises(SystemExit) as excinfo:
        command_loop()

    assert excinfo.value.code == 0

    assert mock_prompt.called
    assert mock_get_args.called
    assert mock_get_engine.called
    assert mock_in_memory_history.called
