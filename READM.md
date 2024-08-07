# ModularDNS

ModularDNS is a highly flexible DNS resolving service designed to be easily
extendable with new functionalities through a modular architecture. It
provides a variety of basic DNS functionalities and allows developers to add
new features as separate modules.

## Key Features

- **DNS Query Forwarding**: Supports DNS over HTTPS (DoH), DNS over TLS (DoT),
  and traditional UDP/TCP forwarding.
- **Load Balancing**: Distributes DNS queries across multiple remote servers.
- **Query Routing**: Routes DNS queries to different remote servers based on
  their question fields.
- **Local DNS Cache and Lookup Table**: Maintains a local cache and lookup
  table for DNS queries.
- **Query Filtering**: Filters unwanted DNS queries.
- **Rate Limiting**: Limits the number of DNS requests to prevent abuse.
- **Modular Architecture**: Easily extend the service by adding new modules.

## Motivation

ModularDNS is inspired by
[encrypted-dns](https://github.com/zhenghaven/encrypted-dns),
which provides similar functionalities but lacks the
flexibility for adding new features due to its complex and inflexible
architecture. ModularDNS addresses these issues by starting from scratch with
a focus on modularity and simplicity.

## Modules

### Downstream

Modules under the `downstream` category are responsible for handling incoming
DNS "question"s and returning the corresponding "answer"s.

There are 3 subcategories of modules under the `downstream` category:

#### Local

Modules under the `local` category are responsible for resolving DNS queries
based on records stored locally.

- **Hosts**: maintains a lookup table for domain names and their corresponding
  IP addresses, similar to the functionality provided by the `/etc/hosts` file.
- **Cache**: caches DNS queries and answers to reduce latency and network
  traffic.

#### Remote

Modules under the `remote` category are mainly relying on remote services to
resolve DNS queries.

- **HTTPS**: forwards DNS queries over HTTPS using the DoH protocol.
- **TLS**: (work in progress) forwards DNS queries over TLS using the DoT
  protocol.
- **UDP**: forwards DNS queries over UDP.
- **TCP**: (work in progress) forwards DNS queries over TCP.
- **ByProtocol**: based on the `endpoint` object giving to this module, it will
  pick the right module (i.e., one of `HTTPS`, `TLS`, `UDP`, and `TCP`)
  to construct the instance.

#### Logical

Modules under the `logical` category will focus on logical operations on
incoming DNS queries, while the actual resolution will likely be delegated to
other modules.

- **Failover**: it will first try to query an `initial` module, and if it fails,
  it will try to query a `failover` module.
- **LimitConcurrentReq**: limits the maximum number of requests that the
  underlying module should handle concurrently.
- **QuestionRuleSet**: based on the question fields, it will route the query to
  various underlying modules.
- **RaiseExcept**: raises an exception for every incoming query.
- **RandomChoice**: randomly (can be weighted) picks one of the underlying
  modules to handle the query.

### Server

Modules under the `server` category are responsible for monitoring incoming
queries (e.g., opening a UDP socket and listening for incoming DNS queries,
in case of a `UDP` server module), forwarding them to the specified
*downstream* module,
and replying with the answer(s) received from the *downstream* module.

- **UDP**: (work in progress) listens for incoming DNS queries over UDP
  and forwards them to the specified downstream module.
- **TCP**: (work in progress) listens for incoming DNS queries over TCP
  and forwards them to the specified downstream module.

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE)
file for details.

## Acknowledgements

- Inspired by [encrypted-dns](https://github.com/zhenghaven/encrypted-dns).


For any questions or suggestions, feel free to open an issue.

