import cfnresponse
import boto3

import logging as log

log.getLogger().setLevel(log.INFO)

# Note, there is a tight coupling between this name and what's in the todo_service_stack.
PHYSICAL_ID = 'ENIPrivateIPResource'


def main_handler(event, context):
    log.info('Input event: %s', event)
    request_type = event['RequestType']

    if request_type == 'Delete':
        log.info("Executing Delete of custom resource")
        cfnresponse.send(event, context, cfnresponse.SUCCESS, {})
    elif request_type in ('Create', 'Update'):
        log.info(f"Executing {request_type} of custom resource")
        result, response_data = _handle_create(event, context)
        log.info(response_data)
        cfnresponse.send(event, context, result, response_data, PHYSICAL_ID)


def _handle_create(event, context):
    response_data = {}

    try:
        enis = event['ResourceProperties']['vpce_enis']

        ec2 = boto3.resource('ec2')

        ips = []

        for i, eni in enumerate(enis):
            network_interface = ec2.NetworkInterface(eni)
            response_data[f"IP{str(i)}"] = network_interface.private_ip_address
            ips.append(network_interface.private_ip_address)

        response_data["IPS"] = ips

        return (cfnresponse.SUCCESS, response_data)
    except Exception as e:
        log.error('Error fetching Network Interfaces')
        log.error(e)
        response_data = {'error': str(e)}

        return (cfnresponse.FAILED, response_data)
