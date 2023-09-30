configuration = [
  {
    "http_tcp_listeners" : [
      {
        "port" : 80,
        "protocol" : "HTTP",
        "target_group_index" : 0
      }
    ],
    "security_groups" : [
      "sg-0a8e4f0232617b63b"
    ],
    "target_groups" : [
      {
        "target_type" : "instance",
        "name_prefix" : "lb1-",
        "health_check" : {
          "path" : "/",
          "healthy_threshold" : 3,
          "protocol" : "HTTP",
          "port" : "traffic-port",
          "unhealthy_threshold" : 3,
          "interval" : 30,
          "matcher" : "200-399",
          "enabled" : true,
          "timeout" : 6
        },
        "backend_protocol" : "HTTP",
        "backend_port" : 80,
        "targets" : {
          "i-0446c827c74392ddf" : {
            "target_id" : "i-0446c827c74392ddf",
            "port" : 80
          },
          "i-0d9bfb42768af734b" : {
            "target_id" : "i-0d9bfb42768af734b",
            "port" : 80
          }
        }
      }
    ],
    "vpc_id" : "vpc-022211da1d6546ff3",
    "internal" : false,
    "discovery_tag" : "lb-1234567",
    "id" : "lb1",
    "name" : "lb1",
    "operational" : true,
    "subnets" : [
      "subnet-0af061bce62a0a251",
      "subnet-0d7282b757dddab53"
    ]
  }
]
