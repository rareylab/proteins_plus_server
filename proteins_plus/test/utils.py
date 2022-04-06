"""Utility functions used in unit tests"""
import subprocess
from pathlib import Path
from django.test import RequestFactory, TestCase

from proteins_plus import settings

from molecule_handler.models import Ligand, ElectronDensityMap


class PPlusTestCase(TestCase):
    """Global TestCase class to handle global setup and teardown"""

    def tearDown(self):
        """Make sure object associated files are deleted"""
        ElectronDensityMap.objects.all().delete()
        Ligand.objects.all().delete()


class MockRequest:  # pylint: disable=too-few-public-methods
    """Mock class for imitating basic request objects"""

    def __init__(self, data={}, query_params={}):
        """Constructor

        :param data: Request data, defaults to {}
        :type data: dict, optional
        :param query_params: Request query parameters, defaults to {}
        :type query_params: dict, optional
        """
        self.data = data
        self.query_params = query_params


def call_api(view_class, method, data={}, query_params={},
             viewset_actions=None, **req_kwargs):
    """Helper function for making calls to the api

    Examples

    POST to APIView:
    response = call_api(MyView, 'post', data)

    GET model from ReadOnlyModelViewSet:
    response = call_api(MyViewSet, 'get', viewset_actions={'get': 'retrieve'}, pk=model.id)


    :param view_class: View to send the api call to
    :type view_class: APIView or ViewSet
    :param method: Http method to use for the api call
    :type method: str
    :param data: Request data, defaults to {}
    :type data: dict, optional
    :param query_params: Request query parameters, defaults to {}
    :type query_params: dict, optional
    :param viewset_actions: Dictionary specifying the viewset actions that should be used
                            for the api call. Implies that view_class is a ViewSet, defaults to None
    :type viewset_actions: dict, optional
    :return: The response of the api call
    :rtype: HttpResponse
    """
    factory = RequestFactory()
    kwargs = {'data': data}

    req_string = '\?'  # pylint: disable=anomalous-backslash-in-string
    for key in query_params:
        req_string += key + '=' + str(query_params[key]) + '&'

    request = getattr(factory, method)(req_string, **kwargs)
    if viewset_actions is None:
        response = view_class.as_view()(request, *[], **req_kwargs)
    else:
        response = view_class.as_view(viewset_actions)(request, *[], **req_kwargs)
    return response


def is_tool_available(tool_name_key):
    """Calls the tool binary by command line and returns the return code or None if unavailable

    :param tool_name_key: name of the tool to check
    :type tool_name_key: str
    :return: Return code of the command line tool execution or None if tool not available.
    :rtype: int or None
    """
    path = Path(settings.BINARIES[tool_name_key])
    if not path.is_file():
        print(f'{tool_name_key} binary does not exist at {path}')
        return None
    completed_process = subprocess.run(
        path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    # 64 == ArgumentError, which means ready to accept arguments
    return completed_process.returncode
