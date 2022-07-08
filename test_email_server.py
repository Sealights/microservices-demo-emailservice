import pytest as pytest

from demo_pb2 import SendOrderConfirmationRequest, Empty

@pytest.fixture(scope='module')
def grpc_add_to_server():
    from demo_pb2_grpc import add_EmailServiceServicer_to_server
    return add_EmailServiceServicer_to_server


@pytest.fixture(scope='module')
def grpc_servicer(module_mocker):
    module_mocker.patch("init_tracing.init_tracer_provider")
    from email_server import DummyEmailService
    return DummyEmailService()


@pytest.fixture(scope='module')
def grpc_stub(grpc_channel):
    from demo_pb2_grpc import EmailServiceStub
    return EmailServiceStub(grpc_channel)


# def test_SendOrderConfirmation(grpc_stub):
#     send_order_confirmation_request = SendOrderConfirmationRequest(email='john.doe@gmail.com')
#     response = grpc_stub.SendOrderConfirmation(send_order_confirmation_request)

#     assert isinstance(response, Empty)

def test_dump():
    assert 1 == 1

    
