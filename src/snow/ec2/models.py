from django.db import models


class Tag(models.Model):
    key = models.CharField(max_length=30, default="Name")
    value = models.CharField(max_length=30, default="Server1")

    def __str__(self):
        return f"{self.key}: {self.value}"


class BlockDevice(models.Model):
    device_name = models.CharField(max_length=30, default="/dev/xvda")
    volume_size = models.IntegerField(default=8)
    volume_type = models.CharField(max_length=5, default="gp3")

    def __str__(self):
        return f"{self.device_name} ({self.volume_size}GB)"

    def get_json_repr(self):
        return {
            "device_name": self.device_name,
            "volume_size": self.volume_size,
            "volume_type": self.volume_type,
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
    operational = models.BooleanField(default=True)
    region = models.CharField(max_length=30, default="us-east-2")
    subnet_id = models.CharField(max_length=30, default="", blank=True)
    type = models.CharField(max_length=15, default="t2.micro")
    tags = models.ManyToManyField(Tag, blank=True)

    def get_json_tags(self):
        obj_json = {}
        for tag in self.tags.all():
            obj_json[tag.key] = tag.value
        return obj_json

    class Meta:
        verbose_name = "EC2 Server"
        verbose_name_plural = "EC2 Servers"


class SecurityGroup(models.Model):
    sg_id = models.CharField(max_length=30)

    def __str__(self):
        return self.sg_id


class Listener(models.Model):
    port = models.IntegerField()
    protocol = models.CharField(max_length=30)
    target_group_index = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.protocol}: {self.port}"


class HealthCheck(models.Model):
    enabled = models.BooleanField(default=True)
    interval = models.IntegerField(default=30)
    path = models.CharField(max_length=30, default="/")
    port = models.CharField(max_length=30, default="traffic-port")
    healthy_threshold = models.IntegerField(default=3)
    unhealthy_threshold = models.IntegerField(default=3)
    timeout = models.IntegerField(default=6)
    protocol = models.CharField(max_length=30, default="HTTP")
    matcher = models.CharField(max_length=30, default="200-399")

    def get_json_data(self):
        return {
            "enabled": self.enabled,
            "interval": self.interval,
            "path": self.path,
            "port": self.port,
            "healthy_threshold": self.healthy_threshold,
            "unhealthy_threshold": self.unhealthy_threshold,
            "timeout": self.timeout,
            "protocol": self.protocol,
            "matcher": self.matcher,
        }


class TargetGroup(models.Model):
    name_prefix = models.CharField(max_length=30)
    backend_protocol = models.CharField(max_length=30)
    backend_port = models.IntegerField(default=80)
    target_type = models.CharField(max_length=30, default="instance")
    health_check = models.ForeignKey(
        HealthCheck, on_delete=models.CASCADE, related_name="target_groups"
    )

    def __str__(self):
        return f"{self.backend_protocol}: {self.backend_port} ({self.name_prefix})"


class ALB(models.Model):
    name = models.CharField(max_length=30)
    vpc_id = models.CharField(max_length=30)
    security_groups = models.ManyToManyField(SecurityGroup, blank=True)
    internal = models.BooleanField(default=False)
    http_tcp_listeners = models.ManyToManyField(Listener, blank=True)
    target_groups = models.ManyToManyField(TargetGroup, blank=True)
    discovery_tag = models.CharField(max_length=30)
    operational = models.BooleanField(default=True)

    def get_http_tcp_listener(self):
        listener = self.http_tcp_listeners.first()
        return {
            "port": listener.port,
            "protocol": listener.protocol,
            "target_group_index": listener.target_group_index,
        }

    def get_target_group(self):
        target_group = self.target_groups.first()
        return {
            "name_prefix": target_group.name_prefix,
            "backend_protocol": target_group.backend_protocol,
            "backend_port": target_group.backend_port,
            "target_type": target_group.target_type,
            "health_check": target_group.health_check.get_json_data(),
        }

    class Meta:
        verbose_name = "Application LB"
        verbose_name_plural = "Application LBs"
