configuration = [
  {
    "id" : "server1",
    "name" : "server1",
    "type" : "t2.micro",
    "region" : "us-east-2",
    "subnet_id" : "subnet-0af061bce62a0a251",
    "ami_id" : "ami-00a9282ce3b5ddfb1",
    "ami_filter" : "N/A",
    "root_block_device" : {
      "device_name" : "/dev/xvda",
      "volume_size" : "8",
      "volume_type" : "gp3"
    },
    "ebs_block_devices" : [
      {
        "device_name" : "/dev/sdb",
        "volume_size" : "1",
        "volume_type" : "gp3"
      },
      {
        "device_name" : "/dev/sdc",
        "volume_size" : "1",
        "volume_type" : "gp3"
      }
    ]
  },
  {
    "id" : "server2",
    "name" : "server2",
    "type" : "t3.micro",
    "region" : "us-east-2",
    "subnet_id" : "subnet-0af061bce62a0a251",
    "ami_id" : "ami-00a9282ce3b5ddfb1",
    "ami_filter" : "N/A",
    "root_block_device" : {
      "device_name" : "/dev/xvda",
      "volume_size" : "8",
      "volume_type" : "gp3"
    },
    "ebs_block_devices" : [
      {
        "device_name" : "/dev/sdb",
        "volume_size" : "1",
        "volume_type" : "gp3"
      }
    ]
  }
]
