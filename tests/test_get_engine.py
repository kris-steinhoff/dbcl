import pytest

from dbcl.command_line import get_engine


def test_get_engine(mocker):
    mock_args = mocker.MagicMock()
    mock_args.database_url = "test_db_url"
    mock_create_engine = mocker.patch("dbcl.command_line.create_engine")

    get_engine(mock_args)

    mock_create_engine.assert_called_with("test_db_url")


def test_get_engine_exception(mocker):
    mock_args = mocker.MagicMock()
    mock_args.database_url = "test_db_url"
    mock_create_engine = mocker.patch(
        "dbcl.command_line.create_engine", side_effect=Exception
    )

    with pytest.raises(SystemExit) as excinfo:
        get_engine(mock_args)

    assert excinfo.value.code == 1
    assert mock_create_engine.called
