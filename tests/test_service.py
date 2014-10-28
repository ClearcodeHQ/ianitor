# -*- coding: utf-8 -*-
from time import sleep
import mock

from ianitor import service
from consul import Consul


def get_tailf_service(session):
    return service.Service(
        ["tailf", "/dev/null"],
        session=session,
        service_name="tailf",
        # small ttl for faster testing
        ttl=1,
    )


def test_service_start():
    session = Consul()
    tailf = get_tailf_service(session)

    with mock.patch.object(service.Service, "register") as register_method:
        tailf.start()

        assert bool(tailf.is_up())
        register_method.assert_any_call()


def test_is_up_false_if_not_started():
    session = Consul()
    tailf = get_tailf_service(session)

    assert not tailf.is_up()


def test_remove_services():
    """
    ~ Yo dawg I herd that you like tests so we put test inside your test so
      you can test while you test

    Note: this is not a tests of `ianitor` but a tests helper. Still we must be
    sure that this helper works so we test it.
    """
    session = Consul()
    agent = session.agent

    services = agent.services()

    for srv, description in services.items():
        if description["ID"] != 'consul':
            agent.service.deregister(description["ID"])

    # this is consul 0.4.1 behavior - consul is one of services
    services = agent.services()
    if 'consul' in services:
        services.pop('consul')

    assert not services


def test_service_register():
    session = Consul()
    agent = session.agent

    tailf = get_tailf_service(session)
    tailf.start()

    test_remove_services()
    tailf.register()

    assert agent.services()


def test_deregister():
    session = Consul()
    agent = session.agent

    tailf = get_tailf_service(session)
    tailf.start()

    test_remove_services()
    tailf.register()
    tailf.deregister()

    # this is consul 0.4.1 behavior - consul is one of services
    services = agent.services()
    if 'consul' in services:
        services.pop('consul')
    assert not services


def test_kill():
    test_remove_services()

    session = Consul()
    agent = session.agent

    tailf = get_tailf_service(session)

    # test service registered after start
    tailf.start()
    assert agent.services()

    # and deregistered after restart
    with mock.patch.object(service.Service, "deregister") as r:
        tailf.kill()
        r.assert_any_call()


def _get_service_status(session, service_obj):
    _, check_response = session.health.service(service_obj.service_name)

    try:
        checks = check_response[0]["Checks"]
    except IndexError:
        # return none because check does not even exist
        return

    # from pprint import pprint; pprint(checks)
    service_check = list(filter(
        lambda check: check["ServiceName"] == service_obj.service_name, checks
    )).pop()

    return service_check["Status"]


def test_keep_alive():
    """
    Integration test for keeping service alive in consul cluster
    """
    test_remove_services()
    session = Consul()
    tailf = get_tailf_service(session)

    # assert that there is no checks yet
    _, checks = session.health.service(tailf.service_name)
    assert not checks

    # test that service health check is unknown or critical after registration
    tailf.register()
    # small sleep for cluster consensus
    sleep(0.1)
    assert _get_service_status(session, tailf) in ("unknown", "critical")

    # assert service is healthy back again after keep alive
    tailf.keep_alive()
    sleep(0.1)
    assert _get_service_status(session, tailf) == "passing"

    # assert service health check fails after ttl passed
    sleep(tailf.ttl + 0.5)
    assert _get_service_status(session, tailf) == "critical"


def test_keepalive_reregister():
    """
    Integration test that keep-alive registers service again if it disapears
    """
    test_remove_services()
    session = Consul()
    tailf = get_tailf_service(session)

    # [integration] assert service is healthy
    tailf.register()
    tailf.keep_alive()
    sleep(0.1)
    assert _get_service_status(session, tailf) == "passing"

    # [integration] assert that check
    test_remove_services()
    assert _get_service_status(session, tailf) is None

    # [integration] assert that keepalive makes service registered again
    tailf.keep_alive()
    sleep(0.1)
    assert _get_service_status(session, tailf) == "passing"


def test_ignore_connection_failures():
    session = Consul(host="invalid")

    tailf = get_tailf_service(session)

    # assert service starts
    tailf.start()
    assert tailf.process.poll() is None

    with mock.patch('ianitor.service.logger') as logger:
        tailf.register()
        assert logger.error.called

    with mock.patch('ianitor.service.logger') as logger:
        tailf.keep_alive()
        assert logger.error.called

    with mock.patch('ianitor.service.logger') as logger:
        tailf.deregister()
        assert logger.error.called

    tailf.deregister()

    # assert service can be killed
    tailf.kill()
    tailf.process.wait()
