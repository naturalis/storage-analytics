from utils import log
from utils import config
from datetime import date, timedelta, datetime
from elasticsearch import Elasticsearch

elastic_host = config.get('elastic_host')
elastic_port = config.get('elastic_port')


def all_stats():
    elastic = Elasticsearch([elastic_host], port=elastic_port)
    stats = elastic.search(index="logstash-default-*", body={
      "size": 1000,
      "query": {
        "match": {
          "source": {
            "query": "/var/log/storage-analytics.json",
            "type": "phrase"
          }
        }
      }
    })['hits']['hits']
    return stats


def agg_stats():
    elastic = Elasticsearch([elastic_host], port=elastic_port)
    stats = elastic.search(index="logstash-default-*", body={
      "size": 1000,
      "aggs": {
        "group": {
          "terms": {
            "field": "storage_path.raw"
          },
          "aggs": {
            "group_docs": {
              "top_hits": {
                "size": 1,
                "sort": [
                  {
                    "@timestamp": {
                      "order": "desc"
                    }
                  }
                ]
              }
            }
          }
        }
      }
    })['hits']['hits']
    return stats


def get_latest_stats_old(filterfield, query, uniqfield,
                         es_index="infra-analytics-*", days=14):
    """
    Gather the latest statitics from Elasticsearch
    * Name of field to query on
    * Phrase to query with
    * Field that uniquely identifies the object for which to get the latest
      statistic
    * Elasticsearch index to look for statistics (default = parsefailure-*)
    * Number of days back in time to look for stats (default = 2)
    Returns a dict with the latest statistics
    """
    elastic = Elasticsearch([elastic_host], port=elastic_port)
    stats = elastic.search(index=es_index, body={
      "size": 10000,
      "query": {
        "constant_score": {
          "filter": {
            "bool": {
              "must": [
                {"match": {
                  filterfield: {
                    "query": query,
                    "type": "phrase"
                  }
                }},
                {"range": {
                  "@timestamp": {
                    "gt": "now-" + str(days) + "d"
                  }
                }},
              ]
            }
          }
        }
      }
    })['hits']['hits']

    latest = {}
    for m in stats:
        data = m['_source']
        # Check if there's already a message about the object in the dictionary
        if data[uniqfield] in latest.keys():
            # TODO: don't just discard timezone data you lazy bastard
            if datetime.strptime(data['@timestamp'][:-5], '%Y-%m-%dT%H:%M:%S') > datetime.strptime(latest[data[uniqfield]]['@timestamp'][:-5], '%Y-%m-%dT%H:%M:%S'):
                latest[data[uniqfield]] = data
        else:
            latest[data[uniqfield]] = data
    return latest


def get_latest_stats(filterfield, query, uniqfield,
                     es_index="infra-analytics-*", days=14):
    """
    Gather the latest statitics from Elasticsearch
    * Name of field to query on
    * Phrase to query with
    * Field that uniquely identifies the object for which to get the latest
      statistic
    * Elasticsearch index to look for statistics (default = parsefailure-*)
    * Number of days back in time to look for stats (default = 14)
    Returns a dict with the latest statistics
    """
    elastic = Elasticsearch([elastic_host], port=elastic_port)
    stats = elastic.search(index="logstash-default-*", body={
      "aggs": {
        "agg_" + uniqfield: {
           "terms": {
             "field": uniqfield + ".raw",
             "size": 0
           },
           "aggs": {
             "newest_records": {
               "top_hits": {
                 "sort": [
                   {"@timestamp": {"order": "desc"}}
                 ],
                 "size": 1,
                 "_source": {}
               }
             }
           }
        }
      },
      "size": 0,
      "query": {
        "bool": {
          "must": [
            {
              "match": {
                filterfield: {
                  "query": query,
                  "type": "phrase"
                }
              }
            },
            {
              "range": {
                "@timestamp": {
                  "gt": "now-" + str(days) + "d"
                }
              }
            },
          ]
        }
      }
    })
    return stats['aggregations']['agg_' + uniqfield]['buckets']


def get_latest_stats_must(filterfield, query, uniqfield,
                          es_index="logstash-default-*", days=14):
    """
    Gather the latest statitics from Elasticsearch
    * Name of field to query on
    * Phrase to query with
    * Field that uniquely identifies the object for which to get the latest
      statistic
    * Elasticsearch index to look for statistics (default = parsefailure-*)
    * Number of days back in time to look for stats (default = 14)
    Returns a dict with the latest statistics
    """
    elastic = Elasticsearch([elastic_host], port=elastic_port)
    stats = elastic.search(index="logstash-default-*", body={
      "aggs": {
        "agg_" + uniqfield: {
          "terms": {
            "field": uniqfield + ".raw",
            "size": 0
          },
          "aggs": {
            "newest_records": {
              "top_hits": {
                "sort": [
                  {
                    "@timestamp": {"order": "desc"}
                  }
                ],
                "size": 1,
                "_source": {
                  "includes": [
                    "data_size",
                    "data_amount",
                    uniqfield
                  ]
                }
              }
            }
          }
        }
      },
      "size": 0,
      "query": {
        "bool": {
          "must": [
            {"match": {"storage_path": "smb*"}},
            {"range": {
              "@timestamp": {
                "gt": "now-" + str(days) + "d"
              }
            }},
          ]
        }
      }
    })
    return stats['aggregations']['agg_' + uniqfield]['buckets']
