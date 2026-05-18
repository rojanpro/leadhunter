from app.services.optout import is_opt_out


def test_stop_opt_out():
    assert is_opt_out("Please STOP")
    assert is_opt_out("do not contact me again")
    assert not is_opt_out("Yes, send details")
