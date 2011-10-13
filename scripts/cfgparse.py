def parse_config(filename, config=dict()):
	for (nr, row) in enumerate(open(filename)):
		row=row.strip()
		if not row or row[0] == "#" or row[0:2] == "//":
			continue
		try:
			(key, value)=row.split("=",1)
		except ValueError:
			print "invalid config syntax on line %i: %s, ignoring"%(nr+1,row)
			continue
		key=key.strip()
		value=value.strip(""" "';""")
		if "," in value:
			config[key]=[element.strip() for element in value.split(",")]
		else:
			config[key]=value
	return config

