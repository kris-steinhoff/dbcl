import pytest

from dbcl.command_line import process_command, _command_prefix, NoSuchTableError


@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)


@pytest.mark.parametrize(
    "command",
    ("%s%s" % (_command_prefix, cmd) for cmd in ("comand_nope", "command_wrong")),
)
def test_bad_command(command, capsys):
    process_command(command, None, None)

    out, err = capsys.readouterr()
    assert out.startswith("Bad command")


info_too_many = [
    "%s%s" % (_command_prefix, cmd)
    for cmd in ["info too many", "info way too many args"]
]


def test_info_no_args(mocker, capsys):
    mock_args = mocker.MagicMock()
    mock_args.database_url = "test_db_url"
    mock_metadata = mocker.patch("dbcl.command_line.MetaData")

    process_command("%sinfo" % _command_prefix, None, mock_args)

    assert mock_metadata.return_value.reflect.called
    out, err = capsys.readouterr()
    assert "Database URL" in out
    assert "Tables" in out


def test_info_one_arg(mocker, capsys):
    mock_args = mocker.MagicMock()
    mock_args.database_url = "test_db_url"
    mock_table = mocker.patch("dbcl.command_line.Table")
    mock_table.return_value.columns = [mocker.MagicMock()]
    mock_print_data = mocker.patch("dbcl.command_line.print_data")

    process_command("%sinfo table_name" % _command_prefix, None, mock_args)

    assert mock_table.called
    assert mock_print_data.called


def test_info_missing_table(mocker, capsys):
    mock_args = mocker.MagicMock()
    mock_args.database_url = "test_db_url"
    mock_table = mocker.patch("dbcl.command_line.Table", side_effect=NoSuchTableError)
    mock_print_data = mocker.patch("dbcl.command_line.print_data")

    process_command("%sinfo table_name" % _command_prefix, None, mock_args)

    assert mock_table.called
    assert not mock_print_data.called
    out, err = capsys.readouterr()
    assert out.startswith("No such table")


def test_exit_no_args(mocker, capsys):
    mock_args = mocker.MagicMock()
    mock_args.database_url = "test_db_url"
    mock_metadata = mocker.patch("dbcl.command_line.MetaData")

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        process_command("%sexit" % _command_prefix, None, mock_args)
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 0


def test_quit_no_args(mocker, capsys):
    mock_args = mocker.MagicMock()
    mock_args.database_url = "test_db_url"
    mock_metadata = mocker.patch("dbcl.command_line.MetaData")

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        process_command("%squit" % _command_prefix, None, mock_args)
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 0


@pytest.mark.parametrize(
    "command",
    (
        "%s%s" % (_command_prefix, cmd)
        for cmd in ("info too many", "info way too many args")
    ),
)
def test_info_too_many_args(command, capsys):
    process_command(command, None, None)

    out, err = capsys.readouterr()
    assert out.startswith("usage: ")
