from __future__ import absolute_import
from flask_restful import Resource, current_app, fields, marshal_with
from . import rest_api
import requests

VNET_PATH_LIST = "/virtual-networks"
VNET_PATH_ID = "/virtual-network/%s"
VM_PATH_LIST = "/virtual-machines"
VM_PATH_ID = "/virtual-machine/%s"

VNC_LIST_FIELDS = {
    "id": fields.String(attribute="name"),
}

VNC_VNET_INSTANCE_FIELDS = {
    "": fields.String(attribute="uuid"),
    "fq_name": fields.String,
    "name": fields.String,
}

VNC_SERVICE_VMS = {
    "id": fields.String(attribute="uuid"),
}

VNC_VNET_VMS = {
    "id": fields.String,
}

VNC_POLICY_FIELDS = {
    "id": fields.String(attribute="uuid"),
    "fq_name": fields.String
}


def filter_tenant(list, tenant):
    return [item for item in list
            if len(item["name"].split(':')) > 1 and
            item["name"].split(':')[1] == tenant]


class VNC(Resource):
    def get_vnets(self, tenant_id):
        url = current_app.config["ANALYTICS_URL"] + "/virtual-networks"
        vnets = requests.get(url).json()
        return filter_tenant(vnets, tenant_id)

    def get_vnet(self, id):
        url = current_app.config["ANALYTICS_URL"] + "/virtual-network/" + id\
            + "?flat"
        vnet = requests.get(url).json()
        return vnet

    def get_vnet_vms(self, vnetid):
        vnet = self.get_vnet(vnetid)
        vms = []
        try:
            vm_list = vnet['UveVirtualNetworkAgent']['virtualmachine_list']
            vms = [dict([("id", vm)]) for vm in vm_list]
            return vms
        except Exception, e:
            print e
        return vms

    def get_vm(self, id):
        url = current_app.config["ANALYTICS_URL"] + "/virtual-machine/" + id\
            + "?flat"
        vm = requests.get(url).json()
        return vm

    def get_services(self, tenant_id):
        url = current_app.config["ANALYTICS_URL"] + "/service-instances"
        services = requests.get(url).json()
        return filter_tenant(services, tenant_id)

    def get_service(self, id):
        url = current_app.config["ANALYTICS_URL"] + "/service-instance/" + id\
            + "?flat"
        service = requests.get(url).json()
        return service

    def get_service_vms(self, serviceid):
        service = self.get_service(serviceid)
        try:
            vms = service['UveSvcInstanceConfig']['vm_list']
            return vms
        except:
            pass
        return []


class VNetList(VNC):
    @marshal_with(VNC_LIST_FIELDS)
    def get(self):
        return self.get_vnets(current_app.config["OS_TENANT_NAME"])


class VNetInstance(VNC):
    # @marshal_with(VNC_VNET_INSTANCE_FIELDS)
    def get(self, id):
        return self.get_vnet(id)


class VNetVMList(VNC):
    @marshal_with(VNC_VNET_VMS)
    def get(self, vnetid):
        return self.get_vnet_vms(vnetid)


class VNetVMInstance(VNC):
    # @marshal_with(VNC_VMS_INSTANCE_FIELDS)
    def get(self, vnetid, id):
        return self.get_vm(id)


class ServiceList(VNC):
    @marshal_with(VNC_LIST_FIELDS)
    def get(self):
        return self.get_services(current_app.config["OS_TENANT_NAME"])


class ServiceInstance(VNC):
    # @marshal_with(VNC_VNET_INSTANCE_FIELDS)
    def get(self, id):
        return self.get_service(id)


class ServiceInstanceVMList(VNC):
    @marshal_with(VNC_SERVICE_VMS)
    def get(self, serviceid):
        return self.get_service_vms(serviceid)


class ServiceInstanceVM(VNC):
    # @marshal_with(VNC_VNET_INSTANCE_FIELDS)
    def get(self, serviceid, id):
        return self.get_vm(id)


class VMInstance(VNC):
    # @marshal_with(VNC_VMS_INSTANCE_FIELDS)
    def get(self, id):
        return self.get_vm(id)


class PolicyResources(Resource):
    # @marshal_with(VNC_POLICY_FIELDS)
    def getPolicy(self, id):
        return requests.get(
            'http://'+current_app.config['OS_SERVER']+':8082/network-policy/'+id).json()

    def get(self):
        policies = current_app.vnc_lib.network_policys_list()
        res_pol = []
        for p in policies['network-policys']:
            if p['fq_name'][1] == current_app.config["OS_TENANT_NAME"]:
                res_pol.append(self.getPolicy(p['uuid']))
        return res_pol


rest_api.add_resource(VNetList, '/vnets')
rest_api.add_resource(VNetInstance, '/vnets/<string:id>')
rest_api.add_resource(VNetVMList, '/vnets/<string:vnetid>/vms')
rest_api.add_resource(VNetVMInstance, '/vnets/<string:vnetid>/vms/<string:id>')
rest_api.add_resource(ServiceList, '/services')
rest_api.add_resource(ServiceInstance, '/services/<string:id>')
rest_api.add_resource(ServiceInstanceVMList,
                      '/services/<string:serviceid>/vms')
rest_api.add_resource(ServiceInstanceVM,
                      '/services/<string:serviceid>/vms/<string:id>')
rest_api.add_resource(VMInstance, '/vms/<string:id>')

rest_api.add_resource(PolicyResources, '/policies')
