#!/usr/local/bin/python

import kopf
import kubernetes.config as k8s_config
import kubernetes.client as k8s_client
import requests
import os
import json

def get_weather_data(location):
    request_url = f"api.openweathermap.org/data/2.5/weather?q={location}&APPID={os.environ['API_KEY']}"
    return requests.get(request_url).json()['main']

def create_weather_report_config_map(namespace, data):
    k8s = k8s_client.CoreV1Api()
    return k8s.create_namespaced_config_map(namespace, data)


def update_weather_report_config_map(namespace, name, new_data):
    k8s = k8s_client.CoreV1Api()
    return k8s.patch_namespaced_config_map(name, namespace, new_data)

@kopf.on.create('operators.rajputvaibhav.github.io', 'v1', 'weatherreports')
def on_create(namespace, spec, body, **kwargs):
    location = spec['location']
    weather_info = get_weather_data(location)
    data = {
            'data': {
                    weather_info
                    }
            }
    kopf.adopt(data) # to make sure it gets deleted if the operator components are removed
    configmap = create_weather_report_config_map(namespace, data)
    return {'configmap-name': configmap.metadata.name}


@kopf.on.update('operators.rajputvaibhav.github.io', 'v1', 'weatherreports')
def on_update(namespace, name, spec, status, **kwargs):
    location = spec['location']
    weather_info = get_weather_data(location)
    name = status['on_create']['configmap-name']
    data = {
            'data': {
                    json.dumps(weather_info)
                    }
            }
    update_weather_report_config_map(namespace, name, data)