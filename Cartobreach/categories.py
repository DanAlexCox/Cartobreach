from .classes.classes import Category

# construct receiver category class objects
## NOTE - All mentions of "Not available" string changed to "Unknown" before handling
sips = Category("State institutions / political system", [
    "Government / ministries","Legislatives","Civil service / administration (also public schools)","Judicary",
    "Military","Police", "Intelligence agencies","Political parties", "Election infrastructure / related systems",
    "Other (e.g., embassies)"
])
iso = Category("International / supranational organization", ["Not available"])
ci = Category("Critical infrastructure", [
    "Energy","Water","Transportation","Health","Chemicals","Telecommunications","Food","Finance","Defence industry",
    "Space","Waste Water Management","Critical Manufacturing","Other"
])
sg = Category("Social groups", [
    "Ethnic","Religious","Hacktivists","Criminal","Terrorist","Advocacy / activists (e.g. human rights organizations)",
    "Political opposition / dissidents / expats","Other social groups"
])
ct = Category("Corporate Targets (corporate targets only coded if the respective company is not part of the critical infrastructure definition)",[
    "Not available"])
euspg = Category("End user(s) / specially protected groups",["Not available"])
me = Category("Media",["Not available"])
sc = Category("Science",["Not available"])
ed = Category("Education",["Not available"])
ot = Category("Other",["Not available"])
noa = Category("Not available",["Not available"])

# receiver catagory list storage
receiverList = [sips, iso, ci, sg, ct, euspg, me, sc, ed, ot, noa]

