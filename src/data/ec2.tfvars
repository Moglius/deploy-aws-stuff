configuration = [
  {
    "id" : "server3",
    "name" : "server3",
    "type" : "t2.micro",
    "region" : "us-east-2",
    "subnet_id" : "subnet-0af061bce62a0a251",
    "ami_id" : "ami-09bed07ff0a9eeff7",
    "ami_filter" : "XMDW_rhel8",
    "root_block_device" : {
      "device_name" : "/dev/xvda",
      "volume_size" : "8",
      "volume_type" : "gp3"
    },
    "ebs_block_devices" : [
      {
        "device_name" : "/dev/sdc",
        "volume_size" : "1",
        "volume_type" : "gp3"
      }
    ]
  },
  {
    "id" : "server4",
    "name" : "server4",
    "type" : "t2.micro",
    "region" : "us-east-2",
    "subnet_id" : "subnet-0af061bce62a0a251",
    "ami_id" : "ami-0b66b95b07c753e1a",
    "ami_filter" : "XMDW_rhel8",
    "root_block_device" : {
      "device_name" : "/dev/xvda",
      "volume_size" : "8",
      "volume_type" : "gp3"
    },
    "ebs_block_devices" : [
      {
        "device_name" : "/dev/sdc",
        "volume_size" : "1",
        "volume_type" : "gp3"
      }
    ]
  }
]
