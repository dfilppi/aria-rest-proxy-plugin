# Copyright (c) 2017 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

from cloudify.decorators import operation
from cloudify import ctx
from cloudify.exceptions import NonRecoverableError
from subprocess import Popen
from subprocess import PIPE
from datetime import datetime
import time
import re

@operation
def proxy_connect(**kwargs):

    ctx.logger.info("entering proxy connect")

    service_names = get_service_names()

    duration = ctx.node.properties['wait_config']['wait_time']

    service_exists = ctx.node.properties['service_name'] in service_names

    wait_for_service =  ctx.node.properties['wait_config']['wait_for_service']

    if not service_exists:
        if wait_for_service:
            if duration > ctx.operation.retry_number:
                return ctx.operation.retry(message = 'Waiting for service to exist', retry_after=1)
            else:
                raise NonRecoverableError("service {} not found".format(ctx.node.properties['service_name']))
        else:
            raise NonRecoverableError("service {} not found".format(ctx.node.properties['service_name']))

    # Service exists, so see if outputs exist yet
    else:
        outputs = get_outputs(ctx.node.properties['service_name'], ctx.node.properties['outputs'])
        if not output_equivalence( ctx.node.properties['outputs'], outputs):
            if wait_for_service:
                if duration > ctx.operation.retry_number:
                    return ctx.operation.retry(message = 'Waiting for service outputs', retry_after=1)
                else:
                    raise NonRecoverableError("service {} outputs not found".format(ctx.node.properties['service_name']))
            else:
                raise NonRecoverableError("service {} outputs {} not found".format(ctx.node.properties['service_name'], ctx.node.properties['outputs']))

        else:
            # Success
            # place outputs in attributes
            if 'service_outputs' not in ctx.instance.runtime_properties:
                ctx.instance.runtime_properties['service_outputs'] = []
            for output in outputs:
                ctx.instance.runtime_properties['service_outputs'].append(output)
           
            ctx.instance.runtime_properties['last_update'] = str(datetime.utcnow())

        
# returns service names from ARIA CLI
def get_service_names():

    p1 = Popen(["aria", "services","list"], stdout = PIPE)
    p2 = Popen(["grep", "[0-9]"], stdin = p1.stdout, stdout = PIPE )
    p3 = Popen(["awk", "{print $4}"], stdin = p2.stdout, stdout = PIPE )
    service_names = p3.communicate()[0].splitlines()
    p3.wait()
    return service_names

# parses service outputs and returns as list of dicts
def get_outputs( service, output_list ):
    p = Popen(["aria","services","outputs",service], stdout = PIPE)
    outputar = p.communicate()[0].splitlines()

    if outputar[1].lstrip() == "No outputs":
      return {}

    outputs = []
    for n in range(1,len(outputar)-1,3):
        output_name = re.search('[^a-zA-Z]*([a-zA-Z][^":]*).*',outputar[n]).group(1)
        if output_name in output_list:
            val = re.search('[\s]*Value:[\s]*(.*)',outputar[n+2]).group(1)
            outputs.append( dict([(output_name,val)]))
    return outputs

# Tests whether the list of configured outputs (a simple string list) is equivalent
# to the list returned from Aria (possible duplicate keys)
def output_equivalence( config_list, service_list ):
        
    sset = set()
    for output in service_list:
        for k,v in output.iteritems():
            sset.add( k )

    if not len(sset) == len(config_list):
        return False

    for entry in sset:
        if not entry in config_list:
            return False

    return True


