#!/bin/env python3

import os
from time import sleep
from libs.setup_lib import run_command, check_environment, download_file, wait_pods_are_running, get_ingress_ip, validate_page
from libs.tester_lib import reviews_v1_testing, reviews_v2_testing, reviews_v3_testing

ip = get_ingress_ip("istio-system", "istio-ingressgateway")


def prerun_check():
    print("Checking environment...")
    components = ["kvm", "helm", "minikube", "virsh", "kubectl"]
    for component in components:
        check_environment(component)


def k8s_cluster_install():
    print(os.linesep + "Installing K8s using minikube...")
    run_command("minikube start --kubernetes-version v1.15.5 --cpus 3 --memory 6144", True)


def metallb_install():
    print(os.linesep + "Installing MetalLB Load Balancer...")
    download_file("https://github.com/metallb/metallb/archive/v0.8.3.zip")
    run_command("kubectl create -f /tmp/metallb-0.8.3/manifests/metallb.yaml", True)
    run_command("kubectl create -f ../tools/metallb_configmap.yaml", True)
    print("Waiting till pods for MetalLB will be ready...")
    wait_pods_are_running("metallb-system")


def helm_initialization():
    print(os.linesep + "Initializing Helm...")
    run_command("helm init --history-max 200", True)


def istio_install():
    print(os.linesep + "Installing Istio...")
    download_file("https://github.com/istio/istio/releases/download/1.0.5/istio-1.0.5-linux.tar.gz")
    os.system("helm template /tmp/istio-1.0.5/install/kubernetes/helm/istio --set global.mtls.enabled=false --set "
              "tracing.enabled=true --namespace istio-system > /tmp/istio-1.0.5/istio.yaml")
    run_command("kubectl create namespace istio-system", True)
    run_command("kubectl create -f /tmp/istio-1.0.5/istio.yaml", True)
    wait_pods_are_running("istio-system")


def bookinfo_install():
    print(os.linesep + "Installing Bookinfo application...")
    run_command("kubectl label namespace default istio-injection=enabled", True)
    run_command("kubectl apply -f /tmp/istio-1.0.5/samples/bookinfo/platform/kube/bookinfo.yaml", True)
    wait_pods_are_running("default")
    run_command("kubectl apply -f /tmp/istio-1.0.5/samples/bookinfo/networking/bookinfo-gateway.yaml", True)
    sleep(5)
    validate_page("http://" + str(ip) + "/productpage")


def test_run_0():
    print(os.linesep + "Configuring Request Routing to the v1...")
    files = ["destination-rule-all.yaml", "virtual-service-all-v1.yaml"]
    for file in files:
        run_command("kubectl apply -f /tmp/istio-1.0.5/samples/bookinfo/networking/" + file, True)
    sleep(2)
    print(os.linesep + "Testing reviews v1...")
    for item in range(0, 20):
        print("Test for book #" + str(item) + ":")
        reviews_v1_testing("http://" + str(ip) + "/api/v1/products/" + str(item) + "/reviews")
    print("Cleaning up after test...")
    for file in files:
        run_command("kubectl delete -f /tmp/istio-1.0.5/samples/bookinfo/networking/" + file, True)


def test_run_1():
    print(os.linesep + "Configuring Request Routing to the v2 based on the user identity...")
    files = ["destination-rule-all.yaml", "virtual-service-reviews-jason-v2-v3.yaml"]
    for file in files:
        run_command("kubectl apply -f /tmp/istio-1.0.5/samples/bookinfo/networking/" + file, True)
    sleep(2)
    print(os.linesep + "Testing reviews v2 as user jason...")
    for item in range(0, 20):
        print("Test for book #" + str(item) + ":")
        reviews_v2_testing("http://" + str(ip) + "/api/v1/products/" + str(item) + "/reviews")
    print(os.linesep + "Testing reviews v1 as anonymous user...")
    for item in range(0, 20):
        print("Test for book #" + str(item) + ":")
        reviews_v1_testing("http://" + str(ip) + "/api/v1/products/" + str(item) + "/reviews")
    print("Cleaning up after test...")
    for file in files:
        run_command("kubectl delete -f /tmp/istio-1.0.5/samples/bookinfo/networking/" + file, True)


def test_run_2():
    print(os.linesep + "Configuring Request Routing to the reviews v3...")
    files = ["destination-rule-all.yaml", "virtual-service-reviews-v3.yaml"]
    for file in files:
        run_command("kubectl apply -f /tmp/istio-1.0.5/samples/bookinfo/networking/" + file, True)
    sleep(2)
    print(os.linesep + "Testing reviews v3...")
    for item in range(0, 20):
        print("Test for book #" + str(item) + ":")
        reviews_v3_testing("http://" + str(ip) + "/api/v1/products/" + str(item) + "/reviews")
    print("Cleaning up after test...")
    for file in files:
        run_command("kubectl delete -f /tmp/istio-1.0.5/samples/bookinfo/networking/" + file, True)


if __name__ == "__main__":
    print("Provisioning K8s cluster...")
    prerun_check()
    k8s_cluster_install()
    metallb_install()
    helm_initialization()
    istio_install()
    bookinfo_install()

    print(os.linesep + "Testing Bookinfo App API...")
    test_run_0()
    test_run_1()
    test_run_2()
