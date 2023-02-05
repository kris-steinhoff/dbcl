import pytest

from dbcl.command_line import prompt_for_command


def test_prompt_with_command(mocker):
    mock_process_command = mocker.patch("dbcl.command_line.process_command")
    mock_get_engine = mocker.patch("dbcl.command_line.get_engine")
    mock_print_result = mocker.patch("dbcl.command_line.print_result")
    mock_prompt = mocker.patch("dbcl.command_line.prompt")
    mock_prompt.return_value = "--/foo"

    prompt_for_command(None, mock_get_engine.return_value, None)

    assert not mock_get_engine.return_value.called
    assert mock_prompt.called
    assert not mock_print_result.called
    assert mock_process_command.called


def test_prompt_with_query(mocker):
    mock_process_command = mocker.patch("dbcl.command_line.process_command")
    mock_get_engine = mocker.patch("dbcl.command_line.get_engine")
    mock_print_result = mocker.patch("dbcl.command_line.print_result")
    mock_prompt = mocker.patch("dbcl.command_line.prompt")
    mock_prompt.return_value = "foo"

    prompt_for_command(None, mock_get_engine.return_value, None)

    assert mock_get_engine.return_value.execute.called
    assert mock_prompt.called
    assert mock_print_result.called
    assert not mock_process_command.called


def test_user_interupt(mocker):
    mock_prompt = mocker.patch(
        "dbcl.command_line.prompt", side_effect=KeyboardInterrupt
    )

    cmd = prompt_for_command(None, None, None)

    assert cmd is None
    assert mock_prompt.called


def test_user_eof(mocker):
    mock_prompt = mocker.patch("dbcl.command_line.prompt", side_effect=EOFError)

    with pytest.raises(SystemExit) as excinfo:
        prompt_for_command(None, None, None)

    assert excinfo.value.code == 0
    assert mock_prompt.called


def test_user_other_error(mocker, capsys):
    mock_prompt = mocker.patch(
        "dbcl.command_line.prompt", side_effect=Exception("test error")
    )

    cmd = prompt_for_command(None, None, None)

    out, err = capsys.readouterr()
    assert "test error" in out
    assert cmd is None
    assert mock_prompt.called
