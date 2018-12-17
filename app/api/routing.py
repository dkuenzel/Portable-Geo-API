from flask import jsonify

# Input format for point to point routing: longitude
@bp.route('/p2p/<float:origin_lon>/<float:origin_lat>/<float:destination_lon>/<float:destination_lat>', methods=['GET'])
def get_user(origin_lon, origin_lat, destination_lon, destination_lat):
    return jsonify(User.query.get_or_404(id).to_dict())
