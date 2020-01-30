# Problem
[Bookinfo](https://istio.io/docs/examples/bookinfo/) application should be deployed to the Kubernetes cluster and tested. The solution for testing can be written on Python or Bash.

## Requirements
Solution for testing should meet the listed below requirements:

- Kubernetes cluster should be deployed using Minikube in the scope of test script/framework;
- Kubernetes cluster should be provisioned and configured by the test script/framework;
- Bookinfo application should be deployed by the test script/framework;
- Bookinfo application should be tested by the test script/framework;
- Test results should be collected by the test script/framework.

# Solution
Task solved using Python framework placed in the current repo.

## Environment requirements
As an environment, I have picked up a bare-metal server running Debian 10.

To start working please clone this project on the machine where the script will be executed. For the acceptable performance I recommend to run all this stuff on the bare-metal server with the minimum requirements:

- 4 Core CPU;
- 8 Gb RAM;
- 20 Gb HDD.

## Environment preparation
Please, clone this repo into the home directory of the root user:
```
git clone git@github.com:SerhiyMakarenko/bookinfo-tester.git
```

To save your time I have prepared the bash script that will prepare the environment for running python tester script. Since the script should install additional packages and create a minikube user it requires superuser privileges. Please, run it under root:
```
cd tools
./environment_setup.sh
```

After that please login into the system using newly created `minikube` user and install required python dependencies:
```
pip3 install -r pip3 install -r ./bookinfo_tester/requirements.txt
```

When dependencies would be installed, please run the tester script:
```
cd bookinfo_tester
./bookinfo_tester.py
```

## Some explanations of the chosen architecture
For providing an ability to reach K8s services locally and assign an external IP address to ingress I chose [MetaLB](https://metallb.universe.tf) load balancer.

This requires a slight modification of the default minikube installation. And this is the reason why the folder `tools` appears in this repo.

Folder contains listed below files:
```
- tools
   |-- environment_setup.sh
   |-- metallb_configmap.yaml
    -- minikube-net.xml
```
About aim of the `environment_setup.sh` I told earler.

`minikube-net.xml` provides a modified network config for `minikube-net` KVM network that will be created by default during minikube run. I have made this to free IP addresses after `192.168.39.200` from DHCP to give some from this range to MetalLB.

`metallb_configmap.yaml` -- config map for K8s to assign IP addresses to Istio ingress load balancer.

## What script do
`bookinfo_tester.py` script performs listed below set of activities in mentioned order:

### K8s provisioning tasks

- Start K8s cluster using minikube;
- Install in K8s cluster MetalLB Load Balancer;
- Initialize Helm;
- Install Istio into K8s cluster;
- Deploy Bookinfo application.

### Bookinfo test tasks

- Request Routing case: route all requests to v1 and check the results;
- Request Routing case: route based on user identity and check the results;
- Request Routing case: route all requests to review v3 and check the results.

## What can be improved
Listed below things clear for me now:

- Invoking `kubectl` command for applying manifests. This approach was chosen to cut corners and save development time. Unfortunately, K8s API does not provide an ability to deploy a set of resources from a single YAML manifest with a mix of resources. To implement those steps in the python-way require developing custom parser. This task beyond the scope of this work;
- Clear and simple error handling during subprocess invocation.
- Increasing test coverage. I cover in the script only Request Routing cases. As an improvement test range can be extended to cover route cases based on user identity, Injecting an HTTP delays fault, weight-based routing and more.