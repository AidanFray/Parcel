import time
from scapy.layers.inet import IP
from Utils.Terminal import Terminal

class Effect:
    """Class that generally defines what an effect should contain

    Params
        accept_packets  - Defines if packets should be accepted (Used when stringing effects together)
        show_output     - Says if the effect should show any output
        graphing        - Toggles if the effect should collect data for a graph
        gather_stats    - Switches on or off the data collection for packets like tcp
        graph_type_num  - Defines the different graph to be generated. List in the the usage menu
    """

    def __init__(self,
                 accept_packets=True,
                 show_output=True,
                 graphing=False,
                 gather_stats=True,
                 graph_type_num=0,
                 slimline=False):

        self.accept_packet = accept_packets
        self.show_output = show_output
        self.graphing = graphing
        self.gather_stats = gather_stats
        self.graph_type_num = graph_type_num
        self.slimline = slimline

        # --- Universal stats --- #
        # Every effect has a starting time
        self.start_time = time.time()
        self.total_packets = 0  # Number of total packets processed

        self.previous_packets = []

    def effect(self, packet):
        """The first method run for all effects - Here custom code will be added
        to collate information"""

        try:

            if True:
                # TCP tracking
                if self.gather_stats:
                    self.track_TCP_stats(packet)


            self.total_packets += 1
            self.print_stats()
            self.custom_effect(packet)
        except Exception as e:
            print('Error in effect(): ', e)

    def custom_effect(self, packet):
        """Each effect will need it's own custom effect"""
        raise Exception('NotImplemented: Please add \'custom_effect()\' to your class')

    def print_stats(self):
        """[Blueprint] - Should print the custom stats for each method.
        Note Print_stats should call 'self.print()' to show any output """
        pass

    def get_elapsed_time(self):
        """Used to find out how long ago the effect started"""
        return time.time() - self.start_time

    def print(self, message, end='\n', force=False):
        """General print method"""
        if self.show_output or force:
            print(message, end=end, flush=True)

    @staticmethod
    def print_clear():
        """Method that is used to clear the output line, this is
        so no fragments are left after a stat print refresh"""
        Terminal.clear_line()

    def accept(self, packet):
        """Center point for accepting packets"""
        if self.accept_packet:
            packet.accept()

    def stop(self):
        """[Blueprint] - Called to stop the object"""
        pass

    def check_packet_type(self, packet, target_packet):
        """Checks if the packet is of a certain type"""

        # Grabs the first section of the Packet
        packet_string = str(packet)
        split = packet_string.split(' ')

        # Checks for the target packet type
        if target_packet == split[0]:
            return True
        else:
            return False

    def track_TCP_stats(self, packet):
        """Method that tracks characteristics of the TCP packets """

        try:
            if self.check_packet_type(packet, 'TCP'):
                self.log_packets(packet)

        except AttributeError:
            pass
        except Exception as e:
            print('Error:', e)

    def log_packets(self, packet):
        """This method checks for any TCP packets that
        have been retransmitted"""

        pkt = IP(packet.get_payload())

        # IPs
        dst = pkt.dst
        src = pkt.src

        # Ports
        dst_port = pkt.dport
        src_port = pkt.sport

        # Sequence number
        seq_num = pkt.seq

        # ACK Number
        ack_num = pkt.ack

        # Window Size
        window_size = pkt.window

        # Creates the session object
        tcp_packet = TcpPacket(src, src_port, dst, dst_port, seq_num, ack_num, len(pkt), window_size, packet)
        self.previous_packets.append(tcp_packet)


class TcpPacket:
    """Used to hold values about packets in a session"""

    def __init__(self, src, src_port, dst, dst_port, seq_num, ack_num, size, window_size, packet):
        self.src = src
        self.src_port = src_port

        self.dst = dst
        self.dst_port = dst_port

        self.ack_num = ack_num
        self.seq_num = seq_num
        self.size = size
        self.window_size = window_size
        self.packet_flags = self.get_flags(packet)

    def __str__(self):
        """String returned when print() is called on the object"""

        return "SEQ: {0:<11} ACK: {1:<11} SIZE: {2:<4} FLAGS: {3:}".\
            format(self.seq_num, self.ack_num, self.size, self.packet_flags)

    def compare(self, t):
        """Used to compare one packet to another to detect a match"""

        if (t.ack_num == self.ack_num) and (t.seq_num == self.seq_num) and (t.size == self.size):
            return self.same_flags(t.packet_flags)
        else:
            return False

    def has_flag(self, name):
        """Checks for the presense of a single flag"""

        if name in self.packet_flags:
            return True
        else:
            return False

    def same_flags(self, other_flags):
        """Compares the two packets flags"""

        return set(self.packet_flags) == set(other_flags)

    def just_has_flag(self, name):
        """Checks if the packet has just a single flag"""

        if len(self.packet_flags) > 1:
            return False
        elif self.packet_flags[0] == name:
            return True
        else:
            return False

    @staticmethod
    def get_flags(packet):
        """Static method that is used to get the flags from the raw TCP packet"""

        FIN = 0x01
        SYN = 0x02
        RST = 0x04
        PSH = 0x08
        ACK = 0x10
        URG = 0x20
        ECE = 0x40
        CWR = 0x80

        pkt = IP(packet.get_payload())
        flags = pkt.flags

        # Saves the flags
        active_flags = ['***'] * 8
        if flags & FIN:
            active_flags[0] = 'FIN'
        if flags & SYN:
            active_flags[1] = 'SYN'
        if flags & RST:
            active_flags[2] = 'RST'
        if flags & PSH:
            active_flags[3] = 'PSH'
        if flags & ACK:
            active_flags[4] = 'ACK'
        if flags & URG:
            active_flags[5] = 'URG'
        if flags & ECE:
            active_flags[6] = 'ECE'
        if flags & CWR:
            active_flags[7] = 'CWR'

        # Filters out blanks
        active_flags = [i for i in active_flags if i != '***']

        return active_flags

