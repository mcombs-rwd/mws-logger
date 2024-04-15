# bacnet_table.py
from dataclasses import dataclass, field
from datetime import datetime
import logging
from typing import Any, List

# BACnet controllers contain BACnet devices
# - BACnet devices have an IP address and contain BACnet objects
# - - BACnet objects have values like identifier and an attribute like Temp

logger = logging.getLogger(__name__)

def _parse_obj_name(obj_name):
    """Parse obj_name into category, floor, identifier, and attribute.

    category is zone|water|power.
    If floor doesn't apply, return None.
    Identifier is the full name, less the attribute
    Attribute is SaFl, EaFl, RmTmp, Power, Water, etc.
    
    Lab_1311_EaFl               -> zone, 1, Lab_1131, SaFl|EaFl
    Lab_1311_RmTmp              -> zone, 1, Lab_1131, RmTmp
    VAV-4-301_HVACModeStatus    -> zone, 3, VAV-4-301, HVACModeStatus
    VAV-4-301_CO2               -> zone, 3, VAV-4-301, CO2
    SAV1100A_RmTmp              -> zone, 1, SAV1100A, RmTmp
    CalcNPWTotal_gal            -> water, NA, CalcNPW, NPW
    NPWIrrigationMtr            -> water, NA, NPWIrrigationMtr, NPW
    CalcDomChwTotal             -> water, NA, CalcDomChwTotal, Chw
    El_SubMtr_A1NLH1_WH         -> power, NA, El_SubMtr_A1NLH1, wh
    El_SubMtr_B1ELH2_B3ELH1_WH  -> power, NA, El_SubMtr_B1ELH2_B3ELH1, wh
    Service_Transformer1_Kwh    -> power, NA, kwh
    """
    # TODO: Load these constants from config
    ATTRIBUTES = ['SaFl', 'EaFl', 'RmTmp', 'HVACModeStatus', 'CO2',
            'NPW', 'ChW', 'wh', 'kwh']
    WATER_COUNTERS = ['CalcNPWTotal_gal', 'NPWIrrigationMtr_gal', 
            'CalcDomChwTotal_gal', 'CalcNPWTotal', 'NPWIrrigationMtr', 
            'CalcDomChwTotal']
    POWER_COUNTERS = ['El_SubMtr', 'Service_Transformer']
    (category, floor, identifier, attribute) = (None, None, None, None)
    if not obj_name or obj_name == 'Name':  # catches None, '', and header row
        return(category, floor, identifier, attribute)

    obj_name = obj_name.split('_copy')[0]  # remove _copy suffix
    if obj_name.startswith('Lab'):
        # Lab1151, Lab_1131, Lab-2200
        category = 'zone'
        floor = obj_name[4] if obj_name[3] in ['-', '_'] else obj_name[3]
        i = obj_name.rfind('_')
        (identifier, attribute) = obj_name[:i], obj_name[i+1:]
    elif obj_name.startswith('VAV'):
        # VAV-2-101_AirFl
        (category, floor) = 'zone', obj_name[6]
        i = obj_name.rfind('_')
        (identifier, attribute) = obj_name[:i], obj_name[i+1:]
    elif obj_name.startswith('SAV'):
        # SAV1100A_TotalSaFl
        (category, floor) = 'zone', obj_name[3]
        i = obj_name.rfind('_')
        (identifier, attribute) = obj_name[:i], obj_name[i+1:]
    elif any(obj_name.startswith(prefix) for prefix in WATER_COUNTERS):
        # CalcNPWTotal_gal, NPWIrrigationMtr, CalcDomChwTotal
        (category, floor, identifier) = 'water', -99, obj_name
        attribute = 'ChW' if 'chw' in identifier.lower() else 'NPW'
    elif any(obj_name.startswith(prefix) for prefix in POWER_COUNTERS):
        # El_SubMtr_A1NLH1_WH, Service_Transformer1_Kwh
        i = obj_name.rfind('_')
        (category, floor, identifier) = 'power', -99, obj_name[:i]
        attribute = obj_name[i+1:].lower()

    if category == 'zone':
        # If 'RmTmp 23', drop 2nd word. What's the 2nd word for?
        attribute = attribute.split(' ')[0]
        if attribute.startswith('Total'):
            attribute = attribute[5:]
        if attribute == 'AirFl':
            attribute = 'SaFl'

    if attribute not in ATTRIBUTES:
        for guess in ATTRIBUTES:
            if guess.lower() in obj_name.lower():
                attribute = guess
                break
        else:
            print(f"Attribute not recognized: {obj_name}")
            breakpoint()
            return(None, None, None, None)
    return(category, floor, identifier, attribute)

def request_dict(ip, bac_objects):
    """Returns a formatted BAC0 request_dict.

    Returns:
        {'address': '192.168.1.3',
            'objects': {
                'analogValue:126': ['objectName', 'presentValue'],
                'multistateValue:26': ['objectName', 'presentValue']
                }
        }
    """
    read_objs = {}
    for obj in bac_objects:
        read_objs[f'{obj.obj_type}:{obj.obj_id}'] = obj.obj_props
    return {'address': ip, 'objects': read_objs}

@dataclass
class BacnetObject:
    """Each object represents one attribute on a device.
    
    The object name can be parsed to determine device and attribute.
    Attributes/objects have properties like objectName and presentValue.
    """
    obj_type: str  # analogValue|multistateValue etc
    obj_id: int  # ex: 19
    obj_name: str  # ex: Lab1131_RmTmp or VAV-4-101_HVACModeStatus
    obj_props: List[str] = field(default_factory=lambda: ['objectName', 'presentValue'])
    # these are derived from the obj_name
    category: str = 'zone' # 'zone'  # zone|water|power
    floor: int = None # -99 if no floor
    identifier: str = '' # ex: Lab1131 or VAV-4-101
    attribute: str = '' # ex: RmTmp

    def __post_init__(self):
        (self.category, self.floor, self.identifier, 
                self.attribute) = _parse_obj_name(self.obj_name)

    def request(self):
        """Returns an object to be included in a request_dict"""
        return {f'{self.obj_type}:{self.obj_id}': self.obj_props}

    def __str__(self):
        return (f"{self.obj_type}:{self.obj_id} {self.obj_name} get"
                + f" {self.attribute}")

@dataclass
class BacnetDevice:
    """A device is a collection of objects with the same IP, floor, and identifier
    
    Each device may have several attributes, like RoomTemp or HVACModeStatus
    """
    ip: str  # ip address
    category: str
    floor: int
    identifier: str
    objects: List[BacnetObject]

    def __str__(self):
        attributes = [obj.attribute for obj in self.objects]
        return (f"{self.ip} {self.category=} {self.floor=} {self.identifier=}"
                + f" get {attributes}")

@dataclass
class BacnetController:
    """Read a spreadsheet into a controller and make its devices and objects
    
    A controller may represent many devices, like Lab1131 or VAV101.
    """
    ip: str
    source_objects: List[Any]  # tuples: obj_type, obj_id, obj_name (lab_131_RmTmp)
    desc: str = ''
    # These are derived from the object list
    objects: List[BacnetObject] = field(default_factory=lambda: [])
    devices: List[BacnetDevice] = field(default_factory=lambda: [])

    def make_objects(self):
        self.objects = []
        # for obj_tuple in self.source_objects:
        for (obj_type, obj_id, obj_name) in self.source_objects:
            if obj_type == None or obj_id == None:
                continue  # Skip rows without objects to poll
            mo = BacnetObject(obj_type, int(obj_id), obj_name)
            logger.debug(mo)
            self.objects.append(mo)

    def make_devices(self):
        """Searches object list to group by device"""
        self.devices = []

    def __post_init__(self):
        """Process rows into BACnet objects and devices"""
        self.make_objects()
        self.make_devices()

    def __str__(self):
        return f"{self.ip} ({len(self.objects)} objects): {self.desc}"

    def __len__(self):
        return len(self.objects)

class BacnetTable:
    """Parses BACnet responses to create a table with device rows and attribute columns.
    
    In production:
        bactable = BacnetTable(controller, column_heads, response_dict)
    In test:
        bactable = BacnetTable(controller, column_heads)
        bactable.load_table(load_csv('hvac_data-tall.csv'))
    Now, you can access the data:
        bactable.response  # dict version, if production, for troubleshooting
        bactable.tall_cache  # csv version, cached if load_table or tall_table previously called
        bactable.tall_table()
        bactable.wide_table()
    """

    def __init__(self, controller, headings, response = {}) -> None:
        """Define attributes"""
        self.controller = controller
        self.headings = headings
        self.response = response  # dict version of results
        if response:
            self.tall_cache = self.tall_table()  # csv version of results
        else:
            self.tall_cache = []
        self.prior_counters = {}  # used to calc rate of change
        # TODO: Load COUNTERS and KILO_UNITS from config
        self.COUNTERS = {  # Column name of counter, col name to store delta
            'NPW': 'Gallon rate',
            'ChW': 'Gallon rate',
            'wh': 'Watt rate',
            'kwh': 'Watt rate'
        }
        self.KILO_UNITS = ['kwh']  # Multiply this column by 1000 before storing

    def __str__(self):
        print(f"{self.controller.ip} {len(self.response.keys())} oids,"
                + f" {len(self.tall_cache)} tall rows,"
                + f" {len(self.wide_table())} wide rows.")

    def load_table(self, tall_cache):
        self.tall_cache = tall_cache

    def trusted_obj_name(self, obj_type, obj_id, obj_name=''):
        """The device obj_name isn't trusted, the spreadsheet obj_name is.
        
        Use the obj_id in the response to get the obj_name from the controller.
        """

        # todo: refactor controller.objects to be a dict instead of a list to hash instead of search
        for ref in self.controller.objects:
            if obj_type == ref.obj_type and int(obj_id) == int(ref.obj_id):
                trusted_name = ref.obj_name
                if obj_name != trusted_name:
                    logger.warning(f"Polled name != Trusted name. "
                            f"{obj_name} != {trusted_name}")
                    logger.warning(f"{self.controller.ip} {obj_type}:{obj_id}")
                break
            else:
                trusted_name = obj_name
                logger.debug(f"The polled object wasn't found in the spreadsheet.")
        return trusted_name

    def response_order(self, response):
        """Return correct indexes for name and value properties
        
        Returned order is unknown
        """
        test_index = 0
        if response[test_index][0] == 'objectName':
            (name_index, value_index) = (0, 1)
        else:
            (name_index, value_index) = (1, 0)
        return (name_index, value_index)

    def tall_table(self):
        """Return a list of rows, 1 per unique tuple

        Each row is a different attribute/value pair
        """
        rows = []
        for type_id_key in self.response:  # ('objectName', 'value'), ('objectID', 19)]
            obj_type, obj_id = type_id_key[0], int(type_id_key[1])
            logger.debug(f'{self.controller.ip} {obj_type=}, {obj_id=}')
            (name_index, value_index) = self.response_order(self.response[type_id_key])
            name = self.response[type_id_key][name_index][1]  # ex: 'Lab_1131_RmTmp'
            trusted_name = self.trusted_obj_name(obj_type, obj_id, name)
            if obj_type == 'multiStateValue':
                value = self.response[type_id_key][value_index][1]
            else:
                value = round(float(self.response[type_id_key][value_index][1]),3)  # ex: 71.3
            rows.append([datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M'), 
                    self.controller.ip, obj_type, obj_id, trusted_name, value])
        return rows

    def widen_table(self, tall_rows=[]):
        """Transforms tall key-value table into key-columns.

        Assumes all from same timestamp and same controller.
        Args:
            tall_rows (list)
        Returns:
            list[dict]: Dict per row with values in appropriate columns
        """
        if tall_rows == []:
            tall_rows = self.tall_cache
        wide_rows = []
        wide_row = {}
        for col in self.headings:  # cols with attributes
            wide_row[col] = ''
        for (i, row) in enumerate(tall_rows):
            if row[0] == self.headings[0]:
                continue  # skip this row, it's the heading
            # print(f"narrow_row={row}")
            wide_row['Date'] = row[0]
            wide_row['IP'] = row[1]
            (wide_row['Category'], wide_row['Floor'], wide_row['Name'], 
                    attr) = _parse_obj_name(row[4])
            if attr in wide_row and wide_row[attr] != '':
                logger.warning(f"Duplicate attribute {attr} for row {i}: {row[4]}")
            wide_row[attr] = row[5]
            # print(f"...{wide_row=}")
            # breakpoint()

            # Group attrs from the same floor+name
            # If last row, or floor+name changes, save this wide row
            if i == len(tall_rows)-1:
                wide_rows.append(wide_row)
                break
            (_, next_floor, next_name, _) = _parse_obj_name(tall_rows[i+1][4])
            if wide_row['Floor'] != next_floor or wide_row['Name'] != next_name:
                # print(f"complete {wide_row=}")
                wide_rows.append(wide_row)
                wide_row = {}
                for col in self.headings:  # cols with attributes
                    wide_row[col] = ''
        return wide_rows

    def calc_counter_key(self, row: dict, attr: str):
        """Return a unique key to look up cached values"""
        counter_key = '+'.join([row['IP'], row['Category'], row['Name'], attr])
        return counter_key

    def calc_rates(self, row):
        """Calc changes from row and prior row
        
        ARGS:
            row (dict): Key-value per column

        RETURNS:
            dict: Row with new columns
        """
        # Establish output columns; these are units
        unique_units = set(val for val in self.COUNTERS.values())
        for unit in unique_units:
            row[unit] = 0
        # Find attributes, accumulate into units
        for (attr, unit) in self.COUNTERS.items():
            counter_key = self.calc_counter_key(row, attr)
            if counter_key in self.prior_counters and self.prior_counters[counter_key]:
                delta = round(float(row[attr])) - round(float(self.prior_counters[counter_key]))
                if attr in self.KILO_UNITS:
                    delta = delta * 1000
                row[unit] = delta
            self.prior_counters[counter_key] = row[attr]
        return row

    def wide_table(self, tall_rows=[]):
        """Return 'wider' rows with gallon and Watt hour rate columns."""
        wide_rows = self.widen_table(tall_rows)
        wider_rows = []
        for row_dict in wide_rows:
            row_dict = self.calc_rates(row_dict)
            row_list = [value for value in row_dict.values()]
            wider_rows.append(row_list)
        return wider_rows
