import BAC0


def main(ip_with_mask, bbmd_ip, bbmd_ttl=900, test_mode=False):
    print("Register to BBMD.")
    if not test_mode:
        bacnet = BAC0.lite(ip=my_ip, bbmdAddress=bbmd_ip, 
            bbmdTTL=bbmd_ttl)

    print("\nTest Read analogValue")
    as0_ip = '10.117.75.12'
    as0_obj_type = 'analogValue'
    as0_obj_id = '19'
    as0_obj_attr = 'presentValue'
    request_0 = f'{as0_ip} {as0_obj_type} {as0_obj_id} {as0_obj_attr}'
    print(f'request_0: {request_0}\n')
    if not test_mode:
        try:
            as0 = bacnet.read(request_0)
        except KeyboardInterrupt:
            bacnet.disconnect()
        print(as0)

    print("\nTest Read multistateValue")
    as1_ip = '10.117.75.12'
    as1_obj_type = 'multiStateValue'
    as1_obj_id = '4'
    as1_obj_attr = 'presentValue'
    request_1 = f'{as1_ip} {as1_obj_type} {as1_obj_id} {as1_obj_attr}'
    print(f'request_1: {request_1}\n')
    if not test_mode:
        try:
            as1 = bacnet.read(request_1)
        except KeyboardInterrupt:
            bacnet.disconnect()
        print(as1)

    print("\nTest Multiread")
    # attrs not implemented on AS will not be returned. 
    # Verified implemented: objectName, presentValue
    as0_obj_attrs = ['objectName', 'presentValue', 'units', 
        'statusFlags', 'eventState', 'reliability', 'outOfService']
    as1_obj_attrs = ['objectName', 'presentValue',
        'statusFlags', 'eventState', 'reliability', 'outOfService']
    request_n = {
        'address': as0_ip,
        'objects': {
            f'{as0_obj_type}:{as0_obj_id}': as0_obj_attrs,
            f'{as1_obj_type}:{as1_obj_id}': as1_obj_attrs,
        }
    }
    print(f'request_n: {request_n}\n')
    if not test_mode:
        try:
            asn = bacnet.readMultiple(as0_ip, request_dict=request_n)
        except KeyboardInterrupt:
            bacnet.disconnect()
        print(asn)

    print("\nGet object names")
    as2_ip = '10.117.75.17'
    as2_obj_type = 'analogValue'
    as2_obj_attrs = ['objectName']
    objs = {}
    for as2_obj_id in range(1,20):
        objs.update({f'{as2_obj_type}:{as2_obj_id}': as2_obj_attrs})
    request_2 = {
        'address': as2_ip,
        'objects': objs
    }
    print(f'request_2: {request_2}\n')
    if not test_mode:
        try:
            response = bacnet.readMultiple(as2_ip, request_dict=request_2)
        except KeyboardInterrupt:
            bacnet.disconnect()
        print(response)
        for tuple_key in response:
            (obj_type, obj_id) = tuple_key
            print(f'{obj_type=}, {obj_id=}')
            for attr in response[tuple_key]:
                print(f'... {attr[0]}={attr[1]}')


if __name__ == '__main__':
    # Find my_ip address(es) with `ipconfig | findstr Address`
    # my_ip = '192.168.1.2'
    my_ip = '10.76.148.128'
    mask = '23' # 23-bit mask

    # if BACnet/IP devices are on a different subnet, we must go through the BBMD
    bbmd_ip = '10.117.75.17:47808'

    test_mode = False  # True if not actual bacnet

    main(f'{my_ip}/{mask}', bbmd_ip, 900, test_mode)
    