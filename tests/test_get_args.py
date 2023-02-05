import pytest

from dbcl.command_line import get_args


@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)


@pytest.mark.parametrize("help_flag", ("-h", "--help"))
def test_help_flag(help_flag, mocker):
    mock_prompt = mocker.patch("dbcl.command_line.prompt")
    mock_getenv = mocker.patch("os.getenv")
    mock_prompt.return_value = "test_url_from_input"

    with pytest.raises(SystemExit) as excinfo:
        get_args([help_flag])

    assert excinfo.value.code == 0
    assert not mock_prompt.called
    assert not mock_getenv.called


def test_with_url_on_command_line(mocker):
    mock_prompt = mocker.patch("dbcl.command_line.prompt")
    mock_prompt.return_value = "test_url_from_input"

    args = get_args(["test_url_from_command_line"])

    assert not mock_prompt.called
    assert args.database_url == "test_url_from_command_line"


def test_no_args_with_input(mocker):
    mock_prompt = mocker.patch("dbcl.command_line.prompt")
    mock_prompt.return_value = "test_url_from_input"

    args = get_args([])

    mock_prompt.assert_called_with("Connect to []: ")
    assert args.database_url == "test_url_from_input"


@pytest.mark.parametrize(
    "exc,return_code",
    (
        (KeyboardInterrupt, 1),
        (EOFError, 0),
    ),
)
def test_no_args_with_user_cancel(exc, return_code, mocker):
    mock_prompt = mocker.patch("dbcl.command_line.prompt", side_effect=exc)
    with pytest.raises(SystemExit) as excinfo:
        get_args([])

    assert excinfo.value.code == return_code
    assert mock_prompt.called


@pytest.mark.parametrize(
    "user_input,url",
    (
        ("", "test_url_from_env"),
        ("test_url_from_input", "test_url_from_input"),
    ),
)
def test_no_args_with_url_in_env(user_input, url, mocker, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "test_url_from_env")
    mock_prompt = mocker.patch("dbcl.command_line.prompt")
    mock_prompt.return_value = user_input

    args = get_args([])

    mock_prompt.assert_called_with("Connect to [test_url_from_env]: ")
    assert args.database_url == url


def test_with_url_in_arg_and_env(mocker, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "test_url_from_env")
    mock_prompt = mocker.patch("dbcl.command_line.prompt")
    mock_prompt.return_value = "test_url_from_input"

    args = get_args(["test_url_from_command_line"])

    assert not mock_prompt.called
    assert args.database_url == "test_url_from_command_line"
