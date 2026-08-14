# Design a Distributed Rate Limiter

> High-Level System Design

## Overview

A Rate Limiter protects backend services from abuse by restricting the number of requests a client can make within a configured time window.

This design targets a **globally distributed API Gateway** serving millions of requests per second while prioritizing:

- High Availability
- Low Latency
- Horizontal Scalability
- Configurable Rate Limits

For this design, we assume:

- Requests are identified using **Client IP**
- Every client has the same rate limit (extensions discussed later)
- Token Bucket algorithm is used
- Rate limiting is enforced at the API Gateway

---



# Functional Requirements

- Limit requests per client IP
- Reject requests exceeding the configured rate limit
- Return HTTP **429 Too Many Requests**
- Support configurable rate limit policies
- Support dynamic configuration updates without restarting services

---



# Non-Functional Requirements

- High Availability
- Low Latency (<10ms additional latency)
- Horizontally Scalable
- Handle burst traffic
- Fault tolerant
- Consistent rate limiting (best effort under distributed constraints)

---



# Capacity Estimation



## Traffic


| Metric             | Value          |
| ------------------ | -------------- |
| Peak Requests      | 10 Million RPS |
| Average Requests   | 3 Million RPS  |
| Daily Active Users | 100 Million    |


---



## Redis Capacity

Assumption:

- One Redis shard can sustain **~100K operations/sec**

Required shards:

```
10M / 100K = 100 Redis shards
```

This excludes replication and operational headroom.

---



# High Level Architecture

```
                  +----------------+
                  | Configuration  |
                  |   ZooKeeper    |
                  +----------------+
                         ^
                         |
                 Pub/Sub / Watch Events
                         |
                         v

+---------+     +------------------------+
| Client  | --->|      API Gateway       |
+---------+     |                        |
                |  +------------------+  |
                |  |   Rate Limiter   |  |
                |  +------------------+  |
                +-----------|------------+
                            |
                    Persistent TCP Connections
                            |
                            v
              +------------------------------+
              | Redis Cluster (100+ Shards)  |
              +------------------------------+
                            |
                            v
          +---------------------------------------+
          | Backend Microservices                 |
          | Service A | Service B | Service C     |
          +---------------------------------------+
```

---



# Request Flow

1. Client sends HTTP request.
2. Request reaches API Gateway.
3. Gateway invokes Rate Limiter.
4. Rate Limiter:
  - Looks up cached configuration.
  - Executes Lua script inside Redis.
5. Lua script:
  - Reads Token Bucket.
  - Refills tokens using elapsed time.
  - Updates bucket atomically.
6. If tokens remain:
  - Forward request to backend.
7. Otherwise:
  - Return HTTP 429.

---



# Components



## API Gateway

Responsibilities:

- Authentication
- Routing
- Rate limiting
- Load balancing

Rate limiting is performed before routing traffic to backend services.

---



## Rate Limiter

Responsible for:

- Identifying client
- Fetching cached configuration
- Executing Redis Lua script
- Returning Allow / Reject decision

No rate limiting state is stored inside the gateway.

---



## Configuration Store

Chosen Technology:

- ZooKeeper

Stores:

- Bucket capacity
- Refill rate
- Algorithm configuration

Configuration is propagated to gateways through:

- Watch Events
- Pub/Sub

Gateways maintain an in-memory cache to avoid querying ZooKeeper on every request.

---



## Redis Cluster

Stores Token Bucket state.

Each entry contains:

```
Client IP
↓

{
    tokens,
    last_refill_timestamp
}
```

Redis is chosen because:

- In-memory
- Extremely low latency
- Atomic Lua execution
- Horizontal sharding

---



# Token Bucket Algorithm

Each client owns one bucket.

Bucket fields:

```
capacity
current_tokens
last_refill_timestamp
```

Whenever a request arrives:

```
elapsed = now - last_refill

tokens += elapsed * refill_rate

tokens = min(capacity, tokens)

if tokens > 0:
    tokens -= 1
    allow
else:
    reject
```

---



# Why Lua?

Without Lua:

```
GET bucket

calculate

SET bucket
```

Two simultaneous requests can both read the same bucket and oversubscribe the limit.

Lua executes the complete Read → Modify → Write cycle atomically inside Redis.

Benefits:

- Atomicity
- Single network call
- Lower latency
- No race conditions

---



# API Design

```python
class RateLimiter:

    def allow_request(
        self,
        client_ip: str
    ) -> bool:
        ...
```

Possible HTTP responses

```
200 OK

or

429 Too Many Requests
```

Future extensions:

```python
allow_request(
    client_ip,
    api_key,
    organization_id,
    endpoint
)
```

---



# Data Model



## Redis

```
Key

rate_limit:<client_ip>
```

Value

```json
{
    "tokens": 87,
    "last_refill_timestamp": 1710000000
}
```

---



## Configuration

```
Key

rate_limit/default
```

```json
{
    "capacity":100,
    "refill_rate":100/sec
}
```

---



# Scaling Decisions



## Horizontal Redis Sharding

Consistent hashing distributes client buckets across Redis shards.

Benefits:

- Horizontal scaling
- Even distribution
- Minimal key movement

---



## Connection Pooling

Gateway maintains persistent TCP connections to Redis.

Avoids:

- TCP handshake
- Connection setup latency

---



## Cached Configuration

Instead of querying ZooKeeper per request:

```
Gateway Memory Cache

↓

Pub/Sub

↓

ZooKeeper
```

Benefits:

- Lower latency
- Reduced ZooKeeper load

---



# Failure Handling



## Redis Failure

Chosen behavior:

**Fail Open**

Reason:

Maintaining API availability is prioritized over strict rate enforcement.

Tradeoff:

Potential abuse while Redis is unavailable.

Alternative:

Fail Closed

Pros:

- Strong protection

Cons:

- Legitimate users blocked

---



## Gateway Failure

Gateway instances are stateless.

Traffic is redirected by the external load balancer.

---



## ZooKeeper Failure

Existing cached configuration continues serving requests.

Only configuration updates are delayed.

---



# Tradeoffs



## Global Redis Cluster



### Pros

- Single global quota
- Strong consistency
- Simpler implementation



### Cons

- Higher cross-region latency
- Difficult to meet sub-10ms globally
- Potential single operational bottleneck

This design intentionally prioritizes **global correctness** over regional latency.

---



## Availability vs Consistency

Chosen:

High Availability

Reason:

A temporary inability to rate limit is preferable to blocking all API traffic.

---



## Token Bucket vs Sliding Window

Chosen:

Token Bucket

Advantages:

- Allows bursts
- Constant memory
- Simple implementation
- Low Redis storage

Sliding Window provides stricter rolling-window guarantees but at higher implementation complexity.

---



# Production Improvements



## Multi-Region Considerations

This design intentionally uses a single globally accessible Redis Cluster to maintain a strict global quota.

### Advantages

- Single source of truth
- Stronger consistency
- Simpler implementation

### Tradeoffs

- Higher latency for geographically distant gateways
- Harder to achieve <10ms globally
- Larger operational blast radius

### Production Alternative

For latency-sensitive deployments, many production systems instead deploy one Redis cluster per region.

Pros:
- Lower latency
- Better regional isolation

Cons:
- Eventual consistency
- Users may temporarily exceed global quotas

The choice depends on business requirements. This design prioritizes global correctness over regional latency.

---



## Hierarchical Rate Limiting

Support:

```
Organization

↓

User

↓

API Key
```

Each request checks:

- Organization quota
- User quota

Challenges:

- Multi-key atomicity
- Cross-shard coordination
- Hot organization keys

---



## Hot Key Protection

Popular clients may overload a single Redis shard.

Possible mitigations:

- Virtual buckets
- Request batching
- Local token caching
- Adaptive throttling

---



## Observability

Metrics:

- Allowed requests/sec
- Rejected requests/sec
- Redis latency
- Lua execution latency
- Gateway latency
- Configuration update propagation time

---



## Rate Limit Headers

Return:

```
X-RateLimit-Limit

X-RateLimit-Remaining

Retry-After
```

---



# Interview Discussion Points

Topics that commonly arise during interviews:

- Why API Gateway instead of service-side rate limiting?
- Why Redis instead of SQL?
- Why Token Bucket instead of Sliding Window?
- Why Lua?
- Why ZooKeeper?
- Fail Open vs Fail Closed?
- Single Redis cluster vs Multi-region Redis?
- Redis replication strategy?
- Hot key mitigation?
- Hierarchical quotas?
- Consistent hashing?
- Configuration propagation?
- Cross-region consistency?
- Monitoring and alerting?
- Handling Redis outages?

---



# Known Limitations

- Single global Redis cluster increases latency for geographically distant clients.
- Strict global quotas become difficult in a multi-region deployment.
- Organization-level quotas can introduce hot keys.
- Replication lag may temporarily affect consistency after failover.

---



# Future Enhancements

- Regional Redis clusters
- Redis Sentinel / Cluster failover
- Hierarchical quotas
- Dynamic per-user plans
- API-key based rate limiting
- Endpoint-specific limits
- Weighted requests
- Adaptive rate limiting using traffic patterns
- Local token caches for ultra-low latency

---



# Technology Choices


| Component           | Technology           |
| ------------------- | -------------------- |
| API Gateway         | NGINX / Envoy / Kong |
| Rate Limiter        | Python               |
| Cache               | Redis Cluster        |
| Configuration Store | ZooKeeper            |
| Communication       | Persistent TCP       |
| Atomic Operations   | Redis Lua Scripts    |


---



# Complexity


| Operation            | Complexity    |
| -------------------- | ------------- |
| Allow Request        | O(1)          |
| Token Refill         | O(1)          |
| Redis Lookup         | O(1)          |
| Configuration Lookup | O(1) (cached) |


---



# Final Notes

This design prioritizes:

- High Availability
- Simplicity
- Horizontal Scalability
- Atomic rate limiting
- Production-ready configuration management

The primary tradeoff is accepting increased cross-region latency in exchange for maintaining a single global rate limit. A production-scale deployment would likely evolve toward regional Redis clusters with carefully considered consistency semantics based on business requirements.