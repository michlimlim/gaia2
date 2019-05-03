#!/usr/bin/python
"""
This is the most simple example to showcase Containernet.
"""
from mininet.net import Containernet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
setLogLevel('info')

net = Containernet(controller=Controller)
info('*** Adding controller\n')
net.addController('c0')
info('*** Adding docker containers\n')
da1 = net.addDocker('da1', ip='10.0.0.251', dimage="ubuntu:trusty")
da2 = net.addDocker('da2', ip='10.0.0.252', dimage="ubuntu:trusty")
db1 = net.addDocker('db1', ip='10.0.0.253', dimage="ubuntu:trusty")
db2 = net.addDocker('db2', ip='10.0.0.254', dimage="ubuntu:trusty")
info('*** Adding switches\n')
s1 = net.addSwitch('s1')
s2 = net.addSwitch('s2')
info('*** Creating links\n')
net.addLink(da1, s1)
net.addLink(da2, s1)
net.addLink(db1, s2)
net.addLink(db2, s2)
net.addLink(s1, s2, cls=TCLink, delay='100ms', bw=1)
info('*** Starting network\n')
net.start()
info('*** Testing connectivity\n')
net.ping([da1, db1])
info('*** Running CLI\n')
CLI(net)
info('*** /Stopping network')
net.stop()
