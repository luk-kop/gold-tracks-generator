import random
import string
from datetime import datetime, timedelta

from ctc_data import CtcFlag, CtcType, CtcCategory


class IdGenerator:
    """
    Simple ID generator.
    """
    def __init__(self, start=1):
        self.id = start

    def __iter__(self):
        return self

    def __next__(self):
        current_id = self.id
        self.id += 1
        return current_id


class GoldCtc:
    """
    A class representing CTC OTG set.
    """
    name_id = IdGenerator()

    def __init__(self, name='TEST'):
        self.track_number = f'T{random.randrange(100, 99_999):05d}'
        self.class_name = f'UNEQUATED-{name}{next(GoldCtc.name_id)}'     # to change
        self.trademark = ''
        self.type = CtcType.get_random_name()
        self.category = CtcCategory.get_random_name()
        self.pennant_number = f'{random.choice(["D", "A", "M", "F", "P", ""])}{random.randrange(10, 9_999)}'
        self.flag = CtcFlag.get_random_name()
        self.sconum = ''
        self.selective_id = ''
        self.alert_code = random.choice(['', 'TGT', 'SUS', 'HIT', 'NSP'])
        while True:
            force_code = random.randrange(1, 58)
            # exclude 33-37
            if force_code not in list(range(33, 38)):
                self.force_code = f'{force_code:02d}'
                break
        self.system_track_no = ''
        self.average_speed = f'{str(random.randint(0, 50))}'
        self.average_time_on_leg = ''
        self.discrete_id = ''
        self.uid = f'{random.choice(["ORP", "FGS", "LLL", "COM"])}{random.randrange(1_000_000, 999_999_999):09d}'
        self.ircs = ''.join(random.sample(string.ascii_uppercase, 4))
        self.suspicion_code = random.choice([f'{random.randrange(1, 11):02d}', ''])
        self.emitter_voice_cs = ''

    def get_all_attr(self):
        return [value for value in self.__dict__.values()]

    def __str__(self):
        separator = '/'
        return f'CTC/{separator.join(self.get_all_attr())}'.rstrip(separator)


class GoldXpos:
    """
    A class representing XPOS OTG set.
    """
    def __init__(self, position=None):
        self._date_time_group = self.date_time_group
        self.month_year = f'{datetime.utcnow().strftime("%b").upper()}{datetime.utcnow().strftime("%y")}'
        self.position = position
        self.sensor_code = random.choice(['', 'RADAR', 'VISUAL', 'UNK', 'PHOTO', 'SRN25', 'IFF', 'IR'])
        self.bearing_of_major_axis = ''
        self.length_of_semi_major_axis = ''
        self.length_of_semi_minor_axis = ''
        self.course = f'{random.randint(0, 359):03d}.{random.randint(0, 9)}T'
        self.speed = f'{random.randint(0, 50)}KTS'
        self.altitude = ''
        self.depth = ''
        self.rdf_rf = ''
        self.source_code = random.choice(['', 'EST', 'NTDS', 'UNK'])
        self.seq_contact_id = ''
        self.photos = ''
        self.total_no_of_contacts = ''

    @property
    def date_time_group(self):
        # TODO: different timestamp for each track
        # Substract 30 min from utcnow
        date = f'{(datetime.utcnow().replace(second=0) - timedelta(hours=0, minutes=30)).strftime("%d%H%M%S")}'
        return f'{date}Z{self._check_sum(date)}'

    @property
    def position(self):
        """
        Returns position in format - LL:552521N0-0163311E5
        """
        # TODO: If more than one track and not random position - units in some radius from position
        # TODO: Validate position with regex on input
        return self._position

    @position.setter
    def position(self, value):
        if not value:
            latitude = f'{random.randrange(0, 90):02d}{random.randrange(0, 60):02d}{random.randrange(0, 60):02d}'
            longitude = f'{random.randrange(0, 180):03d}{random.randrange(0, 60):02d}{random.randrange(0, 60):02d}'
            latitude_dir = random.choice(['N', 'S'])
            longitude_dir = random.choice(['E', 'W'])
            position = f'LL:{latitude}{latitude_dir}{self._check_sum(latitude)}-' \
                       f'{longitude}{longitude_dir}{self._check_sum(longitude)}'
            self._position = position
        # TODO: custom position

    @staticmethod
    def _check_sum(value):
        """
        Calculate checksum
        """
        return sum([int(num) for num in value]) % 10

    def get_all_attr(self):
        return [value for value in self.__dict__.values()]

    def __str__(self):
        separator = '/'
        return f'XPOS/{separator.join(self.get_all_attr())}'.rstrip(separator)


class GoldTrack:
    """
    A class representing a single track
    """
    def __init__(self):
        self.ctc = GoldCtc()
        self.xpos = GoldXpos()

    def __str__(self):
        return f'{self.ctc}\n{self.xpos}\n'


class GoldMessage:
    """
    A class representing GOLD msg to send.
    """
    msg_id = 0

    def __init__(self, track_count=1, msg_originator='GOLDTX'):
        self.gold_tracks_count = track_count
        self.msg_originator = msg_originator    # TODO: 1-14 chars validation
        GoldMessage.msg_id_increase()

    @property
    def gold_tracks(self):
        return [GoldTrack() for _ in range(self.gold_tracks_count)]

    @property
    def msg_header(self):
        date_hour = datetime.utcnow().strftime("%d%H%M")
        month = datetime.utcnow().strftime("%b").upper()
        year = datetime.utcnow().strftime('%y')
        full_date_header = f'{date_hour}Z {month} {year}'
        return f'ZNR UUUUU\nP {full_date_header}\nFM {self.msg_originator}\nTO ALL\nBT\nUNCLAS\n' \
               f'MSGID/{self.msg_originator}/XCTC/{self.get_msg_id()}/{month}\n'

    @property
    def msg_trailer(self):
        return f'ENDAT\nBT\n\n\n\n\n\n\n\nNNNN'

    def __str__(self):
        return f'{self.msg_header}{"".join([str(track) for track in self.gold_tracks])}{self.msg_trailer}'

    @classmethod
    def msg_id_increase(cls):
        cls.msg_id += 1

    @classmethod
    def get_msg_id(cls):
        return f'{cls.msg_id:04d}'

    def gold_send_tcp(self):
        pass

    def gold_send_udp(self):
        pass

    def __len__(self):
        """
        Returns number of GOLD tracks in message.
        """
        return len(self.gold_tracks)

 
if __name__ == "__main__":
    msg = GoldMessage(track_count=10)
    print(msg)
