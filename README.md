# Problem
[Bookinfo](https://istio.io/docs/examples/bookinfo/) application should be deployed to the Kubernetes cluster and tested. Solution for testing can be written on Python or Bash.

## Requirements
Solution for testing should met the listed below requirements:

- Kubernetes cluster should be deployed using Minikube in the scope of test script/framework;
- Kubernetes cluster should be provisioned and configured by the test script/framework;
- Bookinfo application should be deployed by the test script/framework;
- Bookinfo application should be tested by the test script/framework;
- Test results should be collected by the test script/framework.

# Solution
Task solved using Python framework placed in the current repo.

## Environment requirements
As an environment I have picked up bare-metal server running Debian 10.

To start working please clone this project on the machine where script will be executed. For the asseptible perfomance I recomend to run all this staf on the bare-metal server with the minimum requrements:

- 4 Core CPU;
- 8 Gb RAM;
- 20 Gb HDD.

## Environment preparation
Please, clone this repo into home directory of the root user:
```
git clone git@github.com:SerhiyMakarenko/bookinfo-tester.git
```

To save your time I have prepared bash script that will prepeare the environment for running python tester script. Since script should install additional packages and create minikube user it requere superuser privileges. Please, run it under root:
```
./tools/environment_setup.sh
```

After that please login into the system using newly created `minikube` user and install required python dependencies:
```
pip3 install -r pip3 install -r ./bookinfo_tester/requirements.txt
```

When dependencies would be installed, please run tester script:
```
./bookinfo_tester/bookinfo_tester.py
```
