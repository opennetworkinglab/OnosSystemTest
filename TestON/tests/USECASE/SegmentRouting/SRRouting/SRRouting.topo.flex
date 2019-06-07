<TOPOLOGY>
    <COMPONENT>
        <ONOScell>
            <host>localhost</host>  # ONOS "bench" machine
            <user>sdn</user>
            <password>rocks</password>
            <type>OnosClusterDriver</type>
            <connect_order>1</connect_order>
            <home></home>   # defines where onos home is on the build machine. Defaults to "~/onos/" if empty.
            <COMPONENTS>
                <cluster_name></cluster_name>  # Used as a prefix for cluster components. Defaults to 'ONOS'
                <diff_clihost></diff_clihost> # if it has different host other than localhost for CLI. True or empty. OC# will be used if True.
                <karaf_username>ubuntu</karaf_username>
                <karaf_password>ubuntu</karaf_password>
                <web_user></web_user>
                <web_pass></web_pass>
                <rest_port></rest_port>
                <prompt></prompt>  # TODO: we technically need a few of these, one per component
                <onos_home></onos_home>  # defines where onos home is on the target cell machine. Defaults to entry in "home" if empty.
                <nodes>3</nodes>  # number of nodes in the cluster
            </COMPONENTS>
        </ONOScell>

        <OFDPASwitchLeaf201>
            <host>10.192.21.22</host>
            <user>root</user>
            <password></password>
            <type>OFDPASwitchDriver</type>
            <connect_order>2</connect_order>
            <COMPONENTS>
                <shortName>s004</shortName>
                <dpid>0x201</dpid>
                <confDir>/etc/ofdpa/</confDir>
            </COMPONENTS>
        </OFDPASwitchLeaf201>

        <OFDPASwitchLeaf202>
            <host>10.192.21.23</host>
            <user>root</user>
            <password></password>
            <type>OFDPASwitchDriver</type>
            <connect_order>3</connect_order>
            <COMPONENTS>
                <shortName>s005</shortName>
                <dpid>0x202</dpid>
                <confDir>/etc/ofdpa/</confDir>
            </COMPONENTS>
        </OFDPASwitchLeaf202>

        <OFDPASwitchLeaf203>
            <host>10.192.21.24</host>
            <user>root</user>
            <password></password>
            <type>OFDPASwitchDriver</type>
            <connect_order>4</connect_order>
            <COMPONENTS>
                <shortName>s002</shortName>
                <dpid>0x203</dpid>
                <confDir>/etc/ofdpa/</confDir>
            </COMPONENTS>
        </OFDPASwitchLeaf203>

        <OFDPASwitchLeaf204>
            <host>10.192.21.25</host>
            <user>root</user>
            <password></password>
            <type>OFDPASwitchDriver</type>
            <connect_order>5</connect_order>
            <COMPONENTS>
                <shortName>s003</shortName>
                <dpid>0x204</dpid>
                <confDir>/etc/ofdpa/</confDir>
            </COMPONENTS>
        </OFDPASwitchLeaf204>

        <OFDPASwitchLeaf205>
            <host>10.192.21.29</host>
            <user>root</user>
            <password></password>
            <type>OFDPASwitchDriver</type>
            <connect_order>6</connect_order>
            <COMPONENTS>
                <shortName>s006</shortName>
                <dpid>0x205</dpid>
                <confDir>/etc/ofdpa/</confDir>
            </COMPONENTS>
        </OFDPASwitchLeaf205>

        <OFDPASwitchLeaf206>
            <host>10.192.21.30</host>
            <user>root</user>
            <password></password>
            <type>OFDPASwitchDriver</type>
            <connect_order>7</connect_order>
            <COMPONENTS>
                <shortName>s001</shortName>
                <dpid>0x206</dpid>
                <confDir>/etc/ofdpa/</confDir>
            </COMPONENTS>
        </OFDPASwitchLeaf206>

        <OFDPASwitchLeaf225>
            <host>10.192.21.21</host>
            <user>root</user>
            <password></password>
            <type>OFDPASwitchDriver</type>
            <connect_order>8</connect_order>
            <COMPONENTS>
                <shortName>s101</shortName>
                <dpid>0x225</dpid>
                <confDir>/etc/ofdpa/</confDir>
            </COMPONENTS>
        </OFDPASwitchLeaf225>

        <OFDPASwitchLeaf226>
            <host>10.192.21.26</host>
            <user>root</user>
            <password></password>
            <type>OFDPASwitchDriver</type>
            <connect_order>9</connect_order>
            <COMPONENTS>
                <shortName>s102</shortName>
                <dpid>0x226</dpid>
                <confDir>/etc/ofdpa/</confDir>
            </COMPONENTS>
        </OFDPASwitchLeaf226>

        <OFDPASwitchLeaf227>
            <host>10.192.21.28</host>
            <user>root</user>
            <password></password>
            <type>OFDPASwitchDriver</type>
            <connect_order>10</connect_order>
            <COMPONENTS>
                <shortName>s103</shortName>
                <dpid>0x227</dpid>
                <confDir>/etc/ofdpa/</confDir>
            </COMPONENTS>
        </OFDPASwitchLeaf227>

        <OFDPASwitchLeaf228>
            <host>10.192.21.31</host>
            <user>root</user>
            <password></password>
            <type>OFDPASwitchDriver</type>
            <connect_order>11</connect_order>
            <COMPONENTS>
                <shortName>s104</shortName>
                <dpid>0x228</dpid>
                <confDir>/etc/ofdpa/</confDir>
            </COMPONENTS>
        </OFDPASwitchLeaf228>

        <Host4v4>
            <host>10.192.21.61</host>
            <user>vyatta</user>
            <password>vyatta</password>
            <type>HostDriver</type>
            <connect_order>13</connect_order>
            <COMPONENTS>
                <ip>10.0.202.7</ip>
                <ip6></ip6>
                <shortName>h4v4</shortName>
                <ifaceName>bond0</ifaceName>
                <inband>True</inband>
                <username>ubuntu</username>
                <password>ubuntu</password>
            </COMPONENTS>
        </Host4v4>


        <Host5v4>
            <host>10.192.21.61</host>
            <user>vyatta</user>
            <password>vyatta</password>
            <type>HostDriver</type>
            <connect_order>14</connect_order>
            <COMPONENTS>
                <ip>10.0.202.8</ip>
                <ip6></ip6>
                <shortName>h5v4</shortName>
                <ifaceName>bond0</ifaceName>
                <inband>True</inband>
                <username>ubuntu</username>
                <password>ubuntu</password>
            </COMPONENTS>
        </Host5v4>

        <Host9v4>
            <host>10.192.21.61</host>
            <user>vyatta</user>
            <password>vyatta</password>
            <type>HostDriver</type>
            <connect_order>15</connect_order>
            <COMPONENTS>
                <ip>10.0.204.7</ip>
                <ip6></ip6>
                <shortName>h9v4</shortName>
                <ifaceName>bond0</ifaceName>
                <inband>True</inband>
                <username>ubuntu</username>
                <password>ubuntu</password>
            </COMPONENTS>
        </Host9v4>

        <Host10v4>
            <host>10.192.21.61</host>
            <user>vyatta</user>
            <password>vyatta</password>
            <type>HostDriver</type>
            <connect_order>16</connect_order>
            <COMPONENTS>
                <ip>10.0.204.8</ip>
                <ip6></ip6>
                <shortName>h10v4</shortName>
                <ifaceName>bond0</ifaceName>
                <inband>True</inband>
                <username>ubuntu</username>
                <password>ubuntu</password>
            </COMPONENTS>
        </Host10v4>

        <NetworkBench>
            <host>localhost</host>
            <user>sdn</user>
            <password>rocks</password>
            <type>NetworkDriver</type>
            <connect_order>20</connect_order>
            <COMPONENTS>
            </COMPONENTS>
        </NetworkBench>
    </COMPONENT>
</TOPOLOGY>
