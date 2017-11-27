# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from mock import (
    MagicMock,
    Mock
    )
import pytest
import requests
from aria_restservice_proxy import tasks
from cloudify.exceptions import NonRecoverableError
from cloudify.state import current_ctx
    
def test_noservice_with_wait(monkeypatch):
    node = Mock(properties = {'service_name': 'testwait',
                              'wait_config':{'wait_for_service': True, 'wait_time':5},
                              'outputs': ['someoutput'],
                              'aria_rest_url': 'http://127.0.0.1:5000',
                              'aria_rest_version': '0.1'
                             })

    attrs = {'retry.return_value' : 'retry' }
    operation = Mock( retry_number = 0, **attrs)
    ctxmock = MagicMock( node = node , operation = operation)
    current_ctx.set(ctxmock)
    monkeypatch.setattr(tasks,"get_services",lambda: [])
    ret = tasks.proxy_connect()
    assert(ret == 'retry')

def test_noservice_no_wait(monkeypatch):
    node = Mock(properties = {'service_name': 'testfail',
                              'wait_config':{'wait_for_service': False, 'wait_time':5 },
                              'outputs': ['someoutput']})
    ctxmock = MagicMock(node = node)
    current_ctx.set(ctxmock)
    monkeypatch.setattr(tasks,"get_services",lambda: [])
    with pytest.raises(NonRecoverableError):
        tasks.proxy_connect()
        
def test_service_eventual_complete(monkeypatch):
    node = Mock(properties = {'service_name': 'test',
                              'wait_config':{'wait_for_service': True, 'wait_time':1},
                              'outputs': ['someoutput'],
                              'aria_rest_url': 'http://127.0.0.1:5000',
                              'aria_rest_version': '0.1'
                              })
    instance = Mock(runtime_properties = {})
    attrs = {'retry.return_value' : 'retry' }
    operation = Mock( retry_number = 0, **attrs)
    ctxmock = MagicMock( node = node , operation = operation, instance = instance)
    current_ctx.set(ctxmock)

    attrs = {'json.return_value' : [{'name': 'test', 'id': 1}]}
    response = Mock(**attrs)
    monkeypatch.setattr(requests, "get", lambda _: response)
    monkeypatch.setattr(tasks, "get_outputs", lambda a,b: [])

    ret = tasks.proxy_connect()
    assert(ret == 'retry')

    attrs = {'json.return_value' : [{'name': 'test', 'id': 1}]}
    response = Mock(**attrs)
    monkeypatch.setattr(requests, "get", lambda _: response)
    monkeypatch.setattr(tasks, "get_outputs", lambda a,b: [{'someoutput':'someval'}])
    ret = tasks.proxy_connect()
    assert(ret == None)
    assert(len(ctxmock.instance.runtime_properties['service_outputs']) == 1)
    assert(ctxmock.instance.runtime_properties['service_outputs'][0]['someoutput'] == 'someval')

def test_output_retry(monkeypatch):
  
    node = Mock(properties = {'service_name': 'test',
                              'wait_config':{'wait_for_service': True, 'wait_time':5},
                              'aria_rest_url': 'http://127.0.0.1:5000',
                              'aria_rest_version': '0.1',
                              'outputs': ['someoutput']})
    attrs = {'retry.return_value' : 'retry' }
    operation = Mock( retry_number = 0, **attrs)
    ctxmock = MagicMock( node = node , operation = operation)
    current_ctx.set(ctxmock)
    monkeypatch.setattr(tasks, "get_services", lambda: [{'name':'test','id':1}])
    monkeypatch.setattr(tasks, "get_outputs", lambda a,b: [{'test':'someval'}])

    ret = tasks.proxy_connect()
    assert(ret == 'retry')

def test_output_complete(monkeypatch):
    node = Mock(properties = {'service_name': 'test',
                              'wait_config':{'wait_for_service': True, 'wait_time':5},
                              'outputs': ['someoutput']})
    attrs = {'retry.return_value' : 'retry' }
    operation = Mock( retry_number = 5, **attrs)
    ctxmock = MagicMock( node = node , operation = operation)
    current_ctx.set(ctxmock)
    monkeypatch.setattr(tasks, "get_services", lambda: [{'name':'test','id':1}])
    monkeypatch.setattr(tasks, "get_outputs", lambda a,b: [{'someoutput':'someval'}])

    ret = tasks.proxy_connect()
    assert(ret == None)

def test_output_complete(monkeypatch):
    node = Mock(properties = {'service_name': 'test',
                              'wait_config':{'wait_for_service': True, 'wait_time':5},
                              'outputs': ['someoutput']})
    attrs = {'retry.return_value' : 'retry' }
    operation = Mock( retry_number = 5, **attrs)
    ctxmock = MagicMock( node = node , operation = operation)
    current_ctx.set(ctxmock)
    monkeypatch.setattr(tasks, "get_services", lambda: [{'name':'test','id':1}])
    monkeypatch.setattr(tasks, "get_outputs", lambda a,b: [{'someoutput':'someval'}])

    ret = tasks.proxy_connect()
    assert(ret == None)

def test_output_complete(monkeypatch):
    node = Mock(properties = {'service_name': 'test',
                              'wait_config':{'wait_for_service': True, 'wait_time':5},
                              'outputs': ['someoutput']})
    instance = Mock(runtime_properties = {})
    attrs = {'retry.return_value' : 'retry' }
    operation = Mock( retry_number = 5, **attrs)
    ctxmock = MagicMock( node = node , operation = operation, instance = instance)
    current_ctx.set(ctxmock)
    monkeypatch.setattr(tasks, "get_services", lambda: [{'name':'test','id':1}])
    monkeypatch.setattr(tasks, "get_outputs", lambda a,b: [{'someoutput':'someval'}])

    ret = tasks.proxy_connect()
    assert(ret == None)
    assert(len(ctxmock.instance.runtime_properties['service_outputs']) == 1)
    assert(ctxmock.instance.runtime_properties['service_outputs'][0]['someoutput'] == 'someval')

def test_output_eventual_complete(monkeypatch):
    node = Mock(properties = {'service_name': 'test',
                              'wait_config':{'wait_for_service': True, 'wait_time':1},
                              'outputs': ['someoutput']})
    attrs = {'retry.return_value' : 'retry' }
    instance = Mock(runtime_properties = {})
    operation = Mock( retry_number = 0, **attrs)
    ctxmock = MagicMock( node = node , operation = operation, instance = instance)
    current_ctx.set(ctxmock)
    monkeypatch.setattr(tasks, "get_services", lambda: [{'name':'test','id':1}])
    monkeypatch.setattr(tasks, "get_outputs", lambda a,b: [])

    ret = tasks.proxy_connect()
    assert(ret == 'retry')

    monkeypatch.setattr(tasks, "get_outputs", lambda a,b: [{'someoutput':'someval'}])
    ret = tasks.proxy_connect()
    assert(ret == None)
    assert(len(ctxmock.instance.runtime_properties['service_outputs']) == 1)
    assert(ctxmock.instance.runtime_properties['service_outputs'][0]['someoutput'] == 'someval')
