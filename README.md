# UCU Distributed systems course project
Author: Maksym Sarana


## Build Docker image
```docker build -t repl_logs .```

### Run 

Create a docker network

```docker network create ntwk```


Run nodes

```
docker run --net ntwk -p 61001:61001 --name rl_master repl_logs python ./main.py --is_master --http_port 61001 --secondary_nodes rl_secondary1.ntwk:61002 rl_secondary2.ntwk:61003
docker run --net ntwk -p 61004:61004 --name rl_secondary1 repl_logs python ./main.py --http_port 61004 --grpc_port 61002 --delay 10
docker run --net ntwk -p 61005:61005 --name rl_secondary2 repl_logs python ./main.py --http_port 61005 --grpc_port 61003 --delay 20
```

Append a new message

```curl -H "Content-Type: application/text" -X POST -d 'message' localhost:61001```

Get a list of messages

```curl -X GET localhost:61001```