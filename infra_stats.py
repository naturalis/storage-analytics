#!/usr/bin/python2.7
# Import all required libraries
import json
from datetime import date, timedelta, datetime
from time import gmtime, strftime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from lib import es
from utils import config


# Support cost
# TODO: Ask OpenStack API / Fuel about the current number of nodes
# (and possibly some other facts)
# TODO: Determine the number of storage nodes, compute nodes and management
# nodes
def get_number_of_nodes():
    """
    Calculate the number of nodes for:
    * Storage
    * Compute
    And put the results in the stats dictionary
    """
    nodes_controller = 0.0
    nodes_storage_bruto = 0.0
    nodes_compute_bruto = 0.0

    for key, value in hardware.iteritems():
        if value['status'] == 'production':
            if value['role'] == 'ceph-osd':
                nodes_storage_bruto += 1.0
            elif value['role'] == 'compute':
                nodes_compute_bruto += 1.0
            elif value['role'] == 'controller':
                nodes_controller += 1.0

    # Make these variables available to other functions
    global nodes_storage
    global nodes_compute
    global nodes_total
    nodes_total = nodes_controller + nodes_storage_bruto + nodes_compute_bruto
    nodes_storage = nodes_controller * (
                    nodes_storage_bruto /
                    (nodes_storage_bruto + nodes_compute_bruto)
                    ) + nodes_storage_bruto
    nodes_compute = nodes_controller * (
                    nodes_compute_bruto /
                    (nodes_storage_bruto + nodes_compute_bruto)
                    ) + nodes_compute_bruto

    stats['nodes_total'] = nodes_total
    stats['nodes_controller'] = nodes_controller
    stats['nodes_storage_bruto'] = nodes_storage_bruto
    stats['nodes_compute_bruto'] = nodes_compute_bruto
    stats['nodes_storage'] = nodes_storage
    stats['nodes_compute'] = nodes_compute


def get_cost_support_internal():
    """
    Calculate the daily cost for internal support for:
    * Storage
    * Compute
    And put the results in the stats dictionary
    """
    support_internal_fte = float(facts['support_internal_fte']['value'])

    support_internal_labor_cost_per_fte = \
        float(facts['support_internal_labor_cost_per_fte']['value'])

    support_internal_storage_weight = \
        float(facts['support_internal_storage_weight']['value'])

    support_internal_compute_weight = \
        float(facts['support_internal_compute_weight']['value'])

    if 'nodes_total' not in globals():
        get_number_of_nodes()

    """Calculate daily internal support cost based on relative amount of time
    needed for storage"""
    global cost_support_internal_storage
    global cost_support_internal_compute

    cost_support_internal_total = (
        support_internal_fte *
        support_internal_labor_cost_per_fte /
        365
    )

    # TODO: candidate for a more generic, pure function
    cost_support_internal_storage = (
        cost_support_internal_total *
        (nodes_storage * support_internal_storage_weight) /
        (
            (nodes_storage * support_internal_storage_weight) +
            (nodes_compute * support_internal_compute_weight)
        )
    )

    cost_support_internal_compute = (
        cost_support_internal_total *
        (nodes_compute * support_internal_compute_weight) /
        (
            (nodes_storage * support_internal_storage_weight) +
            (nodes_compute * support_internal_compute_weight)
        )
    )

    stats['cost_support_internal_total'] = cost_support_internal_total
    stats['cost_support_internal_storage'] = cost_support_internal_storage
    stats['cost_support_internal_compute'] = cost_support_internal_compute


def get_cost_support_external():
    """
    Calculate the daily cost for external support for:
    * Storage
    * Compute
    And put the results in the stats dictionary
    """
    support_external_per_node = (
        float(facts['support_external_per_node']['value'])
    )

    if 'nodes_total' not in globals():
        get_number_of_nodes()

    # Calculate the daily external support cost
    global cost_support_external_storage
    global cost_support_external_compute

    cost_support_external_total = (
        nodes_total *
        support_external_per_node /
        365
    )

    cost_support_external_storage = (
        nodes_storage *
        support_external_per_node /
        365
    )

    cost_support_external_compute = (
        nodes_compute *
        support_external_per_node /
        365
    )

    stats['cost_support_external_total'] = cost_support_external_total
    stats['cost_support_external_storage'] = cost_support_external_storage
    stats['cost_support_external_compute'] = cost_support_external_compute


def get_cost_dc_rackspace():
    """
    Calculate the daily cost for rackspace for:
    * Storage
    * Compute
    And put the results in the stats dictionary
    """
    dc_rackspace_per_rack = float(facts['dc_rackspace_per_rack']['value'])

    dc_rackspace_racks = float(facts['dc_rackspace_racks']['value'])

    dc_rackspace_rack_units = float(facts['dc_rackspace_rack_units']['value'])

    dc_rackspace_units_storage_bruto = 0.0
    dc_rackspace_units_compute_bruto = 0.0
    dc_rackspace_units_management = 0.0

    for key, value in hardware.iteritems():
        if value['status'] == 'production' and type(value["units"]) is int:
            if value['role'] == 'ceph-osd':
                dc_rackspace_units_storage_bruto += float(value['units'])
            elif value['role'] == 'compute':
                dc_rackspace_units_compute_bruto += float(value['units'])
            else:
                dc_rackspace_units_management += float(value['units'])

    # Divide the units used for management proportionally over storage and
    # compute units
    dc_rackspace_units_storage = (
        dc_rackspace_units_management *
        (
            dc_rackspace_units_storage_bruto /
            (
                dc_rackspace_units_storage_bruto +
                dc_rackspace_units_compute_bruto
            )
        ) +
        dc_rackspace_units_storage_bruto
    )

    dc_rackspace_units_compute = (
        dc_rackspace_units_management *
        (
            dc_rackspace_units_compute_bruto /
            (
                dc_rackspace_units_storage_bruto +
                dc_rackspace_units_compute_bruto
            )
        ) +
        dc_rackspace_units_compute_bruto
    )

    global cost_dc_rackspace_storage
    global cost_dc_rackspace_compute

    cost_dc_rackspace_total = (
        dc_rackspace_per_rack *
        dc_rackspace_racks /
        365
    )

    cost_dc_rackspace_storage = (
        cost_dc_rackspace_total *
        (
            dc_rackspace_units_storage /
            (
                dc_rackspace_units_storage +
                dc_rackspace_units_compute
            )
        )
    )

    cost_dc_rackspace_compute = (
        cost_dc_rackspace_total *
        (
            dc_rackspace_units_compute /
            (
                dc_rackspace_units_storage +
                dc_rackspace_units_compute
            )
        )
    )

    dc_rackspace_units_total_used = (
        dc_rackspace_units_storage_bruto +
        dc_rackspace_units_compute_bruto +
        dc_rackspace_units_management
    )

    dc_rackspace_units_total_available = (
        dc_rackspace_rack_units *
        dc_rackspace_racks
    )

    stats['dc_rackspace_units_total_used'] = dc_rackspace_units_total_used
    stats['dc_rackspace_units_total_available'] = dc_rackspace_units_total_available
    stats['dc_rackspace_units_storage_bruto'] = dc_rackspace_units_storage_bruto
    stats['dc_rackspace_units_compute_bruto'] = dc_rackspace_units_compute_bruto
    stats['dc_rackspace_units_management'] = dc_rackspace_units_management
    stats['cost_dc_rackspace_total'] = cost_dc_rackspace_total
    stats['cost_dc_rackspace_storage'] = cost_dc_rackspace_storage
    stats['cost_dc_rackspace_compute'] = cost_dc_rackspace_compute


# TODO: Calculate power cost
# Get the datacenter power cost
def get_cost_dc_power():
    dc_electricity_per_kwh = float(
        facts['dc_electricity_per_kwh']['value']
    )

    power_per_server = float(facts['power_per_server']['value'])
    power_per_disk = float(facts['power_per_disk']['value'])

    # Get the number of disks for all storage servers
    number_of_disks = 6.0

    # Calculate the power cost for storage
    power_storage_bruto = 0.0
    power_compute_bruto = 0.0
    power_management = 0.0

    for key, value in hardware.iteritems():
        if value['status'] == 'production':
            if value['role'] == 'ceph-osd':
                power_storage_bruto += (
                    power_per_server +
                    (number_of_disks * power_per_disk)
                ) * 24 / 1000 * dc_electricity_per_kwh
            elif value['role'] == 'compute':
                power_compute_bruto += (
                    power_per_server +
                    (number_of_disks * power_per_disk)
                ) * 24 / 1000 * dc_electricity_per_kwh
            else:
                power_management += (
                    power_per_server +
                    (number_of_disks * power_per_disk)
                ) * 24 / 1000 * dc_electricity_per_kwh

    global cost_dc_power_storage
    global cost_dc_power_compute

    # Divide the power used for management proportionally over storage and
    # compute power costs
    cost_dc_power_storage = (
        power_management *
        (
            power_storage_bruto /
            (
                power_storage_bruto +
                power_compute_bruto
            )
        ) +
        power_storage_bruto
    )

    cost_dc_power_compute = (
        power_management *
        (
            power_compute_bruto /
            (
                power_storage_bruto +
                power_compute_bruto
            )
        ) +
        power_compute_bruto
    )

    cost_dc_power_total = (
        cost_dc_power_storage +
        cost_dc_power_compute
    )

    stats['cost_dc_power_total'] = cost_dc_power_total
    stats['cost_dc_power_storage'] = cost_dc_power_storage
    stats['cost_dc_power_compute'] = cost_dc_power_compute


def get_cost_hardware():
    hardware_storage_bruto = 0.0
    hardware_compute_bruto = 0.0
    hardware_management = 0.0

    for key, value in hardware.iteritems():
        if value["purchase_date"] != "" and type(value["purchase_price"]) is int:
            purchase_date = datetime.strptime(value["purchase_date"], '%d-%m-%Y').date()
            writeoff_date = purchase_date + writeoff_time
            if writeoff_date > date.today():
                if value["role"] == 'ceph-osd':
                    hardware_storage_bruto += value["purchase_price"] / writeoff_time.days
                elif value["role"] == 'compute':
                    hardware_compute_bruto += value["purchase_price"] / writeoff_time.days
                else:
                    hardware_management += value["purchase_price"] / writeoff_time.days

    global cost_hardware_storage
    global cost_hardware_compute

    # Divide the hardware costsfor management proportionally over storage and
    # compute hardware costs
    cost_hardware_storage = (
        hardware_management *
        (
            hardware_storage_bruto /
            (
                hardware_storage_bruto +
                hardware_compute_bruto
            )
        ) +
        hardware_storage_bruto
    )

    cost_hardware_compute = (
        hardware_management *
        (
            hardware_compute_bruto /
            (
                hardware_storage_bruto +
                hardware_compute_bruto
            )
        ) +
        hardware_compute_bruto
    )

    cost_hardware_total = cost_hardware_storage + cost_hardware_compute

    stats['cost_hardware_total'] = cost_hardware_total
    stats['cost_hardware_storage'] = cost_hardware_storage
    stats['cost_hardware_compute'] = cost_hardware_compute


def get_cost_total():
    get_cost_support_internal()
    get_cost_support_external()
    get_cost_dc_rackspace()
    get_cost_dc_power()
    get_cost_hardware()

    global cost_total_storage
    global cost_total_compute

    cost_total_storage = (
        cost_support_internal_storage +
        cost_support_external_storage +
        cost_dc_rackspace_storage +
        cost_dc_power_storage +
        cost_hardware_storage
    )

    cost_total_compute = (
        cost_support_internal_compute +
        cost_support_external_compute +
        cost_dc_rackspace_compute +
        cost_dc_power_compute +
        cost_hardware_compute
    )

    cost_total = cost_total_storage + cost_total_compute

    stats['cost_total'] = cost_total
    stats['cost_total_storage'] = cost_total_storage
    stats['cost_total_compute'] = cost_total_compute

# # Benefits / usage
# results = es.get_latest_stats("parsefailure-*", 2, "beat.name", "logging-rsyslog-001")
#
# ## Determine total bruto storage
# ## Query ES for the latest values for all bruto local storage
# ## (basically OpenStack and Ceph)
# storage_raw_stats = es.get_latest_stats("storage_type", "raw", "storage_location")
# storage_size_total = 0
# for key, value in storage_raw_stats.iteritems():
#     storage_size_total += value['storage_size']


def get_storage_size_bruto():
    global storage_size_bruto_ssd
    global storage_size_bruto_hdd
    global storage_size_bruto_total

    storage_size_bruto_total = 0.0
    storage_size_bruto_ssd = 0.0
    storage_size_bruto_hdd = 0.0

    for key, value in hardware.iteritems():
        if type(value["disk_ssd"]) is int and value['status'] != 'discarded':
            storage_size_bruto_ssd += value['disk_ssd']
        if type(value["disk_hdd"]) is int and value['status'] != 'discarded':
            storage_size_bruto_hdd += value['disk_hdd']

    storage_size_bruto_total = storage_size_bruto_ssd + storage_size_bruto_hdd

    stats['storage_size_bruto_total'] = storage_size_bruto_total
    stats['storage_size_bruto_ssd'] = storage_size_bruto_ssd
    stats['storage_size_bruto_hdd'] = storage_size_bruto_hdd


def get_cost_storage_per_type():
    price_ssd = 0.170
    price_hdd = 0.040

    data_size_netto_hdd = 260 * 1024
    data_size_netto_ssd = 10 * 1024

    if cost_total_storage not in globals():
        get_cost_total()

    cost_total_storage_ssd = (
        cost_total_storage *
        (data_size_netto_ssd * price_ssd) /
        (
            (data_size_netto_ssd * price_ssd) +
            (data_size_netto_hdd * price_hdd)
        )
    )

    price_storage_ssd_gb_per_month = (
        cost_total_storage_ssd * 365 / 12 / data_size_netto_ssd
    )

    cost_total_storage_hdd = (
        cost_total_storage *
        (data_size_netto_hdd * price_hdd) /
        (
            (data_size_netto_ssd * price_ssd) +
            (data_size_netto_hdd * price_hdd)
        )
    )

    price_storage_hdd_gb_per_month = (
        cost_total_storage_hdd * 365 / 12 / data_size_netto_hdd
    )

    stats['price_storage_ssd_gb_per_month'] = price_storage_ssd_gb_per_month
    stats['price_storage_hdd_gb_per_month'] = price_storage_hdd_gb_per_month
    stats['cost_total_storage_ssd'] = cost_total_storage_ssd
    stats['cost_total_storage_hdd'] = cost_total_storage_hdd


# ## Determine total netto storage
# # TODO: Determine a way to measure netto storage
#
# # Determine total netto amount of stored data
# ## Query ES for the latest values for all file share storage, block storage and backup
# # TODO: Get data about databases, local storage

def get_usage_storage():
    # TODO: reduce the number of ES queries
    # def get_usage_fileshare_storage():
    global data_fileshare_size_total
    global data_fileshare_amount_total
    data_fileshare_size_total = 0
    data_fileshare_amount_total = 0

    data_fileshare_stats = es.get_latest_stats("storage_type",
                                               "fileshare", "storage_path")
    for stat in data_fileshare_stats:
        s = stat['newest_records']['hits']['hits'][0]['_source']['data_size']
        if type(s) == int:
            data_fileshare_size_total += s
        a = stat['newest_records']['hits']['hits'][0]['_source']['data_amount']
        if type(a) == int:
            data_fileshare_amount_total += a

    stats['data_fileshare_size_total'] = data_fileshare_size_total
    stats['data_fileshare_amount_total'] = data_fileshare_amount_total

    # Get usage for block storage
    global data_block_size_total
    global data_block_amount_total
    data_block_size_total = 0
    data_block_amount_total = 0

    data_block_stats = es.get_latest_stats("storage_type", "block", "data_set.id")
    for stat in data_block_stats:
        s = stat['newest_records']['hits']['hits'][0]['_source']['data_size']
        if type(s) == int:
            data_block_size_total += s
        a = stat['newest_records']['hits']['hits'][0]['_source']['data_amount']
        if type(a) == int:
            data_block_amount_total += a

    stats['data_block_size_total'] = data_block_size_total
    stats['data_block_amount_total'] = data_block_amount_total

    # Get usage for backup storage
    global data_backup_size_total
    global data_backup_amount_total
    global data_backup_stats
    data_backup_size_total = 0
    data_backup_amount_total = 0
    data_backup_stats = es.get_latest_stats("storage_type", "backup", "storage_path")
    for stat in data_backup_stats:
        s = stat['newest_records']['hits']['hits'][0]['_source']['data_size']
        if type(s) == int:
            data_backup_size_total += s
        a = stat['newest_records']['hits']['hits'][0]['_source']['data_amount']
        if type(a) == int:
            data_backup_amount_total += a

    stats['data_backup_size_total'] = data_backup_size_total
    stats['data_backup_amount_total'] = data_backup_amount_total

    data_size_total = (
        data_fileshare_size_total +
        data_block_size_total +
        data_backup_size_total
    )

    data_amount_total = (
        data_fileshare_amount_total +
        data_block_amount_total +
        data_backup_amount_total
    )

    stats['data_size_total'] = data_size_total
    stats['data_amount_total'] = data_amount_total

def update_storage_datapoints():
    """Update the analytics index with the latest available storage stats.

    In order to be able to visualize the infra statitics in Kibana, this
    function queries the temporary Elastic index for the last available
    datapoint on every storage object, applies the same timestamp to all
    datapoints and outputs them to a JSON file so Filebeat can pick them up.
    """
    json_location = config.get('output_file', 'infra_stats')
    latest = []
    latest_block = es.get_latest_stats("storage_type",
                                       "block",
                                       "data_set.id",
                                       es_index="logstash-default-*",
                                       days=14)
    for d in latest_block:
        doc = d['newest_records']['hits']['hits'][0]['_source']
        doc['@timestamp'] = strftime("%Y-%m-%dT06:00:00.000Z", gmtime())
        doc['fields']['type'] = 'infra-analytics'
        latest.append(doc)
    latest_fileshare = es.get_latest_stats("storage_type",
                                           "fileshare",
                                           "storage_path",
                                           es_index="logstash-default-*",
                                           days=14)
    for d in latest_fileshare:
        doc = d['newest_records']['hits']['hits'][0]['_source']
        doc['@timestamp'] = strftime("%Y-%m-%dT06:00:00.000Z", gmtime())
        doc['fields']['type'] = 'infra-analytics'
        latest.append(doc)
    latest_backup = es.get_latest_stats("storage_type",
                                        "backup",
                                        "storage_path",
                                        es_index="logstash-default-*",
                                        days=14)
    for d in latest_backup:
        doc = d['newest_records']['hits']['hits'][0]['_source']
        doc['@timestamp'] = strftime("%Y-%m-%dT06:00:00.000Z", gmtime())
        doc['fields'] = {}
        doc['fields']['type'] = 'infra-analytics'
        latest.append(doc)
    with open(json_location, 'a') as jsonfile:
        # log.logger.debug('Writing stats of %s' % check_folder)
        for l in latest:
            json.dump(l, jsonfile)
            jsonfile.write('\n')
            # log.logger.debug('Done writing file %s' % json_location)

def get_infra_stats():
    get_cost_total()
    get_cost_storage_per_type()
    get_usage_storage()
    stats['@timestamp'] = datetime.now().isoformat()
    stats['fields'] = {}
    stats['fields']['type'] = 'infra-analytics'
    json_location = config.get('output_file', 'infra_stats')
    with open(json_location, 'a') as jsonfile:
        # log.logger.debug('Writing stats of %s' % check_folder)
        json.dump(stats, jsonfile)
        jsonfile.write('\n')
        # log.logger.debug('Done writing file %s' % json_location)
        #return stats

# Connect to the infrastructure facts sheet
scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name(
              config.get('google_credentials', 'infra_stats'), scope)
gc = gspread.authorize(credentials)

factsheet = gc.open_by_key(config.get('factsheet_key', 'infra_stats'))
facts_worksheet = factsheet.worksheet('facts')

cmdb = gc.open_by_key(config.get('cmdb_key', 'infra_stats'))
hardware_worksheet = cmdb.worksheet('PhysicalHosts')

# Put all cost in a nice dictionary
facts = {}
for item in facts_worksheet.get_all_records():
    facts[item['expense']] = {'comment': item['comment'],
                              'unit': item['unit'],
                              'value': item['value']}

# TODO: add a sheet for other investments apart from specific nodes
# (i.e. separate hard disks)
# Do the same with all investments
# investments = {}
# for item in investments_worksheet.get_all_records():
#     investments[item['hardware']] = {'purchase_date': item['purchase_date'],
#                                      'price': item['price'],
#                                      'purpose': item['purpose']}

# Do the same with all investments
hardware = {}
for item in hardware_worksheet.get_all_records():
    hardware[item['barcode']] = {'purchase_date': item['purchase_date'],
                                 'purchase_price': item['purchase_price'],
                                 'role': item['role'],
                                 'status': item['status'],
                                 'units': item['units'],
                                 'disk_hdd': item['disk_hdd'],
                                 'disk_ssd': item['disk_ssd']}

# Determine some constants
# Writeoff time
writeoff_time = timedelta(days=(facts['writeoff_years']['value']*365))

# Create stats dictionary for collection of all stats.
stats = {}

#infra_stats = get_infra_stats()
update_storage_datapoints()
get_infra_stats()

