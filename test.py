settings = "a>d,b>c,c>e,d>e,f>g,g>h,h>m,i>m,m>k,o>d,n1>o,n2>f"
settings = [x.split(">") for x in settings.split(",")]
settings0 = [x[0] for x in settings]
settings1 = [x[1] for x in settings]
independant = [x for x in settings0 if x not in settings1]
dependant = [x for x in settings0 if x not in independant]
entry = [ [y for y in entry if y["heure"] in x]  for x in set([z["heure"] for z in entry])]
countList = []
for subList in entry:
	subDicos = {}
	for item in subList:
		try:
			subDicos[item["code"]] += int(item["nombre"])
		except:
			subDicos[item["code"]] = int(item["nombre"])
	countList.append({"data":subDicos,"heure":item["heure"]})

oredred = "a,b,f,i,n1,o,d,c,e,g,h,i,m,k,n2"
resultDico = {}
results = {}
for zone in oredred:
	for subList in countList:
