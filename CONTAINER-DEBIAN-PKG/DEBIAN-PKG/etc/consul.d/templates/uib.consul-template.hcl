# When a change in the Consul catalog is detected,
# this service will restart Django/Apache to avoid "caching" of its config file.

consul {
  address = "localhost:8500"

  retry {
    enabled = true
    attempts = 0
    backoff = "250ms"
  }
}
template {
  source = "/etc/consul.d/uib.tmpl"
  destination = "/var/run/api.address"
  command = "/usr/sbin/apachectl restart"
  wait {
    min = "1s"
    max = "3s"
  }
}
log_level = "info"
syslog {
  enabled = true
}
