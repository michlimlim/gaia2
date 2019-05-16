#!/usr/bin/python
"""
This is the most simple example to showcase Containernet.
"""
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
setLogLevel('info')

net = Mininet()
info('*** Adding controller\n')
net.addController('c0')
info('*** Adding docker containers\n')
d1a = net.addHost('d1a', ip='10.0.0.1')
d1b = net.addHost('d1b', ip='10.0.0.2')
d2a = net.addHost('d2a', ip='10.0.1.1')
d2b = net.addHost('d2b', ip='10.0.1.2')
d3a = net.addHost('d3a', ip='10.0.2.1')
d3b = net.addHost('d3b', ip='10.0.2.2')
info('*** Adding switches\n')
s1 = net.addSwitch('s1')
s2 = net.addSwitch('s2')
s3 = net.addSwitch('s3')
info('*** Creating links\n')
net.addLink(d1a, s1)
net.addLink(d1b, s1)
net.addLink(d2a, s2)
net.addLink(d2b, s2)
net.addLink(d3a, s3)
net.addLink(d3b, s3)
net.addLink(s1, s2, cls=TCLink, delay='100ms', bw=1)
net.addLink(s2, s3, cls=TCLink, delay='100ms', bw=1)
info('*** Starting network\n')
net.start()
info('*** Testing connectivity\n')
net.ping([d1a, d3b])
info('*** Running CLI\n')
CLI(net)
info('*** /Stopping network')
net.stop()
