/*
First need to set the nameservers of the domain to the following:
ns1.digitalocean.com
ns2.digitalocean.com
ns3.digitalocean.com
*/

resource "digitalocean_domain" "dxetech" {
    name = "dxetech.org"
    ip_address = "${digitalocean_droplet.server.ipv4_address}"
}

output "domain name" {
    value = "${digitalocean_domain.dxetech.id}"
}
