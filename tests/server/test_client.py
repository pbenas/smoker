#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2007-2015, GoodData(R) Corporation. All rights reserved

import mock
import os
import pytest
import shutil
import smoker.client as smoker_client
import socket
from tests.server.smoker_test_resources import client_mock_result
from tests.server.smoker_test_resources.client_mock_result\
    import rest_api_response
from tests.server.smoker_test_resources.client_mock_result import TMP_DIR


class TestHost(object):
    """Unit tests for the client.Host class"""

    hostname = socket.gethostname()

    def test_create_host_instance(self):

        host = smoker_client.Host('%s:8086' % self.hostname)
        assert host.url == 'http://%s:8086' % self.hostname
        assert not host.links

        host = smoker_client.Host('%s' % self.hostname)
        assert host.url == 'http://%s:8086' % self.hostname
        assert not host.links

    @mock.patch('urllib2.urlopen', rest_api_response)
    def test_load_about(self):
        host = smoker_client.Host('%s:8086' % self.hostname)
        assert not host.links
        assert host.load_about() == client_mock_result.about_response
        assert host.links == client_mock_result.links
        assert host.name == client_mock_result.about_response['about']['host']

    @mock.patch('urllib2.urlopen', rest_api_response)
    def test_result_will_be_cleared_after_getting(self):
        host = smoker_client.Host('%s:8086' % self.hostname)
        host.load_about()
        assert host.get_result() == client_mock_result.about_response
        assert not host.get_result()

    @mock.patch('urllib2.urlopen', rest_api_response)
    def test_force_run(self):
        expected = client_mock_result.force_plugin_run_response
        host = smoker_client.Host('%s:8086' % self.hostname)
        host.load_about()
        plugins = {'Uname': dict()}
        assert host.force_run(plugins) == expected
        host.get_result() == expected

    @mock.patch('urllib2.urlopen', rest_api_response)
    def test_force_run_with_invalid_plugin_name(self):
        host = smoker_client.Host('%s:8086' % self.hostname)
        host.load_about()
        plugins = {'uname': dict()}
        assert host.force_run(plugins) is False
        assert host.get_result() == client_mock_result.about_response

    @mock.patch('urllib2.urlopen', rest_api_response)
    def test_load_about_before_open_resource(self):
        host = smoker_client.Host('%s:8086' % self.hostname)
        assert not host.open(resource='plugins')
        host.load_about()
        assert host.open(resource='plugins')

    @mock.patch('urllib2.urlopen', rest_api_response)
    def test_open_with_invalid_uri_and_resource(self):
        expected_exc = 'Argument uri or resource have to be submitted'
        host = smoker_client.Host('%s:8086' % self.hostname)
        host.load_about()
        assert not host.open(uri='/InvalidUri')
        assert not host.open(resource='InvalidResource')
        with pytest.raises(Exception) as exc_info:
            host.open()
        assert expected_exc in exc_info.value


class TestClient(object):
    """Unit tests for the client.Client class"""

    hostname = socket.gethostname()

    @mock.patch('urllib2.urlopen', rest_api_response)
    def test_create_client_instance(self):
        cli = smoker_client.Client(['%s:8086' % self.hostname])
        assert cli.hosts[0].load_about() == client_mock_result.about_response

    @mock.patch('urllib2.urlopen', rest_api_response)
    def test_get_plugins_with_filter_is_none(self):
        cli = smoker_client.Client(['%s:8086' % self.hostname])
        with pytest.raises(TypeError) as exc_info:
            cli.get_plugins()
        assert "'NoneType' object is not iterable" in exc_info.value

    @mock.patch('urllib2.urlopen', rest_api_response)
    def test_get_plugins(self):
        # Need confirm the format of filters. Look likes It doesn't work
        # filters = { 'Category': 'system'}
        # filters = ('Category', 'system')
        # filters = ['Uname', 'Uptime']
        cli = smoker_client.Client(['%s:8086' % self.hostname])
        result = cli.get_plugins(filters=list())
        assert self.hostname in result
        assert cli.hosts[0].load_about() == client_mock_result.about_response
        for x in ['Uname', 'Hostname', 'Uptime']:
            assert x in result[self.hostname]['plugins']
        result = cli.get_plugins(filters=list(), exclude_plugins=['Uname'])
        assert 'Hostname' and 'Uptime' in result[self.hostname]['plugins']
        assert 'Uname' not in result[self.hostname]['plugins']

    @mock.patch('urllib2.urlopen', rest_api_response)
    def test_open_with_invalid_uri_and_resource(self):
        cli = smoker_client.Client(['%s:8086' % self.hostname])
        expected_exc = 'Argument uri or resource have to be submitted'
        expected_response = client_mock_result.about_response
        assert cli.open(uri='/InvalidUri')[self.hostname] == expected_response
        cli.open(resource='InvalidResource') == expected_response
        with pytest.raises(Exception) as exc_info:
            cli.open()
        assert expected_exc in exc_info.value

    @mock.patch('urllib2.urlopen', rest_api_response)
    def test_force_run(self):
        cli = smoker_client.Client(['%s:8086' % self.hostname])
        plugins = cli.get_plugins(filters=list(),
                                  exclude_plugins=['Hostname', 'Uptime'])
        result = cli.force_run(plugins)[self.hostname]['plugins']
        assert 'Uname' in result
        assert 'Uptime' and 'Hostname' not in result
        assert 'forcedResult' in result['Uname']
        assert result['Uname']['forcedResult']['status'] == 'OK'
        assert result['Uname']['links']['self'] == '/plugins/Uname'


class TestCleanUp(object):
    """Clean up all temporary files used by Mock"""
    def test_clean_up(self):
        if os.path.exists(TMP_DIR):
            shutil.rmtree(TMP_DIR)
