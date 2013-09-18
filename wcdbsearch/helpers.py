def truncate_fields(obj):
	for key, val in obj.iteritems():
		if isinstance(val, dict):
			obj[key] = truncate_fields(val)
		elif isinstance(val, (list, tuple, )):
			idx = -1
			for subval in val:
				idx += 1
				obj[key][idx] = truncate_fields(subval)
		elif isinstance(val, (str, unicode)) and key not in ['content', 'text']:
			obj[key] = val[:225]
	return obj