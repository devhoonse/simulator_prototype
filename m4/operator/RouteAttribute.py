
class RouteAttribute(object):

    def __init__(self, from_item_id, to_item_id,
                 from_location_id, to_location_id, from_location_type, to_location_type,
                 item_mix_code, route_conn_code, priority, ratio, move_time):
        self.from_item_id = from_item_id
        self.to_item_id = to_item_id
        self.from_location_id = from_location_id
        self.to_location_id = to_location_id
        self.from_location_type = from_location_type
        self.to_location_type = to_location_type
        self.item_mix_code = item_mix_code
        self.route_conn_code = route_conn_code
        self.priority = priority
        self.ratio = ratio
        self.move_time = move_time
