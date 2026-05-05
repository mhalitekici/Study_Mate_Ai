#!/bin/bash
# Install Istio
curl -L https://istio.io/downloadIstio | sh -
cd istio-*
export PATH=$PWD/bin:$PATH

# Install Istio with demo profile
istioctl install --set profile=demo -y

# Enable injection for studymate namespace
kubectl label namespace studymate istio-injection=enabled

echo "Istio installed successfully!"
istioctl verify-install