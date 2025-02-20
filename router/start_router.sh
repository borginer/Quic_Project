#!/bin/sh
# Check if the service name argument is provided
if [ -z "$1" ]; then
  echo "Error: Private endpoint ip argument is missing."
  exit 1
fi

if [ -z "$2" ]; then
  echo "Error: Public router ip argument is missing."
  exit 1
fi

PRIVATE_ENDPOINT_IP=$1
PUBLIC_ROUTER_IP=$2
SUBNET1=$3
ROUTER1=$4
SUBNET2=$5
ROUTER2=$6

# Set up iptables rules using the service name argument
iptables -t nat -A POSTROUTING -o eth0 -j SNAT --to-source $PUBLIC_ROUTER_IP
iptables -t nat -A PREROUTING -i eth0 -j DNAT --to-destination $PRIVATE_ENDPOINT_IP
iptables -A FORWARD -i eth1 -o eth0 -j ACCEPT
iptables -A FORWARD -i eth0 -o eth1 -j ACCEPT

ip route add $SUBNET1 via $ROUTER1
ip route add $SUBNET2 via $ROUTER2

# Keep the container running
tail -f /dev/null