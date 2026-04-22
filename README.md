# Spark Test

##  datalake 구축

```

cd datalake
docker-compose up -d

$ docker ps
CONTAINER ID   IMAGE                COMMAND                  CREATED             STATUS                       PORTS                                                                                      NAMES
9a54af348920   apache/spark:3.5.0   "/opt/entrypoint.sh …"   About an hour ago   Up About an hour             0.0.0.0:15002->15002/tcp, [::]:15002->15002/tcp                                            spark-connect
ecf0520637e4   apache/hive:4.0.0    "sh -c /entrypoint.sh"   About an hour ago   Up About an hour (healthy)   10000/tcp, 0.0.0.0:9083->9083/tcp, [::]:9083->9083/tcp, 10002/tcp                          hive-metastore
ce4718c7da5b   apache/kudu:latest   "/kudu-entrypoint.sh…"   About an hour ago   Up About an hour             0.0.0.0:7051->7051/tcp, [::]:7051->7051/tcp, 0.0.0.0:8051->8051/tcp, [::]:8051->8051/tcp   kudu-tserver
bad5f49a1826   postgres:15          "docker-entrypoint.s…"   About an hour ago   Up About an hour (healthy)   0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp                                                postgres
35db39f7b53e   apache/kudu:latest   "/kudu-entrypoint.sh…"   About an hour ago   Up About an hour             0.0.0.0:7050->7050/tcp, [::]:7050->7050/tcp, 0.0.0.0:8050->8050/tcp, [::]:8050->8050/tcp   kudu-master
2aea746b9c98   apache/spark:3.5.0   "/opt/spark/bin/spar…"   About an hour ago   Up About an hour             0.0.0.0:7077->7077/tcp, [::]:7077->7077/tcp, 0.0.0.0:8080->8080/tcp, [::]:8080->8080/tcp   spark
868fc1141d69   minio/minio:latest   "/usr/bin/docker-ent…"   About an hour ago   Up About an hour (healthy)   0.0.0.0:9000-9001->9000-9001/tcp, [::]:9000-9001->9000-9001/tcp                            minio

```


## 실행
1. init.py 실행
2. dataGenerator.py 실행



## Spark Local Test
```
$ python spark_local.py
```

## Spark Connect Test
```
python spark_connect.py
```