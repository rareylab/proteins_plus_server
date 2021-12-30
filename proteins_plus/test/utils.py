"""Utility functions used in unit tests"""
from django.test import RequestFactory, TestCase

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
