import sys
import zipfile
import tarfile
import requests
import subprocess
import urllib.request
from lxml import html
from time import sleep
from pathlib import Path
from termcolor import colored
from kubernetes import client, config, watch


def run_command(command_string, show_output):
    """
    This function provide an ability to invoke OS binaries for cases, when for some reasons difficult of impossible
    to perform actions in the python-way
    """
    command_array = command_string.split()
    process = subprocess.Popen(command_array, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            if show_output:
                print(output.strip())
    return_code = process.poll()
    return return_code


def check_environment(component):
    """
    Function for perform initial check of the environment where script will be executed to make sure that all
    requirements are met
    """
    return_code = run_command("which " + component, False)
    if return_code == 0:
        print(colored(component.upper() + " PASS", "green"))
    else:
        print(colored(component.upper() + " FAIL", "red"))
        sys.exit("Please, install " + component.upper() + " and rerun Bookinfo tester.")


def download_file(file_url):
    """
    The name of the function is self explanatory
    """
    path = Path(file_url)
    file_name = path.name
    urllib.request.urlretrieve(file_url, "/tmp/" + file_name)
    uncompress_archive(file_name)


def uncompress_archive(archive_name):
    """
    Function for dealing with zip and tar.gz archives
    """
    archive_type = Path(archive_name).suffixes
    if ".zip" in archive_type:
        with zipfile.ZipFile("/tmp/" + archive_name, 'r') as zip_ref:
            zip_ref.extractall("/tmp/")
    elif ".gz" or ".tar" in archive_type:
        tf = tarfile.open("/tmp/" + archive_name)
        tf.extractall("/tmp/")


def wait_pods_are_running(namespace_name):
    """
    Function for checking pod statuses interacting directly with the K8s API
    """
    pending_pods = []
    config.load_kube_config()
    v1 = client.CoreV1Api()
    w = watch.Watch()
    for event in w.stream(v1.list_pod_for_all_namespaces, timeout_seconds=10):
        if event['object'].metadata.namespace == namespace_name:
            if event['object'].status.phase not in ["Running", "Succeeded"]:
                pending_pods.append(event['object'].metadata.name)
    w.stop()
    while pending_pods:
        for pending_pod in pending_pods:
            pod_status = v1.read_namespaced_pod_status(pending_pod, namespace_name)
            if pod_status.status.phase in ["Running", "Succeeded"]:
                pending_pods.remove(pending_pod)
            else:
                print("Pod " + pod_status.metadata.name + " is not ready, waiting...")
                sleep(2)
    print("Pods for namespace " + namespace_name + " are ready.")


def get_ingress_ip(namespace_name, service_name):
    """
    Function for providing the IP address of the ingress
    """
    config.load_kube_config()
    v1 = client.CoreV1Api()
    services = v1.list_service_for_all_namespaces(watch=False)
    for service in services.items:
        if service.metadata.namespace == namespace_name:
            if service.metadata.name == service_name:
                return service.status.load_balancer.ingress[0].ip


def validate_page(site_url):
    """
    Function for validate that Simple Bookinfo app is deployed
    """
    page = requests.get(site_url)
    tree = html.fromstring(page.content)
    page_title = tree.xpath('/html/head/title/text()')
    if page_title[0] == "Simple Bookstore App":
        print(colored("Simple Bookstore website is reachable", "green"))
    else:
        print(colored("Simple Bookstore website is unreachable", "red"))
