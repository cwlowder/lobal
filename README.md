# lobal
A python load balancer/microservice experiment
### What is this
The purpose of this project is to emmulate what you might find in a microservice architecture in a few python scripts
![load balancer diagram](http://blog.arungupta.me/wp-content/uploads/2015/04/microservices-proxy.png)
So far, this project simply proxies through requests for specific webpages(a service) to a node server
### How it works
A node can be created like so:
```bash
./node <ip of server>
```
When a node is created, it will send a push request to the server, registering this node as a server for some service(a webpage).
The server will then remember that a node at some location has this service. Thus, when a client requests a particular
service, the server will randomly pick a node registered on that service to proxy the request to.

This registration action can be emulated with this bash command:
```bash
curl --header "Content-Type: application/json"   --request POST   --data '{"name":"/", "port":5000}'   http://localhost:9000
```
Where we register the name of the service to be "/" and that service to be running on port 5000.
Evantually, the server will remove this node as it crawls through all the nodes registered on itself.

Before then, we can curl all the nodes registered on the server
```bash
curl localhost:9000
```
This shows the internal state of the server
```json
{
    "/": [
        [
            "127.0.0.1",
            5000
        ]
    ]
}
```
Also included in this code base is a simple file node that can be used to allow the arbitrary query of files, or the service
of a particular file.
```bash
./FileHostHandler.py <ip of server> <service name> <file name>
```
