from django.db import models


class BlockDevice(models.Model):
    device_name = models.CharField(max_length=30, default="/dev/xvda")
    volume_size = models.IntegerField(default=8)
    volume_type = models.CharField(max_length=5, default="gp3")
    available = models.BooleanField(default=True)
    volume_id = models.CharField(max_length=30, default="", blank=True)

    def __str__(self):
        return f"{self.device_name} ({self.volume_size}GB)"

    def get_json_repr(self):
        return {
            "device_name": self.device_name,
            "volume_size": self.volume_size,
            "volume_type": self.volume_type,
            "available": self.available,
            "volume_id": self.volume_id,
        }


class EC2Server(models.Model):
    name = models.CharField(max_length=30)
    ami_filter = models.CharField(max_length=30, default="N/A")
    ami_id = models.CharField(
        max_length=30, default="ami-00a9282ce3b5ddfb1", blank=True
    )
    discovered = models.BooleanField(default=False)
    root_block_device = models.ForeignKey(
        BlockDevice, on_delete=models.CASCADE, related_name="ec2_servers"
    )
    ebs_block_devices = models.ManyToManyField(BlockDevice, blank=True)
    imported = models.BooleanField(default=False)
    instance_id = models.CharField(max_length=30, default="", blank=True)
    instance_az = models.CharField(max_length=30, default="", blank=True)
    operational = models.BooleanField(default=True)
    region = models.CharField(max_length=30, default="us-east-2")
    subnet_id = models.CharField(max_length=30, default="", blank=True)
    type = models.CharField(max_length=15, default="t2.micro")

    class Meta:
        verbose_name = "EC2 Server"
        verbose_name_plural = "EC2 Servers"
