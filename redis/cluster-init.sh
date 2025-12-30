#!/bin/sh

echo "Waiting for Redis nodes to be ready..."

for i in 1 2 3 4 5 6; do
    port=$((7000 + i))
    host="redis-node$i"
    while ! redis-cli -h $host -p $port ping > /dev/null 2>&1; do
        echo "Waiting for $host:$port..."
        sleep 1
    done
    echo "$host:$port is ready!"
done

echo "All Redis nodes are ready. Creating cluster..."

redis-cli --cluster create \
    redis-node1:7001 \
    redis-node2:7002 \
    redis-node3:7003 \
    redis-node4:7004 \
    redis-node5:7005 \
    redis-node6:7006 \
    --cluster-replicas 1 \
    --cluster-yes

echo "Redis Cluster created successfully!"

redis-cli -h redis-node1 -p 7001 cluster info
redis-cli -h redis-node1 -p 7001 cluster nodes
